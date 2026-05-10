#!/usr/bin/env python3
\"\"\"Agent-Specific Evaluation: Tool Use, Planning, Multi-turn, Personalization
Extends eval_benchmarks.py\"\"\"

import json
from typing import Dict, List
from evaluation.eval_benchmarks import EvalBenchmarks, ChatResponse
from personal_ai.agent_assistant import AgentAssistant
import time
from datasets import load_dataset

class AgentEval(EvalBenchmarks):
    def __init__(self, model_path: str):
        super().__init__(model_path)
        self.agent = AgentAssistant("eval_user")

    def tool_use_eval(self, num_samples: int = 20) -> Dict[str, float]:
        """Test tool calling accuracy"""
        tests = [
            {"goal": "Search latest AI news", "expected_tool": "web_search"},
            {"goal": "Calculate 2**10", "expected_tool": "code_exec"},
        ] * (num_samples // 2)
        
        correct = 0
        for test in tests:
            result = self.agent.react_loop(test["goal"])
            if test["expected_tool"] in result:
                correct += 1
        
        return {"tool_accuracy": correct / num_samples}

    def planning_eval(self, num_samples: int = 20) -> Dict[str, float]:
        """Planning success rate"""
        dataset = load_dataset("json", data_files="data/agent_planning_tests.json")  # Create this
        success = 0
        
        for ex in dataset["train"].select(range(num_samples)):
            plan = self.agent.plan(ex["goal"])
            if any(step in plan for step in ex["gold_plan"]):
                success += 1
        
        return {"planning_success": success / num_samples}

    def multi_turn_eval(self, num_convos: int = 10) -> Dict[str, float]:
        """Multi-turn coherence"""
        coherence_score = 0
        
        for _ in range(num_convos):
            agent = AgentAssistant("temp")
            prev = ""
            score = 0
            
            for turn in range(5):  # 5-turn convo
                msg = f"Follow-up {turn}: tell more"
                resp = agent.chat(msg)
                if prev.lower() in resp.lower():  # Coherence check
                    score += 1
                prev = resp
            
            coherence_score += score / 5
        
        return {"coherence": coherence_score / num_convos}

    def personalization_eval(self) -> Dict[str, float]:
        """Adapts to user profile"""
        # Mock profiles
        profiles = [{"role": "developer"}, {"role": "manager"}]
        adaptation_score = 0
        
        for prof in profiles:
            agent = AgentAssistant("prof")
            agent.profile = prof
            agent.save_profile(prof)
            
            resp = agent.chat("Suggest productivity tips")
            if prof["role"] in resp.lower():
                adaptation_score += 1
        
        return {"adaptation_rate": adaptation_score / len(profiles)}

    def run_agent_suite(self, output_path: str):
        results = {
            "tool_use": self.tool_use_eval(),
            "planning": self.planning_eval(),
            "multi_turn": self.multi_turn_eval(),
            "personalization": self.personalization_eval()
        }
        
        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)
        
        print("🧪 Agent Eval Results:", json.dumps(results, indent=2))
        return results

if __name__ == "__main__":
    evals = AgentEval("microsoft/Phi-3-mini-4k-instruct")
    evals.run_agent_suite("evaluation/agent_results.json")

