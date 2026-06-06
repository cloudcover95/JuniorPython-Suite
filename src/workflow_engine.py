# path: src/workflow_engine.py

"""
WorkflowEngine

Composable workflow system with BitNet augmentation and UI support.
"""

from typing import Any, Callable, Dict, List


class WorkflowStep:
    def __init__(self, name: str, func: Callable, bitnet_runner=None):
        self.name = name
        self.func = func
        self.bitnet_runner = bitnet_runner

    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        if self.bitnet_runner:
            bitnet_context = self.bitnet_runner.run_inference(inputs)
            return self.func(bitnet_context)
        return self.func(inputs)


class WorkflowEngine:
    def __init__(self, bitnet_runner=None):
        self.steps: List[WorkflowStep] = []
        self.bitnet_runner = bitnet_runner
        self.results: List[Dict] = []

    def add_step(self, name: str, func: Callable):
        self.steps.append(WorkflowStep(name, func, self.bitnet_runner))

    def run_workflow(self, initial_inputs: Dict[str, Any]) -> List[Dict]:
        current = initial_inputs
        self.results = []
        for step in self.steps:
            result = step.run(current)
            self.results.append({"step": step.name, "result": result})
            current = result
        return self.results

    def get_ui_state(self) -> Dict[str, Any]:
        return {
            "steps": [s.name for s in self.steps],
            "results": self.results
        }
