import requests
from django.conf import settings
import json

OPENROUTER_API_KEY = settings.OPENROUTER_API_KEY

def analyze_response(text):
    url = "https://openrouter.ai/api/v1/analyze" 
    headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}"}
    data=json.dumps({
    "model": "deepseek/deepseek-chat-v3-0324:free",
    "messages": [
      {
        "role": "user",
        "task": "sentiment-analysis",
        "content": text
      }
    ],
    
  })
    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code == 200:
        return response.json().get("category", "unknown")
    
    return "error"
