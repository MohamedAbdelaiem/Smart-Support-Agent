import json
import sys
from pathlib import Path

# Add project root directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from langsmith import Client, evaluate
# pyrefly: ignore [missing-import]
from src.agent import run_agent

# 1. Initialize LangSmith Client
client = Client()

# 2. Upload dataset if not already present in LangSmith
DATASET_NAME = "smart-support-eval-set"
TEST_CASES_FILE = Path(__file__).resolve().parent.parent / "data" / "test_cases.json"

if not client.has_dataset(dataset_name=DATASET_NAME):
    print(f"Uploading {TEST_CASES_FILE.name} to LangSmith dataset '{DATASET_NAME}'...")
    dataset = client.create_dataset(
        dataset_name=DATASET_NAME,
        description="25 gold-standard evaluation cases for Smart Support Agent including grounding traps."
    )
    with open(TEST_CASES_FILE, "r", encoding="utf-8") as f:
        test_cases = json.load(f)
    
    for case in test_cases:
        client.create_example(
            inputs={"input": case["input"]},
            outputs={
                "expected_label": case["expected_label"],
                "expected_tool": case["expected_tool"],
                "expected_behavior": case["expected_behavior"],
                "grounding_trap": case["grounding_trap"],
            },
            dataset_id=dataset.id,
        )
    print("Dataset uploaded successfully!")

# 3. System Prompt Versions
PROMPT_V1 = "You are a customer support agent for Acme Corp. Be helpful and accurate."

PROMPT_V2 = """
You are a helpful, professional customer support agent for Acme Corp.

Rules:
1. Always use available tools (lookup_order, refund_check) when customers inquire about order details or refunds.
2. Grounding Guardrail: If asked about shipping policies, warranty extensions, or custom discounts not explicitly provided in tool outputs or known context, explicitly state that you do not have that information. Do NOT invent policies.
3. Be concise, direct, and polite.
"""

PROMPT_V3 = """
Role:
You are the elite customer support specialist for Acme Corp. Your tone is professional, direct, concise, and helpful. You must assist customers using ONLY verified facts and tools.

Rules & Guardrails:

1. Tool Usage — Order/Refund Specifics:
   If the customer references a SPECIFIC order and asks about its status or refund eligibility, use the appropriate tool (lookup_order or refund_check). Do NOT ask for an order ID if the question is general.

2. General Policy Inquiries (CRITICAL — No tools, no order ID):
   If the customer asks about store-wide policies (e.g., shipping destinations, international returns, warranty extensions, custom discounts, referral bonuses, loyalty tiers), do NOT ask for an order ID or use any tool.
   Immediately state clearly that you do not have access to general policy information and cannot confirm it.

3. Billing & Account Questions (CRITICAL — No tools, no order ID):
   If the customer is asking about a payment failure, billing issue, account charge, or subscription concern — this is a BILLING category question.
   Acknowledge the issue directly and let them know it will be handled by the billing team. Do NOT ask for an order ID or run a tool lookup. Route and respond directly.

4. No Hallucinations:
   Do NOT invent email addresses, phone numbers, discount percentages, warranty terms, or return windows. If you don't have the data, say so cleanly.

5. Response Format: Be brief and polite. Avoid unnecessary filler text.
"""

# 4. Target Prediction Functions for Evaluation
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

# 5. Evaluators
def grounding_trap_evaluator(run, example):
    """Evaluates whether the agent avoids inventing fake policies on grounding trap cases (brittle keyword backup)."""
    is_trap = example.outputs.get("grounding_trap", False)
    if not is_trap:
        return {"key": "grounding_pass", "score": 1.0}

    # Extract response text
    response_text = ""
    if run.outputs:
        response_text = str(run.outputs.get("message", "")).lower().replace("’", "'")

    uncertainty_phrases = [
        "don't have", "do not have", "not certain", "cannot confirm", 
        "unclear", "no information", "don't possess", "unable to confirm",
        "do not possess"
    ]
    passed = any(phrase in response_text for phrase in uncertainty_phrases)
    return {"key": "grounding_pass", "score": 1.0 if passed else 0.0}

def run_evaluation(prompt_version: str = "v3", provider: str = "openrouter"):
    """Runs evaluation experiment for specified prompt version and provider."""
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
