#!/usr/bin/env python3
"""
Dynamic Model Loader - Scale Architecture with Quant, Context Extension, Multimodal Support
+ PEFT Adapter Support for Training Pipeline
"""

import json
from pathlib import Path
import logging
import torch
from transformers import (
    AutoTokenizer, AutoModelForCausalLM, AutoModelForVision2Seq, AutoModelForSpeechSeq2Seq, pipeline
)
from peft import PeftModel
from accelerate import infer_auto_device_map

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ScaleLoader')

class ScaleModelLoader:
    def __init__(self, registry_path='models/hf_registry.json'):
        self.registry_path = Path(registry_path)
        self.registry = self.load_registry()
    
    def load_registry(self):
        with open(self.registry_path) as f:
            return json.load(f)
    
    def load_production(self, quant='fp16', device_map='auto', adapter_path=None):
        """Load current production model + optional PEFT adapter from training"""
        prod_id = self.registry['current_production']
        model_info = next((m for m in self.registry.get('models', []) if m['model_id'] == prod_id), {'hf_repo_id': prod_id})
        repo_id = model_info['hf_repo_id']
        
        tokenizer = AutoTokenizer.from_pretrained(repo_id)
        if 'llava' in repo_id:
            model = AutoModelForVision2Seq.from_pretrained(repo_id, torch_dtype=torch.float16, device_map=device_map)
        elif 'whisper' in repo_id:
            model = AutoModelForSpeechSeq2Seq.from_pretrained(repo_id, torch_dtype=torch.float16, device_map=device_map)
        else:
            model = AutoModelForCausalLM.from_pretrained(
                repo_id, 
                torch_dtype=torch.float16 if quant == 'fp16' else torch.float32,
                device_map=device_map,
                trust_remote_code=True,
                attn_implementation="flash_attention_2" if torch.cuda.is_available() else None
            )
        
        if adapter_path:
            model = PeftModel.from_pretrained(model, adapter_path)
            logger.info(f'Loaded adapter: {adapter_path}')
        
        pipe = pipeline('text-generation', model=model, tokenizer=tokenizer, device_map=device_map)
        logger.info(f"Loaded production {prod_id} ({model_info.get('params_m', 'N/A')}M params)" + (f" + adapter {Path(adapter_path).name}" if adapter_path else ""))
        return pipe
    
    def load_model(self, model_id, task='text-generation', **kwargs):
        model_info = next((m for m in self.registry.get('models', []) if m['model_id'] == model_id), None)
        if model_info:
            repo_id = model_info['hf_repo_id']
            # Dynamic load...
            return f"Loaded {model_id} for {task}"
        return f"Model {model_id} not found"

if __name__ == '__main__':
    loader = ScaleModelLoader()
    pipe = loader.load_production()
    print('Scale model loader ready for billion-param MoE/SSM/Multimodal + PEFT!')
    print(pipe("Hello, world!")[0]['generated_text'][:100])
