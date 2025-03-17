"""
Command Line Interface for Patent Novelty Analyzer.
"""

import os
import sys
import click
import json
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from src.utils.error_handler import handle_exceptions, InputValidationError, APIConnectionError
from src.keyword_extractor import OllamaClient, KeywordExtractor
from src.patent_searcher import PatentSearcher, SerpApiClient
from src.web_searcher import WebSearcher, BraveSearchClient
from src.novelty_analyzer import NoveltyAnalyzer, ClaudeClient


class PatentAnalyzerCLI:
    """Command Line Interface for Patent Novelty Analyzer."""
    
    def __init__(self, config):
        """Initialize the CLI.
        
        Args:
            config: Configuration object.
        """
        self.config = config
        self.console = Console()
        
        # Initialize components
        self.ollama_client = OllamaClient(config)
        self.keyword_extractor = KeywordExtractor(config, self.ollama_client)
        
        # Initialize patent search and novelty analysis components
        self.patent_searcher = PatentSearcher(config, SerpApiClient(config))
        self.web_searcher = WebSearcher(config, BraveSearchClient(config))
        self.novelty_analyzer = NoveltyAnalyzer(config, ClaudeClient(config))
        
        # Check if Ollama is available
        self.ollama_available = self.ollama_client.is_available()
        if not self.ollama_available:
            self.console.print("[yellow]Warning: Ollama is not available. Keyword extraction will use fallback method.[/yellow]")
    
    @handle_exceptions
    def run(self):
        """Run the CLI."""
        # Initialize Click CLI
        cli = click.Group()
        
        @cli.command("analyze")
        @click.argument("idea", required=False)
        @click.option("--idea-file", "-f", type=click.Path(exists=True), help="Load idea from file.")
        @click.option("--output-file", "-o", type=click.Path(), help="Save results to file.")
        @click.option(
            "--analysis-type", "-t",
            type=click.Choice(["simple", "complex"]),
            default="simple",
            help="Type of analysis to perform."
        )
        @click.option(
            "--format",
            type=click.Choice(["text", "markdown", "json"]),
            default="text",
            help="Output format."
        )
        @click.option("--keywords", "-k", help="Comma-separated keywords to use for search.")
        @click.option("--verbose", "-v", is_flag=True, help="Enable verbose output.")
        @click.option("--quiet", "-q", is_flag=True, help="Suppress non-error output.")
        def analyze_command(idea, idea_file, output_file, analysis_type, format, keywords, verbose, quiet):
            """Analyze a patent idea for novelty."""
            return self.analyze(
                idea=idea,
                idea_file=idea_file,
                output_file=output_file,
                analysis_type=analysis_type,
                output_format=format,
                keywords=keywords,
                verbose=verbose,
                quiet=quiet
            )
        
        @cli.command("interactive")
        def interactive_command():
            """Run in interactive mode."""
            return self.interactive()
        
        # Run the CLI
        cli(obj={})
    
    def _perform_analysis(self, idea, keywords, analysis_type="simple", output_format="text", verbose=False):
        """Perform the patent novelty analysis.
        
        Args:
            idea (str): The idea to analyze.
            keywords (list or str): The keywords to use for searching.
            analysis_type (str): Type of analysis to perform ("simple" or "complex").
            output_format (str): Output format ("text", "markdown", or "json").
            verbose (bool): Whether to show verbose output.
            
        Returns:
            str: Analysis results.
        """
        # Convert keywords to list if it's a string
        if isinstance(keywords, str):
            keywords = [kw.strip() for kw in keywords.split(",") if kw.strip()]
        
        # Search for patents
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]Searching for patents..."),
            transient=True,
            disable=not verbose
        ) as progress:
            progress.start()
            patents = self.patent_searcher.search_patents(keywords)
            progress.stop()
        
        if verbose:
            self.console.print(f"Found {len(patents)} relevant patents.")
        
        # Search for existing products/services
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]Searching for existing products/services..."),
            transient=True,
            disable=not verbose
        ) as progress:
            progress.start()
            web_results = self.web_searcher.search_web(keywords)
            progress.stop()
        
        if verbose:
            self.console.print(f"Found {len(web_results)} relevant products/services.")
        
        # Format search results for analysis
        formatted_patents = self.patent_searcher.format_patent_results(patents)
        formatted_web_results = self.web_searcher.format_web_results(web_results)
        
        # Generate novelty analysis
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]Generating novelty analysis..."),
            transient=True,
            disable=not verbose
        ) as progress:
            progress.start()
            
            if analysis_type == "complex":
                analysis = self.novelty_analyzer.generate_complex_analysis(
                    idea, formatted_patents, formatted_web_results, output_format
                )
                formatted_analysis = self.novelty_analyzer.format_complex_analysis(
                    analysis, output_format
                )
            else:
                analysis = self.novelty_analyzer.generate_simple_analysis(
                    idea, formatted_patents, formatted_web_results, output_format
                )
                formatted_analysis = self.novelty_analyzer.format_simple_analysis(
                    analysis, output_format
                )
                
            progress.stop()
        
        if output_format == "json":
            return json.dumps(formatted_analysis, indent=2)
        else:
            return formatted_analysis
    
    def analyze(self, idea=None, idea_file=None, keywords=None, analysis_type="simple", 
                output_format="text", output_file=None, verbose=False):
        """Analyze a patent idea.
        
        Args:
            idea (str, optional): The idea to analyze.
            idea_file (str, optional): Path to a file containing the idea.
            keywords (str, optional): Comma-separated keywords to use for searching.
            analysis_type (str): Type of analysis to perform ("simple" or "complex").
            output_format (str): Output format ("text", "markdown", or "json").
            output_file (str, optional): Path to save the analysis to.
            verbose (bool): Whether to show verbose output.
            
        Returns:
            str: Analysis results.
        """
        # Get the idea text
        idea_text = self._get_idea_text(idea, idea_file)
        
        self.console.print("Analyzing patent idea")
        self.console.print(f"{idea_text[:100]}{'...' if len(idea_text) > 100 else ''}")
        
        # Extract keywords if not provided
        if not keywords:
            with Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]Extracting keywords..."),
                transient=True,
                disable=not verbose
            ) as progress:
                progress.start()
                extracted_keywords = self.keyword_extractor.extract_keywords(idea_text)
                progress.stop()
            
            keywords = extracted_keywords
        
        self.console.print(f"Extracted keywords: {keywords}")
        
        # Perform analysis
        try:
            analysis = self._perform_analysis(
                idea_text, 
                keywords, 
                analysis_type, 
                output_format, 
                verbose
            )
            
            # Save to file if requested
            if output_file:
                Path(output_file).write_text(analysis)
                self.console.print(f"Analysis saved to {output_file}")
            
            return analysis
        except Exception as e:
            self.console.print(f"[red]Error during analysis: {str(e)}[/red]")
            return "Analysis failed."
    
    def interactive(self):
        """Run in interactive mode.
        
        Returns:
            int: Exit code.
        """
        self.console.print("[bold blue]Patent Novelty Analyzer - Interactive Mode[/bold blue]")
        
        # Check if Ollama is available
        if not self.ollama_available:
            self.console.print("[yellow]Warning: Ollama is not available. Keyword extraction will use fallback method.[/yellow]")
        
        # Get idea text
        idea_text = click.prompt("Enter your patent idea")
        
        # Extract keywords
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                progress.add_task("Extracting keywords...", total=None)
                extracted_keywords = self._extract_keywords(idea_text)
            
            # Show extracted keywords
            self.console.print(f"[bold green]Extracted keywords:[/bold green] {', '.join(extracted_keywords)}")
            
            # Allow user to edit keywords
            if click.confirm("Would you like to edit the keywords?", default=False):
                edited_keywords = click.prompt(
                    "Enter comma-separated keywords",
                    default=", ".join(extracted_keywords)
                )
                keywords = [k.strip() for k in edited_keywords.split(",")]
            else:
                keywords = extracted_keywords
            
            # Show final keywords
            self.console.print(f"[bold green]Final keywords:[/bold green] {', '.join(keywords)}")
            
            # TODO: Implement these steps in Phase 3-5
            # 2. Search for patents (Phase 3)
            # 3. Search for existing products (Phase 4)
            # 4. Analyze novelty (Phase 5)
            
            # Placeholder for now
            self.console.print("[yellow]Patent search and novelty analysis not yet implemented.[/yellow]")
            
        except APIConnectionError as e:
            self.console.print(f"[bold red]Error:[/bold red] {str(e)}")
            return 1
        
        return 0
    
    def _get_idea_text(self, idea, idea_file):
        """Get idea text from argument or file.
        
        Args:
            idea (str, optional): Idea text from argument.
            idea_file (str, optional): Path to file containing idea.
        
        Returns:
            str: Idea text.
        """
        if idea:
            return idea
        
        if idea_file:
            try:
                with open(idea_file, 'r') as f:
                    return f.read()
            except Exception as e:
                raise InputValidationError(f"Error reading idea file: {str(e)}")
        
        return None
    
    def _extract_keywords(self, idea_text, keywords=None):
        """Extract keywords from idea text.
        
        Args:
            idea_text (str): The idea text.
            keywords (str, optional): Comma-separated keywords to use instead of extraction.
        
        Returns:
            list: The extracted keywords.
        """
        # If keywords are provided, use them
        if keywords:
            return [k.strip() for k in keywords.split(",")]
        
        # If Ollama is not available, use fallback method
        if not self.ollama_available:
            return self._extract_keywords_fallback(idea_text)
        
        # Otherwise, extract keywords using Ollama
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                progress.add_task("Extracting keywords...", total=None)
                return self.keyword_extractor.extract_keywords(idea_text)
        except APIConnectionError as e:
            self.console.print(f"[bold red]Error extracting keywords:[/bold red] {str(e)}")
            self.console.print("[yellow]Using default keywords based on idea text.[/yellow]")
            return self._extract_keywords_fallback(idea_text)
    
    def _extract_keywords_fallback(self, idea_text):
        """Extract keywords from idea text using a simple fallback method.
        
        Args:
            idea_text (str): The idea text.
        
        Returns:
            list: The extracted keywords.
        """
        # Simple fallback: just use words from the idea text
        words = idea_text.lower().split()
        words = [w for w in words if len(w) > 3 and w not in {"and", "the", "that", "with", "from", "this", "for"}]
        return words[:5]  # Return up to 5 words
