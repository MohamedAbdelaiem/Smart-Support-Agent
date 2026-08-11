import time
from groq import Groq,RateLimitError,APITimeoutError,APIConnectionError,InternalServerError,APIError
from dotenv import load_dotenv

load_dotenv()
client = Groq()

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
    model = kwargs.pop("model", "llama-3.1-8b-instant")
    
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

    return call_with_retries(
        lambda: client.chat.completions.create(
            model=model,
            messages=formatted_messages,
            max_tokens=1000,
            **kwargs
        )
    )
    
def generate_stream(system, messages,**kwargs):
    model = kwargs.pop("model", "llama-3.1-8b-instant")
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
        lambda: client.chat.completions.create(
            model=model,
            messages=formatted_messages,
            max_tokens=1000,
            stream=True,
            **kwargs
        )
    )

    for chunk in response:
        content = chunk.choices[0].delta.content
        if content:
            yield content
        
    

    