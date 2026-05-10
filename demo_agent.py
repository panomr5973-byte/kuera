#!/usr/bin/env python3
"""Demo Agentic Capabilities: Multi-turn, Tools, Planning, Personalization"""

from personal_ai.agent_assistant import AgentAssistant
from evaluation.eval_agent import AgentEval
import time

print("🚀 Agentic AI Demo - Full Capabilities Showcase")
print("Requires: uvicorn deployment.llm_serving:app --port 8001 (running)")

# 1. Personalization Demo
print("\n1️⃣ PERSONALIZATION")
agent_dev = AgentAssistant("developer_user")
agent_dev.profile = {"role": "AI Engineer", "focus": "LLM agents"}
print(agent_dev.chat("Suggest weekly learning plan"))

agent_mgr = AgentAssistant("manager_user")
agent_mgr.profile = {"role": "Product Manager", "focus": "team productivity"}
print(agent_mgr.chat("Suggest weekly learning plan"))

# 2. Multi-turn Reasoning Demo
print("\n2️⃣ MULTI-TURN CoT")
agent = AgentAssistant("demo")
print("Turn 1:", agent.chat("What is agentic AI?"))
print("Turn 2 (CoT):", agent.chat("Explain with examples and future implications"))
print("Turn 3:", agent.chat("How can I implement ReAct?"))

# 3. Tool Use + Planning Demo
print("\n3️⃣ AGENTIC PLANNING + TOOLS")
goal = "Research latest Indonesian AI regulations and summarize key points"
print("🧠 Planning...")
plan = agent.plan(goal)
print(f"Plan: {plan}")

print("\n🤖 Executing ReAct loop...")
result = agent.react_loop(goal)
print(f"✅ Result: {result}")

# 4. Run Agent Evals
print("\n4️⃣ EVALUATION SUITE")
evaler = AgentEval("microsoft/Phi-3-mini-4k-instruct")
results = evaler.run_agent_suite("evaluation/demo_agent_results.json")

print("\n🎉 AGENTIC SYSTEM READY!")
print("\nProduction endpoints:")
print("- Chat: POST /v1/chat/completions")
print("- Agent: personal_ai/agent_assistant.py")
print("- Serving: http://localhost:8001")
print("- Eval: python evaluation/eval_agent.py")

print("\n🚀 Quick Start Commands:")
print("uvicorn deployment.llm_serving:app --port 8001")
print("python personal_ai/agent_assistant.py")
print("python demo_agent.py")

