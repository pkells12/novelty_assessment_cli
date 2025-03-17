"""
Patent search functionality using SerpApi.
"""

import os
import json
import time
import requests
from requests.exceptions import RequestException
from tenacity import retry, stop_after_attempt, wait_exponential
from serpapi import GoogleSearch

from novelty_assessment_cli.utils.error_handler import APIConnectionError, APIAuthenticationError


class SerpApiClient:
    """Client for SerpApi to search Google Patents."""
    
    def __init__(self, config):
        """Initialize the SerpApiClient.
        
        Args:
            config: Configuration object.
        """
        self.api_key = config.get("api_keys.serpapi")
        self.engine = config.get("serpapi.engine")
        self.timeout = config.get("serpapi.timeout")
        self.results_limit = config.get("serpapi.results_limit")
        self.patent_years = config.get("serpapi.patent_years")
        self.country = config.get("serpapi.country")
    
    def validate_credentials(self):
        """Validate API key.
        
        Returns:
            bool: True if credentials are valid.
            
        Raises:
            APIAuthenticationError: If credentials are invalid.
        """
        if not self.api_key:
            raise APIAuthenticationError("SerpApi API key not found.")
        
        return True
    
    def build_search_params(self, keywords):
        """Build search parameters for SerpApi.
        
        Args:
            keywords (str): Keywords to search for.
            
        Returns:
            dict: Search parameters.
        """
        query = keywords if isinstance(keywords, str) else ", ".join(keywords)
        
        # Make sure num parameter is between 10 and 100 as required by SerpApi
        num_results = max(10, min(100, self.results_limit))
        
        return {
            "engine": self.engine,
            "q": query,
            "api_key": self.api_key,
            "num": num_results,
            "tbm": "pts",  # Patents search
            "tbs": f"plt:1,plc:{self.country}"  # Filter by country
        }
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=2, max=10),
        reraise=True
    )
    def search(self, keywords):
        """Search for patents with SerpApi.
        
        Args:
            keywords (str or list): Keywords to search for.
            
        Returns:
            dict: Search results.
            
        Raises:
            APIConnectionError: If there is an error connecting to the API.
            APIAuthenticationError: If credentials are invalid.
        """
        try:
            self.validate_credentials()
            
            params = self.build_search_params(keywords)
            
            search = GoogleSearch(params)
            results = search.get_dict()
            
            if "error" in results:
                error_message = results["error"]
                if "invalid API key" in error_message.lower():
                    raise APIAuthenticationError(f"SerpApi error: {error_message}")
                else:
                    raise APIConnectionError(f"SerpApi error: {error_message}")
                
            return results
        except Exception as e:
            if isinstance(e, (APIConnectionError, APIAuthenticationError)):
                raise
            raise APIConnectionError(f"Error connecting to SerpApi: {str(e)}")


class PatentSearcher:
    """Searches for patents related to an idea."""
    
    def __init__(self, config, serp_client=None):
        """Initialize the PatentSearcher.
        
        Args:
            config: Configuration object.
            serp_client: SerpApi client (optional).
        """
        self.config = config
        self.serp_client = serp_client or SerpApiClient(config)
    
    def search_patents(self, keywords):
        """Search for patents related to the keywords.
        
        Args:
            keywords (str or list): Keywords to search for.
            
        Returns:
            list: List of patent information.
        """
        results = self.serp_client.search(keywords)
        return self._parse_patent_results(results)
    
    def _parse_patent_results(self, results):
        """Parse the patent results from SerpApi.
        
        Args:
            results (dict): Patent search results.
            
        Returns:
            list: List of patent information.
        """
        patents = []
        
        # Check if organic_results exists in the response
        organic_results = results.get("organic_results", [])
        
        if not organic_results:
            return patents
            
        for i, result in enumerate(organic_results):
            # Extract basic information using the actual SerpApi patent format
            patent = {
                "title": result.get("title", ""),
                "link": result.get("patent_link", ""),
                "snippet": result.get("snippet", ""),
                "patent_number": result.get("publication_number", ""),
                "filing_date": result.get("filing_date", ""),
                "inventors": result.get("inventor", "").split(", ") if result.get("inventor") else [],
                "abstract": result.get("snippet", ""),
                "claims": []
            }
            
            # Only add patents with at least a title and a link
            if patent["title"] and patent["link"]:
                patents.append(patent)
            
            # Limit to configured number of results
            if len(patents) >= self.config.get("serpapi.results_limit"):
                break
                
        return patents
    
    def _extract_patent_number(self, result):
        """Extract patent number from result.
        
        Args:
            result (dict): Patent result.
            
        Returns:
            str: Patent number or empty string if not found.
        """
        return result.get("publication_number", "")
    
    def _extract_filing_date(self, result):
        """Extract filing date from result.
        
        Args:
            result (dict): Patent result.
            
        Returns:
            str: Filing date or empty string if not found.
        """
        return result.get("filing_date", "")
    
    def _extract_inventors(self, result):
        """Extract inventors from result.
        
        Args:
            result (dict): Patent result.
            
        Returns:
            list: List of inventors or empty list if not found.
        """
        inventor_str = result.get("inventor", "")
        if inventor_str:
            return [inv.strip() for inv in inventor_str.split(",")]
        return []
    
    def _extract_abstract(self, result):
        """Extract abstract from result.
        
        Args:
            result (dict): Patent result.
            
        Returns:
            str: Abstract or snippet if abstract not found.
        """
        return result.get("snippet", "")
    
    def _extract_claims(self, result):
        """Extract claims from result.
        
        Args:
            result (dict): Patent result.
            
        Returns:
            list: List of claims or empty list if not found.
        """
        return []  # Will require additional API calls to extract claims
    
    def format_patent_results(self, patents, max_length=500):
        """Format patent results for analysis.
        
        Args:
            patents (list): List of patent information.
            max_length (int): Maximum length of formatted text.
            
        Returns:
            str: Formatted patent results.
        """
        if not patents:
            return "No patents found."
        
        formatted_results = []
        
        for i, patent in enumerate(patents):
            formatted_patent = f"Patent {i+1}: {patent['title']}\n"
            
            if patent['patent_number']:
                formatted_patent += f"Patent Number: {patent['patent_number']}\n"
                
            if patent['filing_date']:
                formatted_patent += f"Filing Date: {patent['filing_date']}\n"
                
            if patent['inventors']:
                formatted_patent += f"Inventors: {', '.join(patent['inventors'])}\n"
                
            if patent['abstract']:
                abstract = patent['abstract']
                if len(abstract) > max_length:
                    abstract = abstract[:max_length] + "..."
                formatted_patent += f"Abstract: {abstract}\n"
                
            formatted_patent += f"Link: {patent['link']}\n"
            
            formatted_results.append(formatted_patent)
        
        return "\n\n".join(formatted_results)
    
    def summarize_patent(self, patent, max_length=200):
        """Summarize a patent for display.
        
        Args:
            patent (dict): Patent information.
            max_length (int): Maximum length of summary.
            
        Returns:
            str: Patent summary.
        """
        summary = f"{patent['title']}"
        
        if patent['patent_number']:
            summary += f" ({patent['patent_number']})"
            
        if patent['abstract']:
            abstract = patent['abstract']
            if len(abstract) > max_length:
                abstract = abstract[:max_length] + "..."
            summary += f" - {abstract}"
            
        return summary
