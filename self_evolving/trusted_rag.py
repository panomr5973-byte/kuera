#!/usr/bin/env python3
"""
Trusted RAG (Retrieval-Augmented Generation) dengan Source Ranking
KUERA - AI yang hanya jawab dari sumber terpercaya
"""

import os
import json
import sqlite3
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta

try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    print("[WARNING] sentence-transformers not available. Using fallback.")

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    print("[WARNING] faiss not available. Using keyword fallback.")

try:
    from rank_bm25 import BM25Okapi
    BM25_AVAILABLE = True
except ImportError:
    BM25_AVAILABLE = False


class TrustedSourceScorer:
    """
    Score sumber berdasarkan kredibilitas
    Wikipedia > ArXiv > Papers > Feedback > Blogs
    """
    
    # Authority scores untuk berbagai jenis sumber
    AUTHORITY_SCORES = {
        'wikipedia': 0.95,
        'wiki': 0.95,
        'arxiv': 0.92,
        'paper': 0.90,
        'research': 0.88,
        'textbook': 0.87,
        'gov': 0.85,  # Government sites
        'edu': 0.84,  # Educational institutions
        'feedback': 0.82,  # High-quality user feedback
        'news_reputable': 0.80,  # Reputable news
        'blog_expert': 0.70,  # Expert blogs
        'forum': 0.60,  # Forums
        'blog': 0.50,  # Regular blogs
        'unknown': 0.40,
    }
    
    @classmethod
    def score_authority(cls, filename: str, source_type: str = None) -> float:
        """Score berdasarkan nama file atau tipe sumber"""
        if source_type and source_type in cls.AUTHORITY_SCORES:
            return cls.AUTHORITY_SCORES[source_type]
        
        filename_lower = filename.lower()
        for key, score in cls.AUTHORITY_SCORES.items():
            if key in filename_lower:
                return score
        
        return cls.AUTHORITY_SCORES['unknown']
    
    @classmethod
    def score_freshness(cls, date_str: str) -> float:
        """Score berdasarkan kefreshan (0-1)"""
        try:
            # Parse date dari berbagai format
            date = cls._parse_date(date_str)
            if not date:
                return 0.5  # Unknown date = middle score
            
            age_days = (datetime.now() - date).days
            
            # Exponential decay: semakin baru semakin tinggi
            # 30 hari = 0.9, 1 tahun = 0.5, 5 tahun = 0.1
            import math
            freshness = math.exp(-age_days / 365)
            
            return min(1.0, max(0.1, freshness))
        except:
            return 0.5
    
    @classmethod
    def _parse_date(cls, date_str: str) -> Optional[datetime]:
        """Parse date dari berbagai format"""
        formats = [
            '%Y-%m-%d',
            '%Y-%m',
            '%Y',
            '%d/%m/%Y',
            '%m/%d/%Y',
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except:
                continue
        
        # Try extract year from string
        year_match = re.search(r'20\d{2}', date_str)
        if year_match:
            try:
                return datetime(int(year_match.group()), 1, 1)
            except:
                pass
        
        return None
    
    @classmethod
    def score_popularity(cls, citation_count: int = 0, view_count: int = 0) -> float:
        """Score berdasarkan popularitas/citations"""
        # Normalize citation count
        if citation_count > 1000:
            return 1.0
        elif citation_count > 100:
            return 0.8
        elif citation_count > 10:
            return 0.6
        elif citation_count > 0:
            return 0.4
        
        # View count sebagai fallback
        if view_count > 10000:
            return 0.7
        elif view_count > 1000:
            return 0.5
        
        return 0.3
    
    @classmethod
    def score_verification(cls, sources: List[Dict]) -> float:
        """Cross-check consensus antar sumber"""
        if len(sources) < 2:
            return 0.5  # Cannot verify
        
        # Check agreement between top sources
        agreements = 0
        for i, s1 in enumerate(sources[:3]):
            for s2 in sources[i+1:4]:
                # Simple keyword overlap check
                words1 = set(s1['content'].lower().split())
                words2 = set(s2['content'].lower().split())
                overlap = len(words1 & words2) / max(len(words1), 1)
                if overlap > 0.3:  # 30% overlap
                    agreements += 1
        
        # Score berdasarkan jumlah agreement
        max_possible = min(3, len(sources)) * (min(3, len(sources)) - 1) / 2
        if max_possible == 0:
            return 0.5
        
        return min(1.0, 0.3 + (agreements / max_possible) * 0.7)


class TrustedRAG:
    """
    RAG dengan Trusted Source Ranking
    Hanya gunakan sumber kredibel untuk jawaban
    """
    
    def __init__(self, knowledge_dir: str = "data/knowledge/", 
                 db_path: str = "data/kuera_database.db",
                 use_embeddings: bool = True):
        self.knowledge_dir = Path(knowledge_dir)
        self.db_path = db_path
        self.use_embeddings = use_embeddings and FAISS_AVAILABLE
        
        # Initialize embedding model
        self.embedding_model = None
        if self.use_embeddings:
            try:
                # Lightweight model
                self.embedding_model = SentenceTransformer('paraphrase-MiniLM-L3-v2')
                print("[TrustedRAG] Embedding model loaded.")
            except Exception as e:
                print(f"[TrustedRAG] Failed to load embeddings: {e}")
                self.use_embeddings = False
        
        # Build knowledge base
        self.docs = []
        self.metadata = []
        self.index = None
        self.bm25 = None
        
        self._build_index()
    
    def _build_index(self):
        """Build searchable index dari knowledge base"""
        
        # 1. Load dari file knowledge
        if self.knowledge_dir.exists():
            for file_path in self.knowledge_dir.glob("*.txt"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Extract metadata dari filename atau content
                    meta = self._extract_metadata(file_path.name, content)
                    
                    self.docs.append(content)
                    self.metadata.append(meta)
                except Exception as e:
                    print(f"[Error] Loading {file_path}: {e}")
        
        # 2. Load dari database feedback berkualitas tinggi
        self._load_quality_feedback()
        
        if not self.docs:
            print("[TrustedRAG] No documents found. Using empty index.")
            return
        
        # 3. Build FAISS index (semantic search)
        if self.use_embeddings and self.embedding_model:
            try:
                embeddings = self.embedding_model.encode(self.docs)
                d = embeddings.shape[1]
                
                # Normalize untuk cosine similarity
                faiss.normalize_L2(embeddings)
                
                # Create index
                self.index = faiss.IndexFlatIP(d)  # Inner product = cosine for normalized
                self.index.add(embeddings.astype('float32'))
                
                print(f"[TrustedRAG] FAISS index built: {len(self.docs)} docs")
            except Exception as e:
                print(f"[TrustedRAG] FAISS failed: {e}")
                self.use_embeddings = False
        
        # 4. Build BM25 index (keyword search)
        if BM25_AVAILABLE and self.docs:
            try:
                tokenized_docs = [doc.lower().split() for doc in self.docs]
                self.bm25 = BM25Okapi(tokenized_docs)
                print("[TrustedRAG] BM25 index built.")
            except Exception as e:
                print(f"[TrustedRAG] BM25 failed: {e}")
                self.bm25 = None
    
    def _extract_metadata(self, filename: str, content: str) -> Dict:
        """Extract metadata dari filename dan content"""
        
        # Parse date dari content
        date_match = re.search(r'\b(20\d{2})[-/](\d{1,2})', content)
        if date_match:
            date_str = f"{date_match.group(1)}-{date_match.group(2)}"
        else:
            # Use file modification time
            date_str = datetime.now().strftime('%Y-%m')
        
        # Detect source type
        source_type = 'unknown'
        fname_lower = filename.lower()
        for type_key in ['wikipedia', 'wiki', 'arxiv', 'paper', 'feedback']:
            if type_key in fname_lower:
                source_type = type_key
                break
        
        return {
            'source': filename,
            'source_type': source_type,
            'date': date_str,
            'authority_score': TrustedSourceScorer.score_authority(filename, source_type),
            'freshness_score': TrustedSourceScorer.score_freshness(date_str),
            'content_length': len(content),
        }
    
    def _load_quality_feedback(self):
        """Load high-quality feedback dari database sebagai knowledge"""
        try:
            if not os.path.exists(self.db_path):
                return
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get high-confidence interactions dengan positive feedback
            cursor.execute("""
                SELECT user_message, kuera_response, confidence, user_feedback
                FROM interactions
                WHERE (user_feedback = 1 OR confidence > 0.85)
                  AND LENGTH(kuera_response) > 50
                ORDER BY created_at DESC
                LIMIT 100
            """)
            
            rows = cursor.fetchall()
            conn.close()
            
            for row in rows:
                user_msg, response, conf, feedback = row
                # Format sebagai Q&A
                content = f"Q: {user_msg}\nA: {response}"
                
                # Score berdasarkan feedback dan confidence
                quality_score = 0.82 if feedback == 1 else conf * 0.8
                
                self.docs.append(content)
                self.metadata.append({
                    'source': f"feedback_{len(self.docs)}",
                    'source_type': 'feedback',
                    'date': datetime.now().strftime('%Y-%m'),
                    'authority_score': quality_score,
                    'freshness_score': 0.9,  # Recent feedback
                    'confidence': conf,
                })
            
            print(f"[TrustedRAG] Loaded {len(rows)} quality feedback entries.")
            
        except Exception as e:
            print(f"[TrustedRAG] Feedback load error: {e}")
    
    def search(self, query: str, top_k: int = 5, 
               min_score_threshold: float = 0.5) -> List[Dict]:
        """
        Search dengan trusted source ranking
        
        Returns: List of results dengan combined score
        """
        if not self.docs:
            return []
        
        results = []
        
        # 1. Semantic search dengan FAISS
        if self.use_embeddings and self.index:
            try:
                q_embed = self.embedding_model.encode([query])
                faiss.normalize_L2(q_embed)
                
                D, I = self.index.search(q_embed.astype('float32'), min(top_k*2, len(self.docs)))
                
                for i, doc_idx in enumerate(I[0]):
                    if doc_idx == -1 or doc_idx >= len(self.docs):
                        continue
                    
                    semantic_score = float(D[0][i])
                    
                    results.append({
                        'doc_idx': int(doc_idx),
                        'semantic_score': semantic_score,
                    })
            except Exception as e:
                print(f"[Search] FAISS error: {e}")
        
        # 2. Keyword search dengan BM25
        if self.bm25:
            try:
                bm25_scores = self.bm25.get_scores(query.lower().split())
                
                # Add BM25 scores
                for existing in results:
                    idx = existing['doc_idx']
                    if idx < len(bm25_scores):
                        existing['bm25_score'] = float(bm25_scores[idx])
                    else:
                        existing['bm25_score'] = 0.0
                
                # Add top BM25 results yang belum ada
                top_bm25_indices = np.argsort(bm25_scores)[-top_k:][::-1]
                for idx in top_bm25_indices:
                    if not any(r['doc_idx'] == idx for r in results):
                        results.append({
                            'doc_idx': int(idx),
                            'semantic_score': 0.0,
                            'bm25_score': float(bm25_scores[idx]),
                        })
            except Exception as e:
                print(f"[Search] BM25 error: {e}")
        
        # 3. Calculate combined scores
        scored_results = []
        for r in results:
            idx = r['doc_idx']
            meta = self.metadata[idx]
            
            # Combined score formula
            semantic = r.get('semantic_score', 0) * 0.35
            bm25 = r.get('bm25_score', 0) * 0.25
            authority = meta['authority_score'] * 0.25
            freshness = meta['freshness_score'] * 0.15
            
            total_score = semantic + bm25 + authority + freshness
            
            if total_score >= min_score_threshold:
                scored_results.append({
                    'content': self.docs[idx][:800] + ('...' if len(self.docs[idx]) > 800 else ''),
                    'score': round(total_score, 3),
                    'source': meta['source'],
                    'source_type': meta['source_type'],
                    'authority': meta['authority_score'],
                    'freshness': meta['freshness_score'],
                    'breakdown': {
                        'semantic': round(semantic, 3),
                        'bm25': round(bm25, 3),
                        'authority': round(authority * 0.25, 3),
                        'freshness': round(freshness * 0.15, 3),
                    }
                })
        
        # Sort by total score
        scored_results.sort(key=lambda x: x['score'], reverse=True)
        
        return scored_results[:top_k]
    
    def verify_consensus(self, query: str, results: List[Dict]) -> Dict:
        """Verify consensus antar top results"""
        if len(results) < 2:
            return {
                'verified': False,
                'consensus_score': 0.5,
                'message': 'Insufficient sources for verification'
            }
        
        # Check keyword overlap antara top 3
        agreements = 0
        contents = [r['content'].lower().split() for r in results[:3]]
        
        for i in range(len(contents)):
            for j in range(i+1, len(contents)):
                words_i = set(contents[i])
                words_j = set(contents[j])
                overlap = len(words_i & words_j) / max(len(words_i), 1)
                if overlap > 0.2:  # 20% overlap threshold
                    agreements += 1
        
        max_possible = len(contents) * (len(contents) - 1) / 2
        consensus_score = agreements / max(1, max_possible)
        
        verified = consensus_score > 0.3 and all(r['authority'] > 0.6 for r in results[:2])
        
        return {
            'verified': verified,
            'consensus_score': round(consensus_score, 2),
            'agreements': agreements,
            'message': 'Sources agree' if verified else 'Limited consensus'
        }
    
    def get_context_for_prompt(self, query: str, max_sources: int = 3) -> Tuple[str, Dict]:
        """
        Get formatted context untuk LLM prompt
        
        Returns: (context_string, metadata)
        """
        sources = self.search(query, top_k=max_sources)
        
        if not sources:
            return "", {'sources': [], 'verified': False}
        
        # Build context string
        context_parts = []
        for i, src in enumerate(sources, 1):
            context_parts.append(
                f"[{i}] Sumber: {src['source']} (Score: {src['score']}, "
                f"Authority: {src['authority']}, Freshness: {src['freshness']})\n"
                f"{src['content'][:500]}"
            )
        
        context = "\n\n".join(context_parts)
        
        # Verify consensus
        verification = self.verify_consensus(query, sources)
        
        metadata = {
            'sources': sources,
            'verification': verification,
            'top_authority': sources[0]['authority'] if sources else 0,
            'avg_score': sum(s['score'] for s in sources) / len(sources) if sources else 0,
        }
        
        return context, metadata


# Singleton instance
_rag_instance = None

def get_trusted_rag(knowledge_dir: str = "data/knowledge/", 
                    db_path: str = "data/kuera_database.db") -> TrustedRAG:
    """Get or create singleton TrustedRAG instance"""
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = TrustedRAG(knowledge_dir, db_path)
    return _rag_instance


if __name__ == "__main__":
    # Test
    print("="*70)
    print("TRUSTED RAG - TEST")
    print("="*70)
    
    rag = TrustedRAG()
    
    test_queries = [
        "machine learning",
        "indonesia",
        "ai",
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-"*50)
        
        results = rag.search(query, top_k=3)
        
        for i, r in enumerate(results, 1):
            print(f"{i}. {r['source']}")
            print(f"   Score: {r['score']} (Authority: {r['authority']}, Fresh: {r['freshness']})")
            print(f"   Content: {r['content'][:100]}...")
            print()


