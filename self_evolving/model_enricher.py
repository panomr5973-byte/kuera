#!/usr/bin/env python
"""
AI Model Enricher - Scale-Up Edition: Billion params, MoE, SSM, Multimodal, Quantized
"""

import json
from pathlib import Path
import logging
import torch
try:
    from huggingface_hub import snapshot_download, HfApi
    from transformers import AutoTokenizer, AutoModel, pipeline
    HAS_HF = True
except ImportError:
    HAS_HF = False
    logging.warning("HuggingFace libs not installed. Run: pip install huggingface_hub transformers torch accelerate")

from datetime import datetime
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ModelEnricher')

class ModelEnricher:
    def __init__(self):
        self.registry_path = Path('models/hf_registry.json')
        self.models_dir = Path('models/hf_models')
        self.models_dir.mkdir(exist_ok=True)
    
    def get_top_models(self, scale_mode=True, limit=3):
        """Get scale-up models for billion-param evolution"""
        if scale_mode:
            candidates = [
                'TheBloke/Mixtral-8x7B-Instruct-v0.1-GGUF',  # MoE Quant
                'state-spaces/mamba-3b-hf',  # SSM Efficiency
                'llava-hf/llava-v1.6-mistral-7b-hf',  # Multimodal Vision
                'meta-llama/Meta-Llama-3.1-70B-Instruct',  # Scale 70B
                'openai/whisper-large-v3',  # Audio Multimodal
                'SeaLLM/SeaLLM-7B-Chat',  # Indonesian
                'CohereForAI/c4ai-command-r-plus'  # 1M Context
            ]
        else:
            candidates = [
                'sentence-transformers/all-MiniLM-L6-v2',
                'indobenchmark/indobert-base-p1',
                'distilgpt2',
                'google/mobilebert-uncased',
                'distilbert-base-uncased-finetuned-sst-2-english'
            ]
        return candidates[:limit]

    def download_model(self, repo_id, model_id):
        """Download & test large scale models (MoE/SSM/Multimodal)"""
        if not HAS_HF:
            logger.warning("HF libs missing. Skipping.")
            return None

        try:
            local_path = self.models_dir / model_id.replace('/', '_').replace('Meta-Llama-3.1-70B-Instruct', 'llama3-70b')
            
            snapshot_download(
                repo_id=repo_id,
                local_dir=local_path,
                local_dir_use_symlinks=False,
                resume_download=True,
                cache_dir=str(self.models_dir / 'cache'),
                max_workers=2
            )
            
            # Dynamic test based on type
            if 'whisper' in repo_id.lower():
                test_pipe = pipeline('automatic-speech-recognition', model=str(local_path), torch_dtype=torch.float16)
            elif 'llava' in repo_id.lower():
                test_pipe = pipeline('image-to-text', model=str(local_path), torch_dtype=torch.float16)
            else:
                test_pipe = pipeline('text-generation', model=str(local_path), tokenizer=str(local_path), device_map='auto', torch_dtype=torch.float16, max_new_tokens=1)
            
            logger.info(f'✅ Scale model loaded ({test_pipe.device}): {repo_id}')
            del test_pipe  # Free mem
            return str(local_path)
            
        except Exception as e:
            logger.error(f'❌ Failed {repo_id}: {e}')
            return None

    def update_registry(self, model_info, local_path=None):
        """Update registry with scale metadata"""
        if self.registry_path.exists():
            with open(self.registry_path) as f:
                registry = json.load(f)
        else:
            registry = {'models': []}
        
        for m in registry['models']:
            if m['model_id'] == model_info['model_id']:
                if local_path:
                    m['local_path'] = local_path
                    m['downloaded'] = True
                    m['downloaded_at'] = datetime.now().isoformat()
                break
        
        registry['enriched_at'] = datetime.now().isoformat()
        
        with open(self.registry_path, 'w') as f:
            json.dump(registry, f, indent=2, default=str)
        
        logger.info(f'📝 Updated scale registry: {model_info["model_id"]}')

    def enrich(self, scale_mode=True):
        """Scale-up enrichment for MoE/SSM/Billion params"""
        logger.info(f'🚀 {"Scale-Up" if scale_mode else "Base"} Enrichment (Production: mixtral MoE)...')
        
        if not self.registry_path.exists():
            logger.error('Registry missing!')
            return
        
        with open(self.registry_path) as f:
            registry = json.load(f)
        
        top_repos = self.get_top_models(scale_mode=scale_mode)
        
        for repo_id in top_repos:
            model_info = next((m for m in registry.get('models', []) if m['hf_repo_id'] == repo_id), None)
            if not model_info:
                logger.warning(f'Skipping {repo_id}')
                continue
            
            model_id = model_info['model_id']
            if model_info.get('downloaded'):
                logger.info(f'⏭️ {model_id} ready')
                continue
            
            local_path = self.download_model(repo_id, model_id)
            if local_path:
                self.update_registry(model_info, local_path)
        
        logger.info('🎉 Scale architecture ready! Check TODO.md')

if __name__ == '__main__':
    enricher = ModelEnricher()
    enricher.enrich(scale_mode=True)
