"""List available Gemini models"""
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    api_key = input("Enter your Google API key: ")

genai.configure(api_key=api_key)

print("\n📋 Available Gemini Models:\n")
for model in genai.list_models():
    if "generateContent" in model.supported_generation_methods:
        print(f"✅ {model.name}")
        print(f"   Display Name: {model.display_name}")
        print(f"   Methods: {model.supported_generation_methods}")
        print()
