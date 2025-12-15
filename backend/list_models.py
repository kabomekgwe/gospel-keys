
import google.generativeai as genai
import os
from app.core.config import settings

if settings.google_api_key:
    genai.configure(api_key=settings.google_api_key)
    try:
        print("Listing available models:")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"- {m.name}")
    except Exception as e:
        print(f"Error listing models: {e}")
else:
    print("No Google API Key found")
