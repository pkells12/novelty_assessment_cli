"""
Keyword extraction using Ollama.
"""

import json
import requests
from tenacity import retry, stop_after_attempt, wait_exponential
import re

from src.utils.error_handler import APIConnectionError, APIAuthenticationError

# Common words to filter out
COMMON_WORDS = {
    'and', 'or', 'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'with', 'by', 'of',
    'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do',
    'does', 'did', 'will', 'would', 'shall', 'should', 'may', 'might', 'must', 'can',
    'could', 'that', 'which', 'who', 'whom', 'this', 'these', 'those', 'am', 'is',
    'are', 'was', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'their', 'our', 'my',
    'your', 'its', 'his', 'her'
}

class OllamaClient:
    """Client for Ollama API."""
    
    def __init__(self, config):
        """Initialize the OllamaClient.
        
        Args:
            config: Configuration object.
        """
        self.api_url = config.get("ollama.api_url")
        self.model = config.get("ollama.model")
        self.temperature = config.get("ollama.temperature")
        self.max_tokens = config.get("ollama.max_tokens")
        self.timeout = config.get("ollama.timeout")
    
    def is_available(self):
        """Check if Ollama service is running.
        
        Returns:
            bool: True if Ollama is available, False otherwise.
        """
        try:
            response = requests.get(f"{self.api_url.replace('/api', '')}", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True
    )
    def generate_completion(self, prompt):
        """Generate a completion from Ollama.
        
        Args:
            prompt (str): The prompt to send to Ollama.
        
        Returns:
            str: The generated completion.
        
        Raises:
            APIConnectionError: If the API connection fails.
        """
        try:
            response = requests.post(
                f"{self.api_url}/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "temperature": self.temperature,
                    "num_predict": self.max_tokens,
                },
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                raise APIConnectionError(f"Ollama API returned status code {response.status_code}")
            
            return self._handle_response(response)
        
        except requests.exceptions.RequestException as e:
            raise APIConnectionError(f"Failed to connect to Ollama API: {str(e)}")
    
    def _handle_response(self, response):
        """Extract text from Ollama response.
        
        Args:
            response: Response from Ollama API.
        
        Returns:
            str: The generated text.
        """
        try:
            # Ollama streaming response comes as multiple JSON objects
            # We need to concatenate all response parts
            response_text = response.text
            
            # Split by lines and parse each JSON object
            response_parts = []
            for line in response_text.strip().split('\n'):
                if line:
                    response_json = json.loads(line)
                    if 'response' in response_json:
                        response_parts.append(response_json['response'])
            
            # Join all parts
            return ''.join(response_parts)
        
        except (json.JSONDecodeError, KeyError) as e:
            raise APIConnectionError(f"Failed to parse Ollama response: {str(e)}")


class KeywordExtractor:
    """Extracts keywords from patent ideas using Ollama."""
    
    def __init__(self, config, ollama_client):
        """Initialize the KeywordExtractor.
        
        Args:
            config: Configuration object.
            ollama_client: OllamaClient instance.
        """
        self.ollama_client = ollama_client
        self.keyword_count = 10  # Extract more than needed, filter later
        self.PROMPT_TEMPLATE = """
        You are an expert patent search consultant. Given an idea description, extract {keyword_count} keywords that would be most effective for searching patents and existing products.

        Focus on:
        - Technical terms relevant to the domain
        - Functional descriptions of the innovation
        - Potential application areas
        - Technologies or methods involved
        - Components or materials mentioned

        Do NOT include common words or generic terms.
        Format output as a comma-separated list.

        Idea: {idea_text}

        Keywords:
        """
    
    def extract_keywords(self, idea_text):
        """Extract keywords from an idea description.
        
        Args:
            idea_text (str): The idea to extract keywords from.
            
        Returns:
            list or str: List or comma-separated string of keywords.
        """
        if not idea_text:
            raise ValueError("Idea text cannot be empty.")
            
        # Use Ollama if available, otherwise use fallback
        if self.ollama_client.is_available():
            # Create prompt with additional context for patent search
            prompt = self.PROMPT_TEMPLATE.format(
                keyword_count=self.keyword_count,
                idea_text=idea_text
            )
            
            # Get completion from Ollama
            completion = self.ollama_client.generate_completion(prompt)
            
            # Extract keywords from completion
            keywords = self._parse_keywords_from_completion(completion)
        else:
            # Use fallback method (simple text analysis)
            keywords = self._extract_keywords_fallback(idea_text)
            
        # Clean and validate keywords
        clean_keywords = self.clean_keywords(keywords)
        valid_keywords = self.validate_keywords(clean_keywords)
        
        return valid_keywords
    
    def _parse_keywords_from_completion(self, completion):
        """Parse keywords from an Ollama completion.
        
        Args:
            completion (str): The completion from Ollama.
            
        Returns:
            list: List of extracted keywords.
        """
        # Extract keywords section
        if not completion:
            return []
            
        # Try different parsing approaches
        keywords = []
        
        # Look for comma-separated list
        if "," in completion:
            # Extract only what appears to be the comma-separated list
            for line in completion.split("\n"):
                if "," in line and not line.startswith("#") and not line.startswith("*"):
                    parts = [p.strip() for p in line.split(",")]
                    keywords.extend([p for p in parts if p and len(p) < 50])  # Skip empty or very long items
        
        # If that fails, look for numbered list (1. keyword, 2. keyword)
        if not keywords:
            for line in completion.split("\n"):
                line = line.strip()
                if re.match(r"^\d+\.\s+\w+", line):
                    # Extract the part after the number and period
                    keyword = re.sub(r"^\d+\.\s+", "", line).strip()
                    if keyword and len(keyword) < 50:  # Skip empty or very long items
                        keywords.append(keyword)
        
        # If still empty, extract potential keywords using NLP-like heuristics
        if not keywords:
            # Split by spaces and take words that might be keywords
            words = completion.split()
            for word in words:
                word = word.strip().lower()
                if (word and len(word) > 3 and len(word) < 20 and 
                    word not in COMMON_WORDS and 
                    not any(c.isdigit() for c in word)):
                    keywords.append(word)
        
        # Limit to the expected number of keywords
        if len(keywords) > self.keyword_count:
            keywords = keywords[:self.keyword_count]
            
        return keywords
    
    def _extract_keywords_fallback(self, idea_text):
        """Extract keywords using a fallback method when Ollama is not available.
        
        Args:
            idea_text (str): The idea text.
            
        Returns:
            list: Extracted keywords.
        """
        words = re.findall(r'\b\w+\b', idea_text.lower())
        
        # Get word frequencies
        word_freq = {}
        for word in words:
            if (len(word) > 3 and word not in COMMON_WORDS and 
                not any(c.isdigit() for c in word)):
                word_freq[word] = word_freq.get(word, 0) + 1
                
        # Sort by frequency
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        # Get top words
        keywords = [word for word, _ in sorted_words[:self.keyword_count]]
        
        return keywords
    
    def clean_keywords(self, keywords):
        """Clean keywords.
        
        Args:
            keywords (list): The keywords to clean.
        
        Returns:
            list: The cleaned keywords.
        """
        cleaned = []
        for keyword in keywords:
            # Remove punctuation except hyphens
            keyword = ''.join(c for c in keyword if c.isalnum() or c == '-' or c.isspace())
            # Normalize case
            keyword = keyword.lower()
            # Remove extra whitespace
            keyword = ' '.join(keyword.split())
            
            if keyword:
                cleaned.append(keyword)
        
        return cleaned
    
    def validate_keywords(self, keywords):
        """Validate and filter keywords.
        
        Args:
            keywords (list): Keywords to validate.
            
        Returns:
            list: Filtered and validated keywords.
        """
        if not keywords:
            # Provide default keywords if none are found
            return ["smart", "device", "technology", "innovation", "system"]
            
        # Filter out common words and duplicates
        filtered = []
        for keyword in keywords:
            # Skip if it's a common word
            if keyword.lower() in COMMON_WORDS:
                continue
                
            # Skip if it's too short
            if len(keyword) < 3:
                continue
                
            # Skip if it's already in the filtered list (case-insensitive)
            if keyword.lower() in [k.lower() for k in filtered]:
                continue
                
            filtered.append(keyword)
            
        # If filtering removed all keywords, provide defaults
        if not filtered:
            return ["smart", "device", "technology", "innovation", "system"]
            
        return filtered
