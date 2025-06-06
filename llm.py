# llm.py

import requests
import os
from dotenv import load_dotenv

load_dotenv()  # loads .env file

def call_llm(messages) -> str:
    """
    Calls the Together API for Llama-3 with the given prompt.
    Returns the model's answer as a string.
    """
    api_key = os.getenv("TOGETHER_API_KEY")
    url = "https://api.together.xyz/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "meta-llama/Llama-3-70b-chat-hf",
        "messages": messages,
        "max_tokens": 512,
        "temperature": 0.2
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]
