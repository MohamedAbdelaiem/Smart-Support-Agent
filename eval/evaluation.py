import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from langsmith import Client, evaluate
from eval.config import DATASET_NAME
from eval.dataset import ensure_dataset
from eval.evaluators import grounding_trap_evaluator
from src.agent import run_agent
from src.prompts.prompts import PROMPT_V1, PROMPT_V2, PROMPT_V3


def create_predict_fn(prompt_version: str = "v3", provider: str = "openrouter"):
    if prompt_version == "v3":
        prompt = PROMPT_V3
    elif prompt_version == "v2":
        prompt = PROMPT_V2
    else:
        prompt = PROMPT_V1

    def predict(inputs: dict) -> dict:
        return run_agent(inputs["input"], prompt, [], provider=provider)

    return predict


def run_evaluation(prompt_version: str = "v3", provider: str = "openrouter"):
    """Runs evaluation experiment for specified prompt version and provider."""
    client = Client()
    ensure_dataset(client)
    predict_fn = create_predict_fn(prompt_version=prompt_version, provider=provider)
    print(f"\n Running LangSmith Evaluation Experiment for Prompt={prompt_version.upper()}, Provider={provider.upper()}...")
    
    return evaluate(
        predict_fn,
        data=DATASET_NAME,
        evaluators=[grounding_trap_evaluator],
        experiment_prefix=f"agent-{prompt_version}-{provider}-eval",
    )


if __name__ == "__main__":
    run_evaluation(prompt_version="v2", provider="openrouter")
