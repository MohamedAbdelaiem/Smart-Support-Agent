from unittest.mock import MagicMock, patch
import pytest
from groq import APITimeoutError, RateLimitError
from src.client import call_with_retries, generate,generate_stream


def test_call_with_retries_success():
    """Test that call_with_retries returns immediately when the call succeeds."""
    mock_fn = MagicMock(return_value="success")
    result = call_with_retries(mock_fn, max_retries=3, retry_delay=0.01)
    assert result == "success"
    assert mock_fn.call_count == 1


@patch("time.sleep")
def test_call_with_retries_rate_limit_retry(mock_sleep):
    """Test that RateLimitError triggers exponential backoff sleep and retries."""
    mock_fn = MagicMock(
        side_effect=[
            RateLimitError("Rate limit exceeded", response=MagicMock(), body=None),
            RateLimitError("Rate limit exceeded", response=MagicMock(), body=None),
            "success_after_retries",
        ]
    )
    result = call_with_retries(mock_fn, max_retries=3, retry_delay=0.1)
    assert result == "success_after_retries"
    assert mock_fn.call_count == 3
    assert mock_sleep.call_count == 2
    mock_sleep.assert_any_call(0.1)
    mock_sleep.assert_any_call(0.2)


@patch("time.sleep")
def test_call_with_retries_timeout_exhaustion(mock_sleep):
    """Test that APITimeoutError retries up to max_retries and raises on final attempt."""
    mock_fn = MagicMock(
        side_effect=APITimeoutError(request=MagicMock())
    )
    with pytest.raises(APITimeoutError):
        call_with_retries(mock_fn, max_retries=3, retry_delay=0.01)
    assert mock_fn.call_count == 3


@patch("src.client.groq_client.chat.completions.create")
def test_generate_string_message(mock_create):
    """Test generate function correctly formats system and user messages."""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="Hello!", tool_calls=None))]
    mock_response.usage.prompt_tokens = 10
    mock_response.usage.completion_tokens = 5
    mock_create.return_value = mock_response

    res = generate(system="System prompt", messages="User question")
    assert res == mock_response
    mock_create.assert_called_once_with(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "System prompt"},
            {"role": "user", "content": "User question"},
        ],
        max_tokens=1000,
    )

@patch('src.client.groq_client.chat.completions.create')
def test_generate_stream_String_messages(mock_create):
    """Test generate function correctly formats system and user messages for streaming."""
    mock_chunk = MagicMock()
    mock_chunk.choices = [MagicMock(delta=MagicMock(content="Hello!"))]
    mock_create.return_value = [mock_chunk]

    res = list(generate_stream("System prompt", "User question"))
    print(res)
    assert res == ['Hello!']
    mock_create.assert_called_once_with(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "System prompt"},
            {"role": "user", "content": "User question"},
        ],
        max_tokens=1000,
        stream=True,
    )


    
