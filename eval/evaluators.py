from eval.config import UNCERTAINTY_PHRASES


def grounding_trap_evaluator(run, example):
    """Evaluates whether the agent avoids inventing fake policies on grounding trap cases (brittle keyword backup)."""
    is_trap = example.outputs.get("grounding_trap", False)
    if not is_trap:
        return {"key": "grounding_pass", "score": 1.0}

    # Extract response text
    response_text = ""
    if run.outputs:
        response_text = str(run.outputs.get("message", "")).lower().replace("’", "'")

    passed = any(phrase in response_text for phrase in UNCERTAINTY_PHRASES)
    return {"key": "grounding_pass", "score": 1.0 if passed else 0.0}
