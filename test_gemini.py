#!/usr/bin/env python3
"""
Simple test to check if the Gemini model name is correct
"""
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_gemini_models():
    """Test available Gemini models"""
    try:
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        
        print("🔍 Available Gemini models:")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"  - {m.name}")
        
        print("\n🔍 Testing gemini-1.5-flash...")
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Hello, test message")
        print(f"✅ gemini-1.5-flash works: {response.text[:100]}...")
        
        print("\n🔍 Testing gemini-2.5-flash...")
        try:
            model2 = genai.GenerativeModel('gemini-2.5-flash')
            response2 = model2.generate_content("Hello, test message")
            print(f"✅ gemini-2.5-flash works: {response2.text[:100]}...")
        except Exception as e:
            print(f"❌ gemini-2.5-flash failed: {e}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_gemini_models()