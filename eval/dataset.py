import json
from langsmith import Client
from eval.config import DATASET_NAME, TEST_CASES_FILE


def ensure_dataset(client: Client):
    """Upload dataset if not already present in LangSmith."""
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
                inputs={"input": case["ticket_text"]},
                outputs={
                    "expected_behavior": case["expected_behavior"],
                    "expected_order_id": case["expected_order_id"],
                    "expected_status": case["expected_status"],
                    "expected_label": case["expected_label"],
                    "must_contain": case["must_contain"],
                    "must_not_contain": case["must_not_contain"],
                },
                dataset_id=dataset.id,
    )

        print("Dataset uploaded successfully!")
