from src.observability import log_request
import time
from typing import Any, cast
from groq import Groq,RateLimitError,APITimeoutError,APIConnectionError,InternalServerError,APIError
from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv()   
groq_client = Groq()
openrouter_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY"),
)


def call_with_retries(fn, max_retries=3, retry_delay=2):
    last_exception = None
    for attempt in range(max_retries):
        try:
            return fn()
        except RateLimitError as e:
            last_exception = e
            time.sleep(retry_delay * (2 ** attempt))
        except (APITimeoutError, APIConnectionError, InternalServerError, APIError) as e:
            last_exception = e
            if attempt == max_retries - 1:
                raise e
            time.sleep(retry_delay)
        except Exception as e:
            last_exception = e
            raise e
    if last_exception:
        raise last_exception
    raise RuntimeError("Max retries exceeded")


def generate(system, messages, **kwargs):
    provider = str(kwargs.pop("provider", "groq")).lower()
    if provider == "openrouter":
        active_client = openrouter_client
        model = str(kwargs.pop("model", "meta-llama/llama-3.3-70b-instruct"))
    else:
        active_client = groq_client
        model = str(kwargs.pop("model", "llama-3.3-70b-versatile"))

    if isinstance(messages, str):
        formatted_messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": messages}
        ]
    else:
        if messages and messages[0].get("role") == "system":
            formatted_messages = messages
        else:
            formatted_messages = [
                {"role": "system", "content": system},
                *messages
            ]

    if "tools" in kwargs and "tool_choice" not in kwargs:
        kwargs["tool_choice"] = "auto"

    start_time = time.perf_counter()
    try:
        response = call_with_retries(
            lambda: active_client.chat.completions.create(
                model=model,
                messages=cast(Any, formatted_messages),
                max_tokens=1000,
                **kwargs
            )
        )
    except Exception as e:
        # Automatic fallback to OpenRouter if Groq fails or rate-limits
        if provider == "groq" and os.environ.get("OPENROUTER_API_KEY"):
            print(f"Groq primary call failed ({e}). Falling back to OpenRouter...")
            response = call_with_retries(
                lambda: openrouter_client.chat.completions.create(
                    model="meta-llama/llama-3.3-70b-instruct",
                    messages=cast(Any, formatted_messages),
                    max_tokens=1000,
                    **kwargs
                )
            )
        else:
            raise e

    latency_ms = (time.perf_counter() - start_time) * 1000

    input_tokens = response.usage.prompt_tokens if response.usage else 0
    output_tokens = response.usage.completion_tokens if response.usage else 0

    log_request(
        provider=provider,
        model=model,
        latency_ms=latency_ms,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        tool_calls=[tc.function.name for tc in response.choices[0].message.tool_calls] if response.choices[0].message.tool_calls else None
    )

    return response
    
def generate_stream(system, messages, **kwargs):
    provider = str(kwargs.pop("provider", "groq")).lower()
    if provider == "openrouter":
        active_client = openrouter_client
        model = str(kwargs.pop("model", "qwen/qwen3-32b"))
    else:
        active_client = groq_client
        model = str(kwargs.pop("model", "llama-3.3-70b-versatile"))

    if isinstance(messages, str):
        formatted_messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": messages}
        ]
    else:
        if messages and messages[0].get("role") == "system":
            formatted_messages = messages
        else:
            formatted_messages = [
                {"role": "system", "content": system},
                *messages
            ]

    response = call_with_retries(
        lambda: active_client.chat.completions.create(
            model=model,
            messages=cast(Any, formatted_messages),
            max_tokens=1000,
            stream=True,
            **kwargs
        )
    )

    for chunk in response:
        content = chunk.choices[0].delta.content
        if content:
            yield content
        
    

    