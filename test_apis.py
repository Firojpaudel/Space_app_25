#!/usr/bin/env python3
"""
Test script to verify all free API connections are working correctly.
Run this before starting the application to ensure everything is set up properly.
"""

import os
import sys
from pathlib import Path
import asyncio
from typing import Dict, Any

# Add project root to path
sys.path.append(str(Path(__file__).parent))

def test_environment_variables() -> Dict[str, Any]:
    """Test that all required environment variables are set."""
    print("🔍 Testing environment variables...")
    
    required_vars = {
        'GEMINI_API_KEY': 'Google Gemini API key',
        'PINECONE_API_KEY': 'Pinecone API key', 
        'PINECONE_ENVIRONMENT': 'Pinecone environment'
    }
    
    optional_vars = {
        'NASA_API_KEY': 'NASA API key (optional)',
        'OPENAI_API_KEY': 'OpenAI API key (optional)'
    }
    
    results = {}
    
    # Check required variables
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            results[var] = f"✅ {description}: Set (length: {len(value)})"
        else:
            results[var] = f"❌ {description}: Missing - Required!"
    
    # Check optional variables
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value:
            results[var] = f"✅ {description}: Set (length: {len(value)})"
        else:
            results[var] = f"⚠️ {description}: Not set (optional)"
    
    return results

def test_gemini_api() -> Dict[str, Any]:
    """Test Google Gemini API connection."""
    print("🤖 Testing Gemini API...")
    
    try:
        import google.generativeai as genai
        
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            return {"status": "❌", "message": "GEMINI_API_KEY not set"}
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Test with a simple query
        response = model.generate_content("Hello, respond with just 'API Working'")
        
        if response and response.text:
            return {
                "status": "✅", 
                "message": f"Gemini API working - Response: {response.text[:50]}..."
            }
        else:
            return {"status": "❌", "message": "No response from Gemini API"}
            
    except ImportError:
        return {"status": "❌", "message": "google-generativeai not installed"}
    except Exception as e:
        return {"status": "❌", "message": f"Gemini API error: {str(e)[:100]}"}

def test_pinecone_api() -> Dict[str, Any]:
    """Test Pinecone API connection."""
    print("📌 Testing Pinecone API...")
    
    try:
        from pinecone import Pinecone
        
        api_key = os.getenv('PINECONE_API_KEY')
        if not api_key:
            return {"status": "❌", "message": "PINECONE_API_KEY not set"}
        
        pc = Pinecone(api_key=api_key)
        
        # List indexes to test connection
        indexes = pc.list_indexes()
        
        return {
            "status": "✅", 
            "message": f"Pinecone API working - Found {len(indexes)} indexes"
        }
        
    except ImportError:
        return {"status": "❌", "message": "pinecone-client not installed"}
    except Exception as e:
        return {"status": "❌", "message": f"Pinecone API error: {str(e)[:100]}"}

def test_nasa_api() -> Dict[str, Any]:
    """Test NASA API connection (optional)."""
    print("🚀 Testing NASA API...")
    
    try:
        import requests
        
        api_key = os.getenv('NASA_API_KEY', 'DEMO_KEY')
        
        # Test with APOD endpoint
        url = f"https://api.nasa.gov/planetary/apod?api_key={api_key}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            return {"status": "✅", "message": "NASA API working"}
        else:
            return {"status": "⚠️", "message": f"NASA API returned status {response.status_code}"}
            
    except ImportError:
        return {"status": "❌", "message": "requests not installed"}
    except Exception as e:
        return {"status": "⚠️", "message": f"NASA API error (optional): {str(e)[:100]}"}

def test_dependencies() -> Dict[str, Any]:
    """Test that all required dependencies are installed."""
    print("📦 Testing dependencies...")
    
    required_packages = [
        'streamlit',
        'pandas', 
        'numpy',
        'plotly',
        'langchain',
        'google.generativeai',
        'pinecone'
    ]
    
    results = {}
    
    for package in required_packages:
        try:
            if package == 'google.generativeai':
                import google.generativeai
                results[package] = "✅ Installed"
            else:
                __import__(package)
                results[package] = "✅ Installed"
        except ImportError:
            results[package] = "❌ Missing - Run: pip install -r requirements.txt"
    
    return results

def main():
    """Run all tests and display results."""
    print("🧪 K-OSMOS API & Dependency Test Suite")
    print("=" * 50)
    
    # Load .env file if it exists
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Loaded .env file")
    except ImportError:
        print("⚠️ python-dotenv not installed - environment variables must be set manually")
    except Exception as e:
        print(f"⚠️ Could not load .env file: {e}")
    
    print()
    
    # Test environment variables
    env_results = test_environment_variables()
    for var, result in env_results.items():
        print(f"  {result}")
    print()
    
    # Test dependencies
    dep_results = test_dependencies()
    print("📦 Dependencies:")
    for package, result in dep_results.items():
        print(f"  {result} - {package}")
    print()
    
    # Test APIs
    print("🌐 API Connections:")
    
    # Test Gemini
    gemini_result = test_gemini_api()
    print(f"  {gemini_result['status']} Gemini API: {gemini_result['message']}")
    
    # Test Pinecone
    pinecone_result = test_pinecone_api()
    print(f"  {pinecone_result['status']} Pinecone API: {pinecone_result['message']}")
    
    # Test NASA (optional)
    nasa_result = test_nasa_api()
    print(f"  {nasa_result['status']} NASA API: {nasa_result['message']}")
    
    print()
    print("=" * 50)
    
    # Summary
    critical_errors = []
    if "❌" in gemini_result['status']:
        critical_errors.append("Gemini API")
    if "❌" in pinecone_result['status']:
        critical_errors.append("Pinecone API")
    
    missing_deps = [pkg for pkg, result in dep_results.items() if "❌" in result]
    if missing_deps:
        critical_errors.extend(missing_deps)
    
    if critical_errors:
        print(f"❌ CRITICAL ISSUES FOUND: {', '.join(critical_errors)}")
        print("   Please fix these issues before running the application.")
        return False
    else:
        print("✅ ALL TESTS PASSED! Ready to run K-OSMOS.")
        print("\n🚀 To start the application:")
        print("   python main.py dashboard")
        print("   # or")
        print("   streamlit run kosmos_app.py")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)