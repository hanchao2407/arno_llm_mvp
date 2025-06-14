import requests
import json

CHROMA_BASE_URL = "https://arno-llm-mvp.onrender.com"
HEARTBEAT_ENDPOINT = f"{CHROMA_BASE_URL}/api/v1/heartbeat"

try:
    print(f"Attempting direct HTTP GET to: {HEARTBEAT_ENDPOINT}")
    response = requests.get(HEARTBEAT_ENDPOINT)
    response.raise_for_status()
    heartbeat_data = response.json()

    print("✅ Successfully received response from ChromaDB")
    print("Heartbeat response:", heartbeat_data)

except requests.exceptions.ConnectionError as e:
    print(f"❌ Connection error: Could not reach {CHROMA_BASE_URL}.")
    print(f"Error details: {e}")
except requests.exceptions.Timeout as e:
    print(f"❌ Timeout error: Request to {CHROMA_BASE_URL} timed out.")
    print(f"Error details: {e}")
except requests.exceptions.RequestException as e:
    print(f"❌ An error occurred with the request to {CHROMA_BASE_URL}: {e}")
    print(f"Response status code: {response.status_code if 'response' in locals() else 'N/A'}")
    print(f"Response text: {response.text if 'response' in locals() else 'N/A'}")
except json.JSONDecodeError as e:
    print(f"❌ Failed to decode JSON response from {CHROMA_BASE_URL}. The server might not be returning valid JSON.")
    print(f"Error details: {e}")
    print(f"Response text: {response.text if 'response' in locals() else 'N/A'}")
except Exception as e:
    print(f"❌ An unexpected error occurred: {e}")