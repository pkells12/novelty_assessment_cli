"""
Novelty analysis using Claude API.
"""

import os
import json
import requests
from requests.exceptions import RequestException
from typing import List, Dict, Any, Optional
import time
from tenacity import retry, stop_after_attempt, wait_exponential

from novelty_assessment_cli.utils.error_handler import APIConnectionError, APIAuthenticationError


class ClaudeClient:
    """Client for Claude API."""
    
    def __init__(self, config):
        """Initialize the ClaudeClient.
        
        Args:
            config: Configuration object.
        """
        self.api_key = config.get("api_keys.anthropic")
        self.model = config.get("claude.model")
        self.temperature = config.get("claude.temperature")
        self.max_tokens = config.get("claude.max_tokens")
        self.timeout = config.get("claude.timeout")
    
    def validate_credentials(self):
        """Validate API key.
        
        Returns:
            bool: True if credentials are valid.
            
        Raises:
            APIAuthenticationError: If credentials are invalid.
        """
        if not self.api_key:
            raise APIAuthenticationError("Claude API key not found.")
        
        return True
    
    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=5, min=5, max=20),
        reraise=True
    )
    def generate_analysis(self, user_prompt, system_prompt=None):
        """Generate analysis using Claude API.
        
        Args:
            user_prompt (str): The user prompt to send to Claude.
            system_prompt (str, optional): System prompt for Claude.
            
        Returns:
            str: The generated analysis.
            
        Raises:
            APIConnectionError: If there is an error connecting to the API.
            APIAuthenticationError: If credentials are invalid.
        """
        try:
            self.validate_credentials()
            
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)
            
            messages = [{"role": "user", "content": user_prompt}]
            
            response = client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=system_prompt,
                messages=messages
            )
            
            return response.content[0].text
            
        except anthropic.APIError as e:
            if "invalid_api_key" in str(e).lower() or "authentication" in str(e).lower():
                raise APIAuthenticationError(f"Claude API error: {str(e)}")
            else:
                raise APIConnectionError(f"Claude API error: {str(e)}")
                
        except Exception as e:
            if isinstance(e, (APIConnectionError, APIAuthenticationError)):
                raise
            raise APIConnectionError(f"Error with Claude API: {str(e)}")


class NoveltyAnalyzer:
    """Analyzes the novelty of an idea compared to existing patents and products."""
    
    def __init__(self, config, claude_client=None):
        """Initialize the NoveltyAnalyzer.
        
        Args:
            config: Configuration object.
            claude_client: Claude API client (optional).
        """
        self.config = config
        self.claude_client = claude_client or ClaudeClient(config)
        self.score_range = config.get("output.simple_score_range", [1, 10])
    
    def _create_system_prompt(self, output_format="text"):
        """Create the system prompt for novelty analysis.
        
        Args:
            output_format (str): Output format (text, markdown, json).
            
        Returns:
            str: System prompt.
        """
        min_score, max_score = self.score_range
        
        system_prompt = f"""
        You are a patent and product novelty analyzer. Your task is to analyze a user's idea and compare it against existing patents and products to determine novelty.

        Analyze the following:
        1. How similar is the user's idea to the existing patents/products?
        2. What unique aspects does the user's idea have?
        3. What common elements exist between the idea and existing items?
        4. How technically feasible is the user's idea?
        5. Assign a novelty score from {min_score} to {max_score}, where {min_score} means "already exists" and {max_score} means "completely novel".

        Provide your analysis in {output_format} format.
        """
        
        return system_prompt.strip()
    
    def _create_user_prompt(self, idea, patents, web_results):
        """Create the user prompt for novelty analysis.
        
        Args:
            idea (str): The user's idea.
            patents (str): Patent search results.
            web_results (str): Web search results.
            
        Returns:
            str: User prompt.
        """
        prompt = f"""
        # Idea Description
        {idea}

        # Existing Patents
        {patents}

        # Existing Products/Services
        {web_results}

        Analyze this idea for novelty compared to the existing patents and products/services listed above.
        """
        
        return prompt.strip()
    
    def generate_simple_analysis(self, idea, patents, web_results, output_format="text"):
        """Generate a simple novelty analysis.
        
        Args:
            idea (str): The user's idea.
            patents (str): Patent search results.
            web_results (str): Web search results.
            output_format (str): Output format (text, markdown, json).
            
        Returns:
            str: Simple novelty analysis.
        """
        system_prompt = self._create_system_prompt(output_format)
        user_prompt = self._create_user_prompt(idea, patents, web_results)
        
        # Add simple analysis directive
        system_prompt += f"\nFocus on providing a simple analysis with a novelty score and brief explanation (max 150 words)."
        
        return self.claude_client.generate_analysis(user_prompt, system_prompt)
    
    def generate_complex_analysis(self, idea, patents, web_results, output_format="markdown"):
        """Generate a complex novelty analysis.
        
        Args:
            idea (str): The user's idea.
            patents (str): Patent search results.
            web_results (str): Web search results.
            output_format (str): Output format (text, markdown, json).
            
        Returns:
            str: Complex novelty analysis.
        """
        system_prompt = self._create_system_prompt(output_format)
        user_prompt = self._create_user_prompt(idea, patents, web_results)
        
        # Add complex analysis directive
        system_prompt += f"""
        Provide a comprehensive analysis with:
        1. Executive summary
        2. Detailed comparison table
        3. Novelty score with justification
        4. Unique selling points
        5. Potential challenges
        6. Recommendations for differentiation
        """
        
        return self.claude_client.generate_analysis(user_prompt, system_prompt)
    
    def format_simple_analysis(self, analysis, output_format="text"):
        """Format a simple analysis for output.
        
        Args:
            analysis (str): The analysis from Claude.
            output_format (str): Output format (text, markdown, json).
            
        Returns:
            str or dict: Formatted analysis.
        """
        if output_format == "json":
            try:
                # Check if Claude already returned JSON
                data = json.loads(analysis)
                return data
            except json.JSONDecodeError:
                # Try to extract score and summary from text
                score = None
                for line in analysis.split("\n"):
                    if "score" in line.lower() and ":" in line:
                        try:
                            score_text = line.split(":", 1)[1].strip()
                            score = int(score_text.split("/")[0].strip())
                        except (ValueError, IndexError):
                            pass
                
                return {
                    "score": score or self.score_range[0],
                    "analysis": analysis
                }
        
        return analysis
    
    def format_complex_analysis(self, analysis, output_format="markdown"):
        """Format a complex analysis for output.
        
        Args:
            analysis (str): The analysis from Claude.
            output_format (str): Output format (text, markdown, json).
            
        Returns:
            str or dict: Formatted analysis.
        """
        if output_format == "json":
            try:
                # Check if Claude already returned JSON
                data = json.loads(analysis)
                return data
            except json.JSONDecodeError:
                # Extract relevant sections
                sections = {
                    "executive_summary": "",
                    "novelty_score": self.score_range[0],
                    "unique_points": [],
                    "challenges": [],
                    "recommendations": [],
                    "full_analysis": analysis
                }
                
                # Extract sections from headings
                current_section = None
                for line in analysis.split("\n"):
                    lower_line = line.lower()
                    
                    if "executive summary" in lower_line or "summary" in lower_line:
                        current_section = "executive_summary"
                        continue
                    elif "novelty score" in lower_line or "score" in lower_line:
                        current_section = "novelty_score"
                        # Try to extract score
                        try:
                            score_text = line.split(":", 1)[1].strip()
                            sections["novelty_score"] = int(score_text.split("/")[0].strip())
                        except (ValueError, IndexError):
                            pass
                        continue
                    elif "unique" in lower_line and ("points" in lower_line or "selling" in lower_line):
                        current_section = "unique_points"
                        continue
                    elif "challenges" in lower_line or "limitations" in lower_line:
                        current_section = "challenges"
                        continue
                    elif "recommendations" in lower_line or "suggestions" in lower_line:
                        current_section = "recommendations"
                        continue
                    
                    if current_section == "executive_summary":
                        sections["executive_summary"] += line + "\n"
                    elif current_section in ["unique_points", "challenges", "recommendations"]:
                        if line.strip().startswith(("-", "*", "•")) and line.strip():
                            sections[current_section].append(line.strip()[1:].strip())
                
                return sections
        
        return analysis
