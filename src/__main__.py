"""
Main entry point for Patent Novelty Analyzer.
"""

from src.cli import PatentAnalyzerCLI
from src.utils.config import ConfigLoader


def main():
    """Main entry point."""
    # Load configuration
    config = ConfigLoader()
    
    # Initialize CLI
    cli = PatentAnalyzerCLI(config)
    
    # Run CLI
    cli.run()


if __name__ == "__main__":
    main()
