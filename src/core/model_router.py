"""KUERA AI — Multi-Model Router.

Routes tasks to the most appropriate model:
- Local (ctransformers .gguf) for simple, offline, privacy-critical tasks
- Cloud (OpenAI-compatible API) for complex reasoning tasks

Usage:
    from src.core.model_router import ModelRouter
    router = ModelRouter()
    result = router.generate("Analyze this audit finding...", task_complexity="high")
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger("KUERA-ModelRouter")

BASE_DIR = Path(__file__).parent.parent.parent.resolve()


@dataclass
class ModelResponse:
    text: str
    provider: str
    model: str
    tokens_used: Optional[int] = None
    latency_ms: Optional[int] = None
    error: Optional[str] = None


class LocalModelProvider:
    """Provider for local GGUF models via ctransformers."""

    def __init__(self, models_dir: Path = None):
        self.models_dir = models_dir or (BASE_DIR / "models" / "llm")
        self._models: Dict[str, any] = {}  # lazy-loaded
        self._default_model = "Llama-3.2-3B-Instruct-Q4_K_M.gguf"
        self._scan_available()

    def _scan_available(self):
        self.available = []
        if self.models_dir.exists():
            self.available = sorted([f.name for f in self.models_dir.glob("*.gguf")])
        logger.info("[Local] Found %d GGUF models", len(self.available))

    def _load(self, filename: str):
        if filename in self._models:
            return self._models[filename]
        try:
            from ctransformers import AutoModelForCausalLM
            path = self.models_dir / filename
            model = AutoModelForCausalLM.from_pretrained(
                str(path),
                model_type="llama",
                max_new_tokens=512,
                context_length=4096,
            )
            self._models[filename] = model
            logger.info("[Local] Loaded %s", filename)
            return model
        except Exception as e:
            logger.error("[Local] Failed to load %s: %s", filename, e)
            return None

    def generate(self, prompt: str, system_prompt: str = "", model_file: str = None) -> ModelResponse:
        filename = model_file or self._default_model
        if filename not in self.available:
            return ModelResponse(
                text="", provider="local", model=filename,
                error=f"Model {filename} not found. Available: {self.available}"
            )

        model = self._load(filename)
        if model is None:
            return ModelResponse(
                text="", provider="local", model=filename,
                error=f"Failed to load {filename}"
            )

        import time
        start = time.time()
        try:
            full_prompt = f"<|system|>\n{system_prompt}\n<|user|>\n{prompt}\n<|assistant|>\n"
            text = model(full_prompt, stop=["<|user|>", "<|system|>"])
            latency = int((time.time() - start) * 1000)
            return ModelResponse(
                text=text.strip(), provider="local", model=filename, latency_ms=latency
            )
        except Exception as e:
            return ModelResponse(
                text="", provider="local", model=filename, error=str(e)
            )


class CloudModelProvider:
    """Provider for cloud APIs (OpenAI-compatible: Kimi, OpenRouter, Gemini, etc.)."""

    def __init__(self):
        self.api_key = os.getenv("KUERA_CLOUD_API_KEY", "")
        self.base_url = os.getenv("KUERA_CLOUD_BASE_URL", "https://api.moonshot.cn/v1")
        self.model = os.getenv("KUERA_CLOUD_MODEL", "kimi-k2-5")
        self.enabled = bool(self.api_key)
        if not self.enabled:
            logger.warning("[Cloud] No API key configured. Set KUERA_CLOUD_API_KEY env var.")

    def generate(self, prompt: str, system_prompt: str = "") -> ModelResponse:
        if not self.enabled:
            return ModelResponse(
                text="", provider="cloud", model=self.model,
                error="Cloud provider not configured. Set KUERA_CLOUD_API_KEY."
            )

        import time
        import openai
        start = time.time()
        try:
            client = openai.OpenAI(api_key=self.api_key, base_url=self.base_url)
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            resp = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
                max_tokens=2048,
            )
            latency = int((time.time() - start) * 1000)
            return ModelResponse(
                text=resp.choices[0].message.content.strip(),
                provider="cloud",
                model=self.model,
                tokens_used=resp.usage.total_tokens if resp.usage else None,
                latency_ms=latency,
            )
        except Exception as e:
            return ModelResponse(
                text="", provider="cloud", model=self.model, error=str(e)
            )


class ModelRouter:
    """Routes generation requests to local or cloud based on task."""

    def __init__(self):
        self.local = LocalModelProvider()
        self.cloud = CloudModelProvider()

    def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        provider: Optional[str] = None,  # "local", "cloud", or None (auto)
        task_complexity: str = "auto",   # "low", "medium", "high", "auto"
        model_file: str = None,
    ) -> ModelResponse:
        """Generate text with automatic or manual provider selection."""

        # Determine provider
        if provider is None:
            provider = self._select_provider(prompt, task_complexity)

        # Route
        if provider == "cloud":
            return self.cloud.generate(prompt, system_prompt)
        else:
            return self.local.generate(prompt, system_prompt, model_file)

    def _select_provider(self, prompt: str, complexity: str) -> str:
        """Heuristic to choose local vs cloud."""
        if complexity == "high":
            return "cloud" if self.cloud.enabled else "local"
        if complexity == "low":
            return "local"

        # Auto: use cloud for complex keywords, else local
        complex_indicators = [
            "analisis mendalam", "deep analysis", "multi-step",
            "reasoning", "compare and contrast", "synthesize",
            "generate finding", "draft laporan", "evaluasi komprehensif",
            "identify patterns", "root cause", "recommend",
        ]
        prompt_lower = prompt.lower()
        is_complex = any(k in prompt_lower for k in complex_indicators)

        if is_complex and self.cloud.enabled:
            return "cloud"
        return "local"

    def explain_audit_result(
        self,
        audit_summary: Dict,
        jenis: str = "keuangan",
        provider: Optional[str] = None,
    ) -> ModelResponse:
        """Generate natural-language explanation of audit findings."""
        system_prompt = (
            "Kamu adalah auditor senior BPKP. Tugasmu menulis finding draft "
            "berdasarkan hasil analisis data. Gunakan bahasa Indonesia formal. "
            "Fokus pada: (1) apa yang ditemukan, (2) implikasinya, (3) rekomendasi."
        )
        prompt = self._build_audit_prompt(audit_summary, jenis)
        return self.generate(prompt, system_prompt, provider=provider, task_complexity="high")

    def _build_audit_prompt(self, summary: Dict, jenis: str) -> str:
        if jenis == "keuangan":
            return (
                f"Berikut hasil analisis keuangan BUMD:\n"
                f"- Total BUMD: {summary.get('total_bumd', 'N/A')}\n"
                f"- ROA Rendah (<5%): {summary.get('roa_rendah', 'N/A')}\n"
                f"- Underperforming: {summary.get('underperforming', 'N/A')}\n"
                f"- Anomaly Flags: {summary.get('anomaly_flags', 'N/A')}\n"
                f"\nTulis finding draft dalam bahasa Indonesia formal. "
                f"Sertakan: (1) kondisi, (2) kriteria, (3) sebab, (4) akibat, (5) rekomendasi."
            )
        elif jenis == "spi":
            return (
                f"Berikut hasil evaluasi SPI (COSO Framework):\n"
                f"- Nilai Total: {summary.get('nilai_total', 'N/A')}/5.00\n"
                f"- Kategori: {summary.get('kategori', 'N/A')}\n"
                f"- Rekomendasi: {summary.get('rekomendasi_count', 'N/A')} items\n"
                f"\nTulis finding draft untuk kelemahan pengendalian internal."
            )
        elif jenis == "kinerja":
            return (
                f"Berikut hasil audit kinerja:\n"
                f"- Tahun: {summary.get('tahun', 'N/A')}\n"
                f"- Total Entitas: {summary.get('total_entitas', 'N/A')}\n"
                f"- Predikat: {json.dumps(summary.get('predikat_distribution', {}))}\n"
                f"\nTulis finding draft untuk entitas dengan predikat D/E."
            )
        return json.dumps(summary, ensure_ascii=False, indent=2)
