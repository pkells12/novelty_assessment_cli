"""
Main entry point for Patent Novelty Analyzer.
"""

from .cli import PatentAnalyzerCLI
from .utils.config import ConfigLoader


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
