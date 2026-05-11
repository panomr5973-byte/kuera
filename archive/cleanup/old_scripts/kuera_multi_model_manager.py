#!/usr/bin/env python
"""
KUWERA Multi-Model Manager
Manajemen multiple AI models dengan routing cerdas
"""

import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime

try:
    from ctransformers import AutoModelForCausalLM
    CT_AVAILABLE = True
except ImportError:
    CT_AVAILABLE = False


@dataclass
class ModelCapability:
    """Kemampuan model"""
    name: str
    supports_indonesian: bool
    supports_english: bool
    supports_chinese: bool
    context_length: int
    size_gb: float
    strengths: List[str]


class KueraMultiModelManager:
    """
    Manager untuk multiple models dengan smart routing
    """
    
    def __init__(self, models_dir: str = "models/llm"):
        self.models_dir = Path(models_dir)
        self.registry_path = self.models_dir / "llm_registry.json"
        self.loaded_models: Dict[str, any] = {}
        self.current_model: Optional[str] = None
        
        # Define capabilities for each model
        self.model_capabilities = {
            "Qwen2.5-1.5B-Instruct": ModelCapability(
                name="Qwen2.5-1.5B-Instruct",
                supports_indonesian=True,
                supports_english=True,
                supports_chinese=True,
                context_length=32768,
                size_gb=1.04,
                strengths=["indonesian", "multilingual", "fast", "lightweight"]
            ),
            "Qwen2.5-3B-Instruct": ModelCapability(
                name="Qwen2.5-3B-Instruct",
                supports_indonesian=True,
                supports_english=True,
                supports_chinese=True,
                context_length=32768,
                size_gb=0.8,
                strengths=["indonesian", "multilingual", "balanced", "high_quality"]
            ),
            "SeaLLM-7B-v2": ModelCapability(
                name="SeaLLM-7B-v2",
                supports_indonesian=True,
                supports_english=True,
                supports_chinese=True,
                context_length=8192,
                size_gb=1.9,
                strengths=["southeast_asia", "indonesian", "malay", "cultural_aware"]
            ),
            "Merak-7B-v4": ModelCapability(
                name="Merak-7B-v4",
                supports_indonesian=True,
                supports_english=True,
                supports_chinese=False,
                context_length=4096,
                size_gb=1.9,
                strengths=["indonesian", "local_slang", "buatan_indonesia", "cultural"]
            ),
            "Llama-3.2-3B-Instruct": ModelCapability(
                name="Llama-3.2-3B-Instruct",
                supports_indonesian=True,
                supports_english=True,
                supports_chinese=False,
                context_length=128000,
                size_gb=0.8,
                strengths=["multilingual", "long_context", "meta", "tool_use"]
            ),
            "Gemma-2-2B-it": ModelCapability(
                name="Gemma-2-2B-it",
                supports_indonesian=True,
                supports_english=True,
                supports_chinese=False,
                context_length=8192,
                size_gb=0.6,
                strengths=["google", "safety", "balanced", "reliable"]
            ),
            "Phi-3.5-mini-instruct": ModelCapability(
                name="Phi-3.5-mini-instruct",
                supports_indonesian=True,
                supports_english=True,
                supports_chinese=False,
                context_length=128000,
                size_gb=0.9,
                strengths=["microsoft", "reasoning", "coding", "long_context"]
            ),
            "Command-R-v01": ModelCapability(
                name="Command-R-v01",
                supports_indonesian=True,
                supports_english=True,
                supports_chinese=False,
                context_length=131072,
                size_gb=1.0,
                strengths=["rag", "long_context", "knowledge", "cohere"]
            ),
            "StableLM-2-1.6B-Chat": ModelCapability(
                name="StableLM-2-1.6B-Chat",
                supports_indonesian=True,
                supports_english=True,
                supports_chinese=False,
                context_length=4096,
                size_gb=0.5,
                strengths=["stable", "balanced", "stability_ai"]
            ),
            "TinyLlama-1.1B-Chat": ModelCapability(
                name="TinyLlama-1.1B-Chat",
                supports_indonesian=False,
                supports_english=True,
                supports_chinese=False,
                context_length=2048,
                size_gb=0.3,
                strengths=["ultra_lightweight", "fast", "english_only"]
            )
        }
        
        self._load_registry()
    
    def _load_registry(self):
        """Load model registry"""
        if self.registry_path.exists():
            with open(self.registry_path) as f:
                self.registry = json.load(f)
        else:
            self.registry = {"available_models": [], "downloaded": []}
    
    def get_downloaded_models(self) -> List[str]:
        """Get list of downloaded models"""
        downloaded = []
        for model_name, capability in self.model_capabilities.items():
            # Find filename from registry
            for reg_model in self.registry.get("available_models", []):
                if reg_model["name"] == model_name:
                    model_path = self.models_dir / reg_model["filename"]
                    if model_path.exists():
                        downloaded.append(model_name)
                        break
        return downloaded
    
    def select_best_model(self, query: str, context: str = "") -> str:
        """
        Pilih model terbaik berdasarkan query dan context
        
        Returns:
            Name of best model for the task
        """
        query_lower = query.lower()
        downloaded = self.get_downloaded_models()
        
        if not downloaded:
            raise RuntimeError("No models downloaded")
        
        # Rule-based routing
        
        # 1. Bahasa Indonesia with slang/local context
        if any(word in query_lower for word in [
            "gue", "lu", "elo", "gw", "lo", "sih", "dong", "nih", 
            "bete", "kepo", "mager", "gokil", "santuy"
        ]):
            if "Merak-7B-v4" in downloaded:
                return "Merak-7B-v4"
        
        # 2. Bahasa Indonesia formal
        if any(word in query_lower for word in [
            "indonesia", "bahasa indonesia", "jakarta", "nusantara",
            "budaya", "adat", "tradisi", "pancasila"
        ]):
            priority = ["Qwen2.5-3B-Instruct", "SeaLLM-7B-v2", "Qwen2.5-1.5B-Instruct"]
            for model in priority:
                if model in downloaded:
                    return model
        
        # 3. Southeast Asia context
        if any(word in query_lower for word in [
            "malaysia", "singapura", "thailand", "vietnam", "filipina",
            "asean", "melayu", "singapore", "bangkok"
        ]):
            if "SeaLLM-7B-v2" in downloaded:
                return "SeaLLM-7B-v2"
        
        # 4. Long document/RAG
        if len(query) > 1000 or any(word in query_lower for word in ["dokumen", "dokumen panjang", "rag"]):
            priority = ["Command-R-v01", "Phi-3.5-mini-instruct", "Llama-3.2-3B-Instruct"]
            for model in priority:
                if model in downloaded:
                    return model
        
        # 5. Coding/Technical
        if any(word in query_lower for word in ["code", "programming", "python", "coding"]):
            priority = ["Phi-3.5-mini-instruct", "Llama-3.2-3B-Instruct"]
            for model in priority:
                if model in downloaded:
                    return model
        
        # 6. Safety/Cautious topics
        if any(word in query_lower for word in ["sensitive", "politik", "agama", "ras"]):
            if "Gemma-2-2B-it" in downloaded:
                return "Gemma-2-2B-it"
        
        # 7. Default: Best Indonesian model
        priority = [
            "Qwen2.5-3B-Instruct",
            "Qwen2.5-1.5B-Instruct",
            "SeaLLM-7B-v2",
            "Merak-7B-v4",
            "Llama-3.2-3B-Instruct"
        ]
        for model in priority:
            if model in downloaded:
                return model
        
        # Fallback to any available model
        return downloaded[0]
    
    def load_model(self, model_name: str) -> AutoModelForCausalLM:
        """Load model by name"""
        if model_name in self.loaded_models:
            self.current_model = model_name
            return self.loaded_models[model_name]
        
        # Find model in registry
        model_info = None
        for reg_model in self.registry.get("available_models", []):
            if reg_model["name"] == model_name:
                model_info = reg_model
                break
        
        if not model_info:
            raise ValueError(f"Model {model_name} not found in registry")
        
        model_path = self.models_dir / model_info["filename"]
        if not model_path.exists():
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        if not CT_AVAILABLE:
            raise ImportError("ctransformers not installed")
        
        print(f"Loading {model_name}...")
        
        # Determine model type
        if "qwen" in model_name.lower():
            model_type = "qwen"
        elif "llama" in model_name.lower():
            model_type = "llama"
        else:
            model_type = "llama"  # Default
        
        try:
            model = AutoModelForCausalLM.from_pretrained(
                str(model_path),
                model_type=model_type,
                context_length=8192
            )
            self.loaded_models[model_name] = model
            self.current_model = model_name
            print(f"[OK] {model_name} loaded")
            return model
        except Exception as e:
            # Fallback to llama type
            model = AutoModelForCausalLM.from_pretrained(
                str(model_path),
                model_type="llama",
                context_length=4096
            )
            self.loaded_models[model_name] = model
            self.current_model = model_name
            print(f"[OK] {model_name} loaded (fallback)")
            return model
    
    def generate(self, prompt: str, model_name: Optional[str] = None, **kwargs) -> str:
        """Generate response using specified or auto-selected model"""
        if model_name is None:
            model_name = self.select_best_model(prompt)
        
        model = self.load_model(model_name)
        
        max_tokens = kwargs.get("max_tokens", 300)
        temperature = kwargs.get("temperature", 0.7)
        
        response = model(prompt, max_new_tokens=max_tokens, temperature=temperature)
        return response.strip()
    
    def get_model_info(self, model_name: str) -> Optional[ModelCapability]:
        """Get capability info for a model"""
        return self.model_capabilities.get(model_name)
    
    def list_models_detailed(self) -> str:
        """Generate detailed model list"""
        downloaded = self.get_downloaded_models()
        
        lines = []
        lines.append("="*80)
        lines.append("KUWERA MULTI-MODEL SYSTEM")
        lines.append("="*80)
        lines.append(f"\nTotal Downloaded: {len(downloaded)} models")
        lines.append(f"Current Model: {self.current_model or 'None'}")
        lines.append("")
        lines.append("-"*80)
        lines.append("AVAILABLE MODELS:")
        lines.append("-"*80)
        
        for i, model_name in enumerate(downloaded, 1):
            cap = self.model_capabilities.get(model_name)
            if cap:
                lines.append(f"\n{i}. {model_name}")
                lines.append(f"   Size: {cap.size_gb} GB")
                lines.append(f"   Indonesian: {'Yes' if cap.supports_indonesian else 'No'}")
                lines.append(f"   Context: {cap.context_length:,} tokens")
                lines.append(f"   Strengths: {', '.join(cap.strengths)}")
                if model_name == self.current_model:
                    lines.append("   [CURRENTLY LOADED]")
        
        lines.append("")
        lines.append("-"*80)
        lines.append("ROUTING RULES:")
        lines.append("-"*80)
        lines.append("  - Indonesian slang -> Merak-7B")
        lines.append("  - Indonesian formal -> Qwen2.5-3B")
        lines.append("  - SEA context -> SeaLLM-7B")
        lines.append("  - Long documents -> Command-R")
        lines.append("  - Coding -> Phi-3.5")
        lines.append("  - Safety critical -> Gemma-2")
        lines.append("="*80)
        
        return "\n".join(lines)


class KueraSmartRouter:
    """
    Router cerdas untuk memilih model berdasarkan kebutuhan
    """
    
    def __init__(self, manager: KueraMultiModelManager):
        self.manager = manager
    
    def route_and_generate(self, user_message: str, system_context: str = "") -> Dict:
        """
        Route ke model terbaik dan generate response
        
        Returns:
            Dictionary dengan response dan metadata
        """
        # Select best model
        selected_model = self.manager.select_best_model(user_message)
        
        # Get model capability
        capability = self.manager.get_model_info(selected_model)
        
        # Generate response
        try:
            response = self.manager.generate(user_message, selected_model)
            success = True
            error = None
        except Exception as e:
            response = f"[Error: {e}]"
            success = False
            error = str(e)
        
        return {
            "response": response,
            "model_used": selected_model,
            "model_strengths": capability.strengths if capability else [],
            "supports_indonesian": capability.supports_indonesian if capability else False,
            "success": success,
            "error": error
        }


if __name__ == "__main__":
    # Test
    print("Initializing Multi-Model Manager...")
    manager = KueraMultiModelManager()
    print(manager.list_models_detailed())
