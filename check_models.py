import os
import requests
import json

# Try to get key from env, but handle if it's not there
api_key = os.environ.get("GOOGLE_API_KEY")

if not api_key:
    print("Warning: GOOGLE_API_KEY not found in environment.")
    print("Please make sure you have exported your API key.")
    exit(1)

print(f"Using API Key: {api_key[:5]}...{api_key[-5:] if len(api_key)>10 else ''}")

url = f"https://generativelanguage.googleapis.com/v1/models?key={api_key}"

print(f"Querying: {url.replace(api_key, 'HIDDEN_KEY')}")

try:
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        models = data.get('models', [])
        print(f"Found {len(models)} models:")
        for m in models:
            print(f"- {m.get('name')} | Supported methods: {m.get('supportedGenerationMethods')}")
            if 'gemini' in m.get('name', ''):
                print(f"  -> Description: {m.get('description')}")
    else:
        print(f"Error {response.status_code}: {response.text}")

except Exception as e:
    print(f"Connection Exception: {e}")
