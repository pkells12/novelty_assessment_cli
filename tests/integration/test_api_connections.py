#!/usr/bin/env python3
"""
Script to test API connections for Patent Novelty Analyzer.
"""

import os
import sys
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_anthropic_api():
    """Test connection to Anthropic API (Claude)."""
    print("\nTesting Anthropic API connection...")
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not found in environment variables.")
        return False
    
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        
        # Make a simple API call
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=10,
            messages=[{"role": "user", "content": "Hello"}]
        )
        
        print("✓ Successfully connected to Anthropic API.")
        return True
    except Exception as e:
        print(f"✗ Error connecting to Anthropic API: {str(e)}")
        return False

def test_serpapi():
    """Test connection to SerpApi (Google Patents)."""
    print("\nTesting SerpApi connection...")
    api_key = os.environ.get("SERPAPI_API_KEY")
    
    if not api_key:
        print("Error: SERPAPI_API_KEY not found in environment variables.")
        return False
    
    try:
        from serpapi import GoogleSearch
        
        # Make a simple API call
        params = {
            "engine": "google_patents",
            "q": "smart umbrella",
            "api_key": api_key
        }
        
        search = GoogleSearch(params)
        results = search.get_dict()
        
        if "error" in results:
            print(f"✗ SerpApi error: {results['error']}")
            return False
        
        print("✓ Successfully connected to SerpApi.")
        return True
    except Exception as e:
        print(f"✗ Error connecting to SerpApi: {str(e)}")
        return False

def test_brave_search_api():
    """Test connection to Brave Search API."""
    print("\nTesting Brave Search API connection...")
    api_key = os.environ.get("BRAVE_API_KEY")
    
    if not api_key:
        print("Error: BRAVE_API_KEY not found in environment variables.")
        return False
    
    try:
        headers = {
            "Accept": "application/json",
            "X-Subscription-Token": api_key
        }
        
        response = requests.get(
            "https://api.search.brave.com/res/v1/web/search",
            headers=headers,
            params={"q": "smart umbrella", "count": 1}
        )
        
        if response.status_code == 200:
            print("✓ Successfully connected to Brave Search API.")
            return True
        else:
            print(f"✗ Brave Search API error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"✗ Error connecting to Brave Search API: {str(e)}")
        return False

def test_ollama():
    """Test connection to Ollama."""
    print("\nTesting Ollama connection...")
    
    try:
        response = requests.get("http://localhost:11434/api/tags")
        
        if response.status_code == 200:
            models = response.json()
            llama2_found = any(model["name"] == "llama2:latest" for model in models.get("models", []))
            
            if llama2_found:
                print("✓ Successfully connected to Ollama with llama2 model available.")
                return True
            else:
                print("✗ Connected to Ollama but llama2:latest model not found.")
                return False
        else:
            print(f"✗ Ollama API error: {response.status_code} - {response.text}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Could not connect to Ollama. Is it running?")
        return False
    except Exception as e:
        print(f"✗ Error connecting to Ollama: {str(e)}")
        return False

def main():
    """Main function."""
    print("Testing API connections for Patent Novelty Analyzer...")
    
    results = {
        "Anthropic": test_anthropic_api(),
        "SerpApi": test_serpapi(),
        "Brave Search": test_brave_search_api(),
        "Ollama": test_ollama()
    }
    
    print("\n=== Summary ===")
    
    all_successful = True
    for name, success in results.items():
        status = "✓ CONNECTED" if success else "✗ FAILED"
        print(f"{name}: {status}")
        all_successful = all_successful and success
    
    return 0 if all_successful else 1

if __name__ == "__main__":
    sys.exit(main()) 