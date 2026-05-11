#!/usr/bin/env python
"""
Data & Knowledge Foundation Manager for Self-Evolving AI
Handles: Large datasets, curation, multimodal, KG, continuous learning
"""

import json
from pathlib import Path
import pandas as pd
from datetime import datetime
from typing import Dict, List
import logging
from sentence_transformers import SentenceTransformer
import networkx as nx
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('DataKnowledge')

class DataKnowledgeFoundation:
    def __init__(self, base_dir='data/knowledge'):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
        self.text_dir = self.base_dir / 'text'
        self.multimodal_dir = self.base_dir / 'multimodal'
        self.kg_dir = self.base_dir / 'knowledge_graph'
        self.text_dir.mkdir(exist_ok=True)
        self.multimodal_dir.mkdir(exist_ok=True)
        self.kg_dir.mkdir(exist_ok=True)
        
        # Use enriched HF model
        try:
            self.embedder = SentenceTransformer('models/hf_models/hf_all_minilm_l6_v2')
        except:
            logger.warning("HF model not ready, using default")
            self.embedder = None
        
        self.kg = nx.DiGraph()
        self.load_kg()
    
    def curate_dataset(self, input_dir: str, min_quality_score: float = 0.7, max_size_mb: int = 1000) -> pd.DataFrame:
        """Data Curation: Clean, filter, score quality"""
        logger.info(f"Curating data from {input_dir}")
        
        df = pd.read_csv(input_dir) if Path(input_dir).suffix == '.csv' else pd.read_json(input_dir)
        
        # Quality filters
        df = df.dropna()
        df = df[df['text'].str.len() > 10]  # Min length
        df = df[df['text'].str.len() < 5000]  # Max length
        
        # Semantic dedup using embeddings
        if self.embedder:
            embeddings = self.embedder.encode(df['text'].tolist())
            from sklearn.metrics.pairwise import cosine_similarity
            sim = cosine_similarity(embeddings)
            df['dup_score'] = sim.max(axis=1)
            df = df[df['dup_score'] < 0.95]
        
        # Save curated
        output_path = self.text_dir / f"curated_{datetime.now().strftime('%Y%m%d')}.csv"
        df.to_csv(output_path, index=False)
        logger.info(f"Curated {len(df)} samples -> {output_path}")
        return df
    
    def add_multimodal(self, data_type: str, files: List[str]):
        """Handle multimodal data"""
        for file in files:
            dest = self.multimodal_dir / data_type / Path(file).name
            dest.parent.mkdir(exist_ok=True)
            Path(file).rename(dest)
        logger.info(f"Added {len(files)} {data_type} files")
    
    def build_knowledge_graph(self, texts: List[str], entities: List[str] = None):
        """Simple KG from texts"""
        self.kg.add_nodes_from(entities or texts[:50])
        
        # Basic relations (expand with NER)
        for i in range(len(texts)-1):
            self.kg.add_edge(texts[i], texts[i+1], relation='context')
        
        self.save_kg()
        logger.info(f"KG nodes: {self.kg.number_of_nodes()}, edges: {self.kg.number_of_edges()}")
    
    def continuous_update(self, new_data_path: str):
        """Continuous learning: Merge new data"""
        existing = list(self.text_dir.glob('*.csv'))
        if existing:
            df_old = pd.concat([pd.read_csv(f) for f in existing[-3:]], ignore_index=True)  # Last 3
        else:
            df_old = pd.DataFrame()
        
        df_new = pd.read_csv(new_data_path)
        df_combined = pd.concat([df_old, df_new]).drop_duplicates(subset=['text'])
        
        output = self.text_dir / f"knowledge_{datetime.now().strftime('%Y%m%d')}.csv"
        df_combined.to_csv(output, index=False)
        logger.info(f"Updated knowledge: {len(df_combined)} total samples")
    
    def load_kg(self):
        kg_path = self.kg_dir / 'knowledge.json'
        if kg_path.exists():
            data = json.load(kg_path)
            self.kg = nx.node_link_graph(data)
    
    def save_kg(self):
        data = nx.node_link_data(self.kg)
        kg_path = self.kg_dir / 'knowledge.json'
        json.dump(data, kg_path)
    
    def get_stats(self) -> Dict:\n        stats = {\n            'text_datasets': len(list(self.text_dir.glob('*.csv'))),\n            'multimodal_types': [d.name for d in self.multimodal_dir.iterdir() if d.is_dir()],\n            'kg_nodes': self.kg.number_of_nodes(),\n            'kg_edges': self.kg.number_of_edges(),\n            'total_size_gb': sum(f.stat().st_size for f in self.base_dir.rglob('*') if f.is_file()) / 1e9\n        }\n        return stats\n\n    def generate_instructions(self, num_samples=500):\n        \"""Generate synthetic instructions for SFT\\\"\""\n        instructions_dir = self.text_dir.parent / 'sft'\n        instructions_dir.mkdir(exist_ok=True)\n        data = [\n            {'instruction': f'Jelaskan {i}', 'input': f'Topik {i}', 'output': f'Penjelasan lengkap tentang {i}.'} \n            for i in range(num_samples)\n        ]\n        path = instructions_dir / 'instructions.json'\n        with open(path, 'w') as f:\n            json.dump(data, f, indent=2)\n        logger.info(f'Generated {num_samples} instructions -> {path}')\n        return path\n\n    def generate_preferences(self, num_samples=200):\n        \"""Generate RLHF preferences (Indonesian)\\\"\""\n        preferences_dir = self.text_dir.parent / 'rlhf'\n        preferences_dir.mkdir(exist_ok=True)\n        data = [\n            {'prompt': f'Prompt {i}', 'chosen': f'Respon bagus {i}', 'rejected': f'Respon buruk {i}'} \n            for i in range(num_samples)\n        ]\n        path = preferences_dir / 'preferences.json'\n        with open(path, 'w') as f:\n            json.dump(data, f, indent=2)\n        logger.info(f'Generated {num_samples} preferences -> {path}')\n        return path\n\nif __name__ == '__main__':
    foundation = DataKnowledgeFoundation()
    print("Data & Knowledge Foundation ready!")
    print(json.dumps(foundation.get_stats(), indent=2))
    
    # Example usage
    # foundation.curate_dataset('raw_data.csv')
    # foundation.continuous_update('new_data.csv')
    logger.info("Run foundation.curate_dataset(), .continuous_update(), etc.")

