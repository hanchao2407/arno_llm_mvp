# llm.py

import requests
import os
from dotenv import load_dotenv

load_dotenv()  # Loads .env file

def call_llm(messages: list[dict]) -> str:
    """
    Calls the Together API for Llama 3 with a list of chat messages.
    Returns the model's response as a string.
    """
    api_key = os.getenv("TOGETHER_API_KEY")
    if not api_key:
        raise ValueError("TOGETHER_API_KEY not found in environment.")

    url = "https://api.together.xyz/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "meta-llama/Llama-3-70b-chat-hf",
        "messages": messages,
        "max_tokens": 2048,
        "temperature": 0.2,
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except requests.RequestException as e:
        raise RuntimeError(f"LLM API call failed: {e}")
