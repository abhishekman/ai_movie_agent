import requests

from config import OPENROUTER_API_KEY


def ask_llm(messages):
    """
    Send conversation messages to OpenRouter
    and return the AI response.
    """

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "model": "openrouter/free",
        "messages": messages
    }

    response = requests.post(
        url,
        headers=headers,
        json=data,
        timeout=30
    )

    response.raise_for_status()

    result = response.json()

    return result["choices"][0]["message"]["content"]