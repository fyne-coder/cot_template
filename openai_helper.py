import os
import openai
from typing import List, Dict, Any

# Load API key from environment
_API_KEY = os.getenv("OPENAI_API_KEY")
if not _API_KEY:
    raise RuntimeError(
        "Environment variable OPENAI_API_KEY not set."
    )

# Initialize client
openai_client = openai.OpenAI(api_key=_API_KEY)

# Default model and temperature (override via env vars)
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1")
DEFAULT_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.3"))


def chat_completion(
    messages: List[Dict[str, str]],
    model: str | None = None,
    temperature: float | None = None,
) -> str:
    """Call the Chat Completions API and return the assistant content."""
    response = openai_client.chat.completions.create(
        model=model or DEFAULT_MODEL,
        messages=messages,
        temperature=temperature or DEFAULT_TEMPERATURE,
        response_format={"type": "json_object"},
    )
    return response.choices[0].message.content