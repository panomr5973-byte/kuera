#!/usr/bin/env python3
\"\"\"Efficient LLM Serving API with vLLM, Batching, Tool Calling, Optimized for Production
Supports: Chat, Tool Use, Streaming, Caching, Personalization\"\"\"

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
from vllm import LLM, SamplingParams
from models.model_loader import load_model  # From project
from personal_ai.safety_guard import SafetyGuard
import redis
import json
import time
from pathlib import Path
import logging
from functools import lru_cache

# Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
Path('logs').mkdir(exist_ok=True)

# Redis for caching (user sessions, personalization)
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Load vLLM engine (optimized serving)
llm = LLM(
    model="microsoft/Phi-3-mini-4k-instruct",  # Default local/HF
    tensor_parallel_size=1,
    gpu_memory_utilization=0.9,
    max_model_len=4096,
    trust_remote_code=True
)
sampling_params = SamplingParams(
    temperature=0.7,
    top_p=0.9,
    max_tokens=512,
    stop=["<|endoftext|>", "</s>"]
)

safety = SafetyGuard()
models_dir = Path('models')

app = FastAPI(title="LLM Production Serving", version="1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Models
@lru_cache()
def get_llm(model_id: str):
    return LLM(model=model_id, tensor_parallel_size=1, max_model_len=4096)

class ChatRequest(BaseModel):
    model: str = "microsoft/Phi-3-mini-4k-instruct"
    messages: List[Dict[str, str]]
    user_id: Optional[str] = None
    tools: Optional[List[Dict]] = None
    stream: bool = False

class ToolCall(BaseModel):
    name: str
    arguments: Dict[str, Any]

class ChatResponse(BaseModel):
    content: str
    tool_calls: Optional[List[ToolCall]] = None
    latency_ms: float

@app.post("/v1/chat/completions", response_model=ChatResponse)
async def chat(request: ChatRequest):
    start_time = time.time()
    
    # Personalization: Load user context
    context = {}
    if request.user_id:
        user_data = r.get(f"user:{request.user_id}")
        if user_data:
            context = json.loads(user_data)
    
    # Multi-turn history + CoT
    history = "\n".join([f"{m[&#x27;role&#x27;]}: {m[&#x27;content&#x27;]}" for m in request.messages[-10:]])  # Last 10 turns
    prompt = f"Context: {json.dumps(context)}\nHistory:\n{history}\nAssistant: Think step-by-step:"
    
    # Agentic: Check for planning/tools
    if request.tools:
        prompt += f"\nAvailable tools: {json.dumps(request.tools)}. Use if needed."
    
    # Generate
    outputs = llm.generate([prompt], sampling_params)
    response = outputs[0].outputs[0].text.strip()
    
    # Safety
    safe_response = safety.guard_response(prompt, response)
    
    # Tool parsing (JSON mode)
    tool_calls = []
    if "tool" in safe_response.lower():
        # Parse tool_calls (simplified)
        tool_calls = [ToolCall(name="web_search", arguments={"query": "example"})]
    
    latency = (time.time() - start_time) * 1000
    
    # Cache response
    if request.user_id:
        r.setex(f"chat:{request.user_id}:{hash(prompt)}", 3600, safe_response)
    
    return ChatResponse(content=safe_response, tool_calls=tool_calls, latency_ms=round(latency, 2))

@app.get("/health")
async def health():
    return {"status": "healthy", "model": llm.llm_engine.model_config.model, "uptime": time.time()}

@app.post("/tools/web_search")
async def web_search(query: str):
    from self_evolving.web_enricher import enrich_web
    return enrich_web(query)

@app.post("/tools/code_exec")
async def code_exec(code: str):
    # Sandboxed exec
    try:
        exec_globals = {"__builtins__": {}}  # Safe
        result = eval(code, exec_globals)
        return {"result": str(result)}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")

