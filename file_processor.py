#!/usr/bin/env python3
"""
File Processor untuk KUERA
Menangani ekstraksi teks dari berbagai format file
"""

import os
import re
import sys
from pathlib import Path
from datetime import datetime

# Add user site-packages to path untuk Windows
sys.path.insert(0, r'C:\Users\Admin\AppData\Roaming\Python\Python314\site-packages')

# Try to import optional dependencies
try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("[WARNING] PyPDF2 not available")

try:
    import docx
    DOCX_AVAILABLE = True
except ImportError as e:
    DOCX_AVAILABLE = False
    print(f"[WARNING] python-docx not available: {e}")


class FileProcessor:
    """Processor untuk mengekstrak teks dari file"""
    
    def __init__(self, upload_dir="data/uploads"):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    def save_uploaded_file(self, file_storage):
        """Save uploaded file ke disk"""
        original_name = file_storage.filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = f"{timestamp}_{self._sanitize_filename(original_name)}"
        file_path = self.upload_dir / safe_name
        
        file_storage.save(str(file_path))
        
        return {
            'original_name': original_name,
            'saved_name': safe_name,
            'file_path': str(file_path),
            'file_size': file_path.stat().st_size,
            'file_type': self._get_file_type(original_name)
        }
    
    def extract_text(self, file_path, file_type=None):
        """Extract text dari file berdasarkan type"""
        if file_type is None:
            file_type = self._get_file_type(file_path)
        
        file_type = file_type.lower()
        
        if file_type == 'txt' or file_type == 'text':
            return self._extract_txt(file_path)
        elif file_type == 'pdf':
            return self._extract_pdf(file_path)
        elif file_type in ['docx', 'doc']:
            return self._extract_docx(file_path)
        elif file_type == 'csv':
            return self._extract_csv(file_path)
        elif file_type in ['json']:
            return self._extract_json(file_path)
        else:
            # Try as text file
            try:
                return self._extract_txt(file_path)
            except:
                return None
    
    def generate_summary(self, text, max_length=500):
        """Generate summary dari teks"""
        if not text:
            return ""
        
        # Bersihkan teks
        text = text.strip()
        
        # Ambil paragraf pertama yang meaningful
        paragraphs = text.split('\n\n')
        summary_parts = []
        current_length = 0
        
        for para in paragraphs:
            para = para.strip()
            if len(para) < 20:  # Skip paragraf terlalu pendek
                continue
            
            if current_length + len(para) <= max_length:
                summary_parts.append(para)
                current_length += len(para)
            else:
                remaining = max_length - current_length
                if remaining > 50:
                    summary_parts.append(para[:remaining] + "...")
                break
        
        summary = ' '.join(summary_parts)
        if len(summary) > max_length:
            summary = summary[:max_length] + "..."
        
        return summary
    
    def extract_keywords(self, text, max_keywords=10):
        """Extract keywords dari teks"""
        if not text:
            return ""
        
        # Clean text
        text = text.lower()
        
        # Remove common Indonesian stopwords
        stopwords = {
            'dan', 'atau', 'yang', 'di', 'ke', 'dari', 'pada', 'dalam', 'untuk', 'dengan',
            'adalah', 'ini', 'itu', 'saya', 'anda', 'dia', 'kita', 'mereka', 'tidak', 'ya',
            'sudah', 'akan', 'bisa', 'dapat', 'oleh', 'karena', 'seperti', 'jika', 'maka',
            'the', 'and', 'or', 'is', 'are', 'was', 'were', 'be', 'been', 'to', 'of', 'in',
            'for', 'on', 'with', 'at', 'from', 'as', 'a', 'an', 'this', 'that', 'i', 'you',
            'he', 'she', 'it', 'we', 'they', 'not', 'yes', 'can', 'could', 'will', 'would'
        }
        
        # Extract words
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text)
        
        # Count frequency
        word_counts = {}
        for word in words:
            if word not in stopwords and len(word) > 3:
                word_counts[word] = word_counts.get(word, 0) + 1
        
        # Get top keywords
        sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
        keywords = [word for word, count in sorted_words[:max_keywords]]
        
        return ', '.join(keywords)
    
    def chunk_text(self, text, chunk_size=1000, overlap=100):
        """Split text into chunks untuk RAG"""
        if not text:
            return []
        
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + chunk_size
            
            # Try to end at a sentence boundary
            if end < text_length:
                # Look for sentence ending
                search_end = min(end + 100, text_length)
                sentence_end = text.rfind('. ', end - 50, search_end)
                if sentence_end != -1:
                    end = sentence_end + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap
        
        return chunks
    
    def _sanitize_filename(self, filename):
        """Sanitize filename untuk keamanan"""
        # Remove path components
        filename = Path(filename).name
        # Replace spaces with underscores
        filename = filename.replace(' ', '_')
        # Remove potentially dangerous characters
        filename = re.sub(r'[^a-zA-Z0-9._-]', '', filename)
        return filename
    
    def _get_file_type(self, filename):
        """Get file type dari extension"""
        ext = Path(filename).suffix.lower()
        type_map = {
            '.txt': 'txt', '.text': 'txt',
            '.pdf': 'pdf',
            '.docx': 'docx', '.doc': 'doc',
            '.csv': 'csv',
            '.json': 'json',
            '.md': 'txt', '.markdown': 'txt'
        }
        return type_map.get(ext, 'unknown')
    
    def _extract_txt(self, file_path):
        """Extract text dari file txt"""
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
        
        # Last resort - read as binary and ignore errors
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    
    def _extract_pdf(self, file_path):
        """Extract text dari file PDF"""
        global PDF_AVAILABLE
        
        if not PDF_AVAILABLE:
            return "[Error: PyPDF2 not installed. Install with: pip install PyPDF2]"
        
        try:
            text = []
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text.append(page_text)
            return '\n\n'.join(text)
        except Exception as e:
            return f"[Error extracting PDF: {str(e)}]"
    
    def _extract_docx(self, file_path):
        """Extract text dari file DOCX"""
        global DOCX_AVAILABLE
        
        # Try to import again dengan path yang benar
        if not DOCX_AVAILABLE:
            try:
                import docx
                DOCX_AVAILABLE = True
            except ImportError as e:
                return f"[Error: python-docx not installed. Install with: pip install python-docx. Detail: {e}]"
        
        try:
            import docx
            doc = docx.Document(file_path)
            paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
            return '\n\n'.join(paragraphs)
        except Exception as e:
            return f"[Error extracting DOCX: {str(e)}]"
    
    def _extract_csv(self, file_path):
        """Extract text dari file CSV"""
        import csv
        try:
            text = []
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                reader = csv.reader(f)
                for row in reader:
                    text.append(' | '.join(row))
            return '\n'.join(text)
        except Exception as e:
            return f"[Error extracting CSV: {str(e)}]"
    
    def _extract_json(self, file_path):
        """Extract text dari file JSON"""
        import json
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return json.dumps(data, indent=2, ensure_ascii=False)
        except Exception as e:
            return f"[Error extracting JSON: {str(e)}]"


# Global instance
file_processor = FileProcessor()


if __name__ == "__main__":
    # Test
    processor = FileProcessor()
    print("[File Processor] Ready")
    print(f"[File Processor] Upload directory: {processor.upload_dir}")
    print(f"[File Processor] PDF support: {PDF_AVAILABLE}")
    print(f"[File Processor] DOCX support: {DOCX_AVAILABLE}")
