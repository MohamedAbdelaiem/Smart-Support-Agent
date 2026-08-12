import json
from eval.config import UNCERTAINTY_PHRASES
from langsmith.schemas import Run, Example
from langsmith.evaluation import run_evaluator


def grounding_trap_evaluator(run: Run, example: Example):
    """Evaluates whether the agent avoids inventing fake policies on grounding trap cases (brittle keyword backup)."""
    outputs = example.outputs or {}
    is_trap = outputs.get("grounding_trap", False)
    if not is_trap:
        return {"key": "grounding_pass", "score": 1.0}

    # Extract response text
    response_text = ""
    if run.outputs:
        response_text = str(run.outputs.get("message", "")).lower().replace("’", "'")

    passed = any(phrase in response_text for phrase in UNCERTAINTY_PHRASES)
    return {"key": "grounding_pass", "score": 1.0 if passed else 0.0}


def tool_call_verifier(run: Run, example: Example, expected_tool: str | None = None):
    # 1. Look at the expected tool call in the example inputs or outputs safely
    outputs = example.outputs or {}
    target_tool = expected_tool or outputs.get("expected_tool")
    if not target_tool or str(target_tool).lower() == "none":
        return {"key": "tool_call_pass", "score": 1.0}

    # 2. Extract tool calls from agent run outputs
    run_outputs = run.outputs or {}
    tool_calls = list(run_outputs.get("tool_calls", []))

    # 3. Fallback to child runs if tool_calls wasn't in run_outputs directly
    if not tool_calls and hasattr(run, "child_runs") and run.child_runs:
        for child in run.child_runs:
            if getattr(child, "name", "") == "Execute Tool":
                child_inputs = getattr(child, "inputs", {}) or {}
                if "name" in child_inputs:
                    tool_calls.append(child_inputs["name"])

    # 4. Check if expected target_tool was called
    passed = any(
        (tc.get("name") == target_tool if isinstance(tc, dict) else str(tc) == target_tool)
        for tc in tool_calls
    )
    return {"key": "tool_call_pass", "score": 1.0 if passed else 0.0}

