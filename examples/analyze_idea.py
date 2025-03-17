#!/usr/bin/env python3
"""
Example script demonstrating how to use the Patent Novelty Analyzer programmatically.
"""

import sys
import os

# Add the parent directory to the path so we can import the src package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.config import ConfigLoader
from src.cli import PatentAnalyzerCLI


def main():
    """Main function."""
    # Load configuration
    config = ConfigLoader()
    
    # Initialize CLI
    cli = PatentAnalyzerCLI(config)
    
    # Example 1: Analyze an idea with provided keywords
    print("\n=== Example 1: Analyze with provided keywords ===")
    cli.analyze(
        idea="A smart umbrella that predicts rain and automatically opens when needed",
        keywords="umbrella, smart, rain, prediction, automatic",
        verbose=True
    )
    
    # Example 2: Analyze an idea from a file
    print("\n=== Example 2: Analyze from file ===")
    cli.analyze(
        idea_file="examples/smart_umbrella.txt",
        keywords="umbrella, weather prediction, machine learning, automatic, sensors",
        verbose=True
    )
    
    # Example 3: Analyze an idea with automatic keyword extraction (requires Ollama)
    print("\n=== Example 3: Analyze with automatic keyword extraction ===")
    try:
        cli.analyze(
            idea="A device that translates dog barks into human language using AI",
            verbose=True
        )
    except Exception as e:
        print(f"Error: {str(e)}")
        print("Note: This example requires Ollama to be running with the llama2 model.")


if __name__ == "__main__":
    main() 