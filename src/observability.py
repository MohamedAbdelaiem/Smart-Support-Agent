import json
import uuid

def log_request(
    provider: str,
    model: str,
    latency_ms: float,
    input_tokens: int,
    output_tokens: int,
    tool_calls: list[str] | None = None,
    error: str | None = None,
    prompt_version: str = "v1",
) -> dict:
    """Logs structured JSON request details for observability and log analysis."""
    log_data = {
        "request_id": str(uuid.uuid4()),
        "provider": provider,
        "model": model,
        "prompt_version": prompt_version,
        "latency_ms": round(latency_ms, 2),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "tool_calls": tool_calls or [],
        "error": error,
    }
    # Write raw json log to local log file for analysis
    with open("request_logs.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(log_data) + "\n")

    # Clean, easy-on-the-eyes console log output
    tools_str = f" | Tools: {', '.join(tool_calls)}" if tool_calls else ""
    print(f"📊 [LOG] Latency: {round(latency_ms)}ms | Tokens: {input_tokens}in/{output_tokens}out{tools_str}")

    return log_data
