#!/usr/bin/env python3
\"\"\"Agentic Personal AI Assistant
Features: ReAct Planning, Tool Use, CoT Reasoning, Personalization, Multi-turn Memory
Integrates: LLM Serving, Web Enricher, Safety Guard\"\"\"

import json
import requests
from typing import List, Dict, Any
from pathlib import Path
import redis
from datetime import datetime
from personal_ai.safety_guard import SafetyGuard
from personal_ai.personal_assistant_final import analyze_behavior  # Legacy
from models.model_loader import load_model

r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
safety = SafetyGuard()
LLM_URL = "http://localhost:8001"  # deployment/llm_serving

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
        """ReAct planning: Thought → Action → Observation"""
        cot_prompt = f"Goal: {goal}\nProfile: {json.dumps(self.profile)}\nPlan step-by-step."
        return self._call_llm(cot_prompt)

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
        """ReAct agent loop"""
        thought = self.plan(goal)
        observation = ""
        
        for step in range(max_steps):
            prompt = f"Step {step+1}\nGoal: {goal}\nThought: {thought}\nObservation: {observation}\nAction?"
            action = self._call_llm(prompt)
            
            # Parse action (simplified)
            if "tool" in action and "(" in action:
                tool_name = action.split("(")[0].split()[-1]
                args_str = action.split("(")[1].split(")")[0]
                args = json.loads(args_str) if args_str.startswith("{") else {"input": args_str}
                obs = self.call_tool(tool_name, args)
                observation += f"Tool {tool_name}: {json.dumps(obs)}\n"
            else:
                break
        
        final = self._call_llm(f"Goal: {goal}\nObservations: {observation}\nFinal Answer:")
        return safety.guard_response(goal, final)

    def chat(self, message: str) -> str:
        self.memory.append({"role": "user", "content": message, "time": datetime.now().isoformat()})
        
        # Multi-turn CoT
        history = self.memory[-8:]  # Context window
        prompt = f"User profile: {json.dumps(self.profile)}\n" + \
                 "\n".join([f"{m[&#x27;role&#x27;]}: {m[&#x27;content&#x27;]}" for m in history]) + \
                 "\nAssistant (CoT): Think step-by-step then respond."
        
        response = self._call_llm(prompt)
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
            return "LLM service unavailable."

if __name__ == &#x27;__main__&#x27;:
    agent = AgentAssistant("demo_user")
    print("🤖 Agent Assistant Ready!")
    print("Test: agent.chat(&#x27;Plan my day&#x27;) or agent.react_loop(&#x27;Research AI trends&#x27;)")
    
    # Demo
    print("\n=== Multi-turn Chat ===")
    print(agent.chat("Hi, analyze my work pattern."))
    print(agent.chat("Suggest optimizations with CoT."))
    
    print("\n=== Agentic Planning ===")
    result = agent.react_loop("Find latest AI papers on agentic systems")
    print(result)

