from pathlib import Path

# Dataset configuration
DATASET_NAME = "smart-support-eval-set"
TEST_CASES_FILE = Path(__file__).resolve().parent.parent / "data" / "test_cases.json"

# Evaluation phrases for grounding check
UNCERTAINTY_PHRASES = [
    "don't have",
    "do not have",
    "not certain",
    "cannot confirm",
    "unclear",
    "no information",
    "don't possess",
    "unable to confirm",
    "do not possess",
]
