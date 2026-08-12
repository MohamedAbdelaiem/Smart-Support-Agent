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


def call_with_retries (fn,max_retries = 3,retry_delay = 1):
    for attempt in range(max_retries):
        try: 
            return fn()
        except RateLimitError:
            time.sleep(retry_delay * (2 ** attempt))
        except (APITimeoutError,APIConnectionError,InternalServerError) as e:
            if attempt == max_retries-1:
                raise e
            time.sleep(retry_delay)
    raise RuntimeError("Max retries exceeded")

def generate(system, messages, **kwargs):
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
        # If system role is already present in messages list, don't duplicate it
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
    response = call_with_retries(
        lambda: active_client.chat.completions.create(
            model=model,
            messages=cast(Any, formatted_messages),
            max_tokens=1000,
            **kwargs
        )
    )

    latency_ms = (time.perf_counter() - start_time)*1000

    input_tokens = response.usage.prompt_tokens if response.usage else 0
    output_tokens = response.usage.completion_tokens if response.usage else 0

    log_request(
        provider=provider,
        model=model,
        latency_ms=latency_ms,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        tool_calls = [tc.function.name for tc in response.choices[0].message.tool_calls] if response.choices[0].message.tool_calls else None
    )

    return response
    
def generate_stream(system, messages,**kwargs):
    model = str(kwargs.pop("model", "llama-3.3-70b-versatile"))
    if isinstance(messages, str):
        formatted_messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": messages}
        ]
    else:
        formatted_messages = [
            {"role": "system", "content": system},
            *messages
        ]
    
    response= call_with_retries(
        lambda: groq_client.chat.completions.create(
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
        
    

    