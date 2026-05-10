#!/usr/bin/env python3
\"\"\"Agentic Personal AI Assistant with Nusantara Spirit
Features: ReAct Planning, Tool Use, CoT Reasoning, Personalization, Multi-turn Memory
Integrates: LLM Serving Nusantara, Safety Guard Nusantara\"\"\"

import json
import requests
from typing import List, Dict, Any
from pathlib import Path
import redis
from datetime import datetime
from personal_ai.safety_guard_nusantara import SafetyGuard
from personal_ai.personal_assistant_final import analyze_behavior  # Legacy
from models.model_loader import load_model

r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
safety = SafetyGuard()
LLM_URL = "http://localhost:8001"  # deployment/llm_serving_nusantara recommended

class AgentAssistant:
    def __init__(self, user_id: str = "default"):
        self.user_id = user_id
        self.memory = self.load_memory()
        self.profile = self.load_profile()
        self.tools = [
            {"name": "web_search", "description": "Search web for info"},
            {"name": "code_exec", "description": "Execute Python code safely"},
            {"name": "behavior_analyze", "description": "Analyze user behavior"}
        ]

    def load_memory(self) -> List[Dict]:
        mem = r.get(f"memory:{self.user_id}")
        return json.loads(mem) if mem else []

    def save_memory(self):
        r.setex(f"memory:{self.user_id}", 86400, json.dumps(self.memory[-100:]))  # Last 100 turns

    def load_profile(self) -> Dict:
        prof = r.get(f"profile:{self.user_id}")
        if not prof:
            prof = analyze_behavior()  # From legacy
            self.save_profile(prof)
        return json.loads(prof)

    def save_profile(self, profile: Dict):
        r.setex(f"profile:{self.user_id}", 86400*7, json.dumps(profile))  # 1 week

    def plan(self, goal: str) -> str:
        \"\"\"ReAct planning: Thought → Action → Observation - Yuk kita rencanakan bareng!\"\"\"
        cot_prompt = f"Goal: {goal}\nProfile: {json.dumps(self.profile)}\nPlan step-by-step yuk."
        injected_prompt = safety.inject_system_prompt(cot_prompt)
        return self._call_llm(injected_prompt)

    def call_tool(self, tool_name: str, args: Dict) -> Dict:
        if tool_name == "web_search":
            resp = requests.post(f"{LLM_URL}/tools/web_search", json={"query": args["query"]})
            return resp.json()
        elif tool_name == "code_exec":
            resp = requests.post(f"{LLM_URL}/tools/code_exec", json={"code": args["code"]})
            return resp.json()
        elif tool_name == "behavior_analyze":
            return analyze_behavior()
        return {"error": "Unknown tool"}

    def react_loop(self, goal: str, max_steps: int = 5) -> str:
        \"\"\"ReAct agent loop with Nusantara gotong royong\"\"\"
        thought = self.plan(goal)
        observation = ""
        
        for step in range(max_steps):
            prompt = f"Step {step+1}\nGoal: {goal}\nThought: {thought}\nObservation: {observation}\nAction yuk bareng?"
            injected_prompt = safety.inject_system_prompt(prompt)
            action = self._call_llm(injected_prompt)
            
            # Parse action (simplified)
            if "tool" in action and "(" in action:
                tool_name = action.split("(")[0].split()[-1]
                args_str = action.split("(")[1].split(")")[0]
                args = json.loads(args_str) if args_str.startswith("{") else {"input": args_str}
                obs = self.call_tool(tool_name, args)
                observation += f"Tool {tool_name}: {json.dumps(obs)}\n"
            else:
                break
        
        final_prompt = f"Goal: {goal}\nObservations: {observation}\nFinal Answer yuk!"
        injected_final = safety.inject_system_prompt(final_prompt)
        final = self._call_llm(injected_final)
        return safety.guard_response(goal, final)

    def chat(self, message: str) -> str:
        self.memory.append({"role": "user", "content": message, "time": datetime.now().isoformat()})
        
        # Multi-turn CoT with Nusantara
        history = self.memory[-8:]  # Context window
        prompt = f"User profile: {json.dumps(self.profile)}\n" + \
                 "\n".join([f"{m['role']}: {m['content']}" for m in history]) + \
                 "\nAssistant (CoT Nusantara): Think step-by-step then respond yuk bareng."
        
        injected_prompt = safety.inject_system_prompt(prompt)
        response = self._call_llm(injected_prompt)
        safe_resp = safety.guard_response(message, response)
        
        self.memory.append({"role": "assistant", "content": safe_resp})
        self.save_memory()
        
        # Update profile
        self.profile["last_interaction"] = message
        self.save_profile(self.profile)
        
        return safe_resp

    def _call_llm(self, prompt: str) -> str:
        try:
            resp = requests.post(f"{LLM_URL}/v1/chat/completions", json={
                "messages": [{"role": "user", "content": prompt}],
                "user_id": self.user_id,
                "tools": self.tools
            })
            return resp.json()["choices"][0]["message"]["content"]
        except:
            return "Layanan LLM sedang tidak tersedia, Kak. Mari coba lagi nanti ya!"

if __name__ == '__main__':
    agent = AgentAssistant("demo_user")
    print("🤖 Agent Assistant Nusantara Ready! Salam dari tanah air!")
    print("Test: agent.chat('Plan my day yuk') or agent.react_loop('Research AI trends bareng')")
    
    # Demo
    print("\\n=== Multi-turn Chat Nusantara ===")
    print(agent.chat("Halo Kak, analisis pola kerja saya dong."))
    print(agent.chat("Sarankan optimasi dengan CoT yuk!"))
    
    print("\\n=== Agentic Planning Gotong Royong ===")
    result = agent.react_loop("Cari paper AI terbaru tentang agentic systems yuk")
    print(result)
