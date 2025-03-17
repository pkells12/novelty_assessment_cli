#!/usr/bin/env python3
"""
Test end-to-end functionality of the Patent Novelty Analyzer.
"""

import os
import sys
from dotenv import load_dotenv
from novelty_assessment_cli.utils.config import ConfigLoader
from novelty_assessment_cli.keyword_extractor import KeywordExtractor, OllamaClient
from novelty_assessment_cli.novelty_analyzer import ClaudeClient, NoveltyAnalyzer

# Load environment variables
load_dotenv()

def main():
    """Test the entire workflow."""
    print("\nTesting Patent Novelty Analyzer end-to-end workflow...")
    
    # Load configuration
    try:
        print("\nLoading configuration...")
        config = ConfigLoader()
        print("✓ Configuration loaded successfully.")
    except Exception as e:
        print(f"✗ Error loading configuration: {str(e)}")
        return False
    
    # Test keyword extraction
    try:
        print("\nTesting keyword extraction...")
        # Create Ollama client first
        ollama_client = OllamaClient(config)
        keyword_extractor = KeywordExtractor(config, ollama_client)
        
        # Sample patent idea
        patent_idea = """
        A smart umbrella that can predict rain using local weather data and remind the owner 
        to take it when leaving the house. It includes LED lights for visibility at night, 
        a location tracker to prevent losing it, and USB charging ports in the handle.
        """
        
        keywords = keyword_extractor.extract_keywords(patent_idea)
        
        if keywords and len(keywords) > 0:
            print(f"✓ Successfully extracted keywords: {', '.join(keywords)}")
        else:
            print("✗ Failed to extract keywords.")
            return False
    except Exception as e:
        print(f"✗ Error during keyword extraction: {str(e)}")
        return False
    
    # Test Claude API directly
    try:
        print("\nTesting Claude API directly...")
        claude_client = ClaudeClient(config)
        
        sample_prompt = "Briefly describe the concept of novelty in patent law in one sentence."
        system_prompt = "You are a patent law expert. Provide concise and accurate information about patent law concepts."
        
        response = claude_client.generate_analysis(sample_prompt, system_prompt)
        
        if response and len(response) > 0:
            print(f"✓ Claude API response received: {response[:100]}...")
            print("\nEnd-to-end test completed successfully!")
            return True
        else:
            print("✗ Empty response from Claude API.")
            return False
    except Exception as e:
        print(f"✗ Error using Claude API: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 