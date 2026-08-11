# Smart Support Agent — Evaluation Report

> **Dataset:** smart-support-eval-set - 25 tickets - Provider: OpenRouter (qwen/qwen3-32b)

---

## Results Summary

| Prompt | Grounding Pass | Correctness (LLM Judge) | Avg Latency |
|:---|:---:|:---:|:---:|
| V1 (baseline) | 92.0% | N/A | 4.19s |
| V2 (guardrails) | 96.0% | 60.0% (20/25 scored) | 5.44s |
| **V3 (elite)** | **100.0%** | **75.0%** (20/25 scored) | 7.19s |

> 5/25 rows per run have no correctness score — LangSmith judge runs asynchronously and the CSV was exported before all scores arrived.

All runs: **0 errors**, **100% tool execution success**.

---

## What Changed Each Version

| Version | Change | Result |
|:---|:---|:---:|
| V1 | Baseline one-liner | 92% / N/A |
| V2 | Grounding guardrail + tool-use rule | 96% / 60% |
| V3 | Billing routing + no-contact-detail rule | 100% / 75% |

---

## Key Failures Found & Fixed

- **V1:** Invented sales@acmecorp.com on a referral query. Asked for order ID on a policy question.
- **V2:** Invented support@acmecorp.com + 1-800-ACME-HELP on warranty/account queries.
- **V3:** Zero keyword failures. LLM judge still flags ~25% — mostly billing routing edge cases.

---

## Verdict

| Dimension | Best | Note |
|:---|:---:|:---|
| Grounding Accuracy | V3 | 100% pass, 0 hallucinations |
| LLM Judge Score | V3 | 75% vs 60% for V2 |
| Latency | V1 | 4.19s vs 7.19s (V3 is 72% slower) |
| Production-ready | **V3** | Only version with zero keyword failures |

**Deploy V3. For latency: switch to Groq or meta-llama/llama-3.3-70b-instruct:free on OpenRouter.**

---

## Reproduce

`ash
uv run python eval/evaluation.py
`

LangSmith: prompt-engineering-app -> smart-support-eval-set
