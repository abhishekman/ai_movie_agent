import requests
from config import OPENROUTER_API_KEY


url = "https://openrouter.ai/api/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
}

data = {
    "model": "openrouter/free",
    "messages": [
        {
            "role": "user",
            "content": "Hello! Give me one short sentence about movies."
        }
    ]
}

response = requests.post(
    url,
    headers=headers,
    json=data,
    timeout=30
)

print("Status:", response.status_code)
print(response.json())