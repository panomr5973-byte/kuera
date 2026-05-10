#!/usr/bin/env python
"""
KUWERA LLM Integration menggunakan CTransformers
Alternative to llama-cpp-python (easier installation)
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Iterator
from dataclasses import dataclass

try:
    from ctransformers import AutoModelForCausalLM
    CT_AVAILABLE = True
except ImportError:
    CT_AVAILABLE = False
    logging.warning("ctransformers not installed. Run: pip install ctransformers")


@dataclass
class ModelConfig:
    """Konfigurasi untuk model LLM"""
    name: str
    model_path: str
    context_length: int = 2048
    temperature: float = 0.7
    max_tokens: int = 512
    top_p: float = 0.9
    top_k: int = 40
    repetition_penalty: float = 1.1


class KueraLLM:
    """
    Wrapper untuk LLM menggunakan CTransformers
    """
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load model ke memori"""
        if not CT_AVAILABLE:
            raise ImportError("ctransformers not installed. Run: pip install ctransformers")
        
        if not Path(self.config.model_path).exists():
            raise FileNotFoundError(f"Model not found: {self.config.model_path}")
        
        logging.info(f"Loading model: {self.config.name}")
        logging.info(f"Path: {self.config.model_path}")
        
        self.model = AutoModelForCausalLM.from_pretrained(
            self.config.model_path,
            model_type="llama",  # or "gpt2", "gptj", etc.
            context_length=self.config.context_length
        )
        
        logging.info(f"[OK] Model loaded: {self.config.name}")
    
    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate response dari model
        
        Args:
            prompt: Input prompt
            **kwargs: Override generation parameters
        
        Returns:
            Generated text
        """
        if self.model is None:
            raise RuntimeError("Model not loaded")
        
        # Merge parameters
        max_tokens = kwargs.get("max_tokens", self.config.max_tokens)
        temperature = kwargs.get("temperature", self.config.temperature)
        top_p = kwargs.get("top_p", self.config.top_p)
        top_k = kwargs.get("top_k", self.config.top_k)
        repetition_penalty = kwargs.get("repetition_penalty", self.config.repetition_penalty)
        
        # Generate
        response = self.model(
            prompt,
            max_new_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            repetition_penalty=repetition_penalty,
            stop=["</s>", "Human:", "User:", "Assistant:"]
        )
        
        return response.strip()
    
    def chat(self, message: str, system_prompt: Optional[str] = None, 
             history: Optional[List[Dict]] = None) -> str:
        """
        Chat-style conversation dengan model
        
        Args:
            message: User message
            system_prompt: System prompt/instruction
            history: List of previous messages
        
        Returns:
            Assistant response
        """
        # Build prompt
        prompt_parts = []
        
        if system_prompt:
            prompt_parts.append(f"System: {system_prompt}")
        
        if history:
            for msg in history:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role == "user":
                    prompt_parts.append(f"Human: {content}")
                else:
                    prompt_parts.append(f"Assistant: {content}")
        
        prompt_parts.append(f"Human: {message}")
        prompt_parts.append("Assistant:")
        
        prompt = "\n\n".join(prompt_parts)
        
        return self.generate(prompt)
    
    def get_model_info(self) -> Dict:
        """Get model information"""
        return {
            "name": self.config.name,
            "path": self.config.model_path,
            "context_length": self.config.context_length,
            "parameters": {
                "temperature": self.config.temperature,
                "max_tokens": self.config.max_tokens,
                "top_p": self.config.top_p,
                "top_k": self.config.top_k
            }
        }


class ModelManager:
    """
    Manager untuk mengelola multiple models
    """
    
    def __init__(self, models_dir: str = "models/llm"):
        self.models_dir = Path(models_dir)
        self.registry_path = self.models_dir / "llm_registry.json"
        self.loaded_models: Dict[str, KueraLLM] = {}
        self.current_model: Optional[str] = None
        
        self._load_registry()
    
    def _load_registry(self):
        """Load model registry"""
        if self.registry_path.exists():
            with open(self.registry_path) as f:
                self.registry = json.load(f)
        else:
            self.registry = {"available_models": [], "downloaded": []}
    
    def get_available_models(self) -> List[Dict]:
        """Get list of available models"""
        available = []
        
        for model in self.registry.get("available_models", []):
            model_path = self.models_dir / model["filename"]
            is_downloaded = model_path.exists()
            
            available.append({
                **model,
                "is_downloaded": is_downloaded,
                "actual_path": str(model_path) if is_downloaded else None
            })
        
        return available
    
    def load_model(self, model_name: str) -> KueraLLM:
        """Load model by name"""
        # Check if already loaded
        if model_name in self.loaded_models:
            self.current_model = model_name
            return self.loaded_models[model_name]
        
        # Find model config
        model_config = None
        for model in self.registry.get("available_models", []):
            if model["name"] == model_name:
                model_config = model
                break
        
        if not model_config:
            raise ValueError(f"Model not found: {model_name}")
        
        # Check if downloaded
        model_path = self.models_dir / model_config["filename"]
        if not model_path.exists():
            raise FileNotFoundError(
                f"Model not downloaded: {model_name}\n"
                f"Run: python download_models_simple.py"
            )
        
        # Create config and load
        config = ModelConfig(
            name=model_config["name"],
            model_path=str(model_path),
            context_length=2048,
            temperature=0.7,
            max_tokens=512
        )
        
        llm = KueraLLM(config)
        self.loaded_models[model_name] = llm
        self.current_model = model_name
        
        return llm
    
    def get_current_model(self) -> Optional[KueraLLM]:
        """Get currently loaded model"""
        if self.current_model and self.current_model in self.loaded_models:
            return self.loaded_models[self.current_model]
        return None
    
    def list_models(self) -> str:
        """Generate formatted list of models"""
        models = self.get_available_models()
        
        lines = []
        lines.append("="*70)
        lines.append("AVAILABLE MODELS")
        lines.append("="*70)
        lines.append("")
        
        for i, model in enumerate(models, 1):
            status = "[DOWNLOADED]" if model["is_downloaded"] else "[NOT DOWNLOADED]"
            current = " <- CURRENT" if model["name"] == self.current_model else ""
            
            lines.append(f"{i}. {model['name']}{current}")
            lines.append(f"   Size: {model['size_gb']} GB | Status: {status}")
            lines.append(f"   {model['description']}")
            lines.append("")
        
        lines.append("="*70)
        return "\n".join(lines)


def test_model():
    """Test function"""
    print("="*70)
    print("KUWERA LLM INTEGRATION TEST (CTransformers)")
    print("="*70)
    print()
    
    # Check ctransformers
    if not CT_AVAILABLE:
        print("[ERROR] ctransformers not installed.")
        print("Install with: pip install ctransformers")
        return
    
    # Initialize manager
    manager = ModelManager()
    
    # Show available models
    print(manager.list_models())
    
    # Try to load first downloaded model
    models = manager.get_available_models()
    downloaded = [m for m in models if m["is_downloaded"]]
    
    if not downloaded:
        print("\n[WARNING] No models downloaded yet.")
        print("Run: python download_models_simple.py")
        return
    
    # Load first model
    model_name = downloaded[0]["name"]
    print(f"\nLoading model: {model_name}")
    
    try:
        llm = manager.load_model(model_name)
        print(f"[OK] Model loaded successfully!")
        
        # Test generation
        print("\n[Test Generation]")
        prompt = "Q: What is AI?\nA:"
        print(f"Prompt: {prompt}")
        print("Generating... (this may take a moment)")
        
        response = llm.generate(prompt, max_tokens=100)
        print(f"Response: {response}")
        
        # Test chat
        print("\n[Test Chat]")
        response = llm.chat(
            message="Hello, who are you?",
            system_prompt="You are Kuwera, a helpful AI assistant.",
            history=[]
        )
        print(f"Response: {response}")
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*70)


if __name__ == "__main__":
    test_model()
