"""
Web search functionality using Brave Search API.
"""

import json
import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from src.utils.error_handler import APIConnectionError, APIAuthenticationError


class BraveSearchClient:
    """Client for Brave Search API."""
    
    def __init__(self, config):
        """Initialize the BraveSearchClient.
        
        Args:
            config: Configuration object.
        """
        self.api_key = config.get("api_keys.brave")
        self.timeout = config.get("brave.timeout")
        self.results_limit = config.get("brave.results_limit")
        self.search_focus = config.get("brave.search_focus")
        self.base_url = "https://api.search.brave.com/res/v1/web/search"
    
    def validate_credentials(self):
        """Validate API key.
        
        Returns:
            bool: True if credentials are valid.
            
        Raises:
            APIAuthenticationError: If credentials are invalid.
        """
        if not self.api_key:
            raise APIAuthenticationError("Brave Search API key not found.")
        
        return True
    
    def build_search_params(self, keywords):
        """Build search parameters for Brave Search API.
        
        Args:
            keywords (str or list): Keywords to search for.
            
        Returns:
            dict: Search parameters.
        """
        # Convert keywords to string if it's a list
        if isinstance(keywords, list):
            # Take only the first few keywords to avoid exceeding length limits
            if len(keywords) > 5:
                keywords = keywords[:5]
            query = ", ".join(keywords)
        else:
            query = keywords
        
        # Add product/service modifiers to the query
        if self.search_focus == "products_services":
            query = f"{query} product service available"
        
        # Ensure query stays within Brave API's 400 character limit
        if len(query) > 380:  # Leave some room for the modifiers
            query = query[:380]
        
        return {
            "q": query,
            "count": self.results_limit
        }
    
    def build_headers(self):
        """Build headers for Brave Search API request.
        
        Returns:
            dict: Request headers.
        """
        return {
            "Accept": "application/json",
            "X-Subscription-Token": self.api_key
        }
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=2, max=10),
        reraise=True
    )
    def search(self, keywords):
        """Search using Brave Search API.
        
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
            headers = self.build_headers()
            
            response = requests.get(
                self.base_url,
                headers=headers,
                params=params,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                raise APIAuthenticationError(f"Brave Search API error: Invalid API key")
            else:
                raise APIConnectionError(f"Brave Search API error: {response.status_code} - {response.text}")
                
        except requests.exceptions.RequestException as e:
            raise APIConnectionError(f"Error connecting to Brave Search API: {str(e)}")
        except Exception as e:
            if isinstance(e, (APIConnectionError, APIAuthenticationError)):
                raise
            raise APIConnectionError(f"Error with Brave Search API: {str(e)}")


class WebSearcher:
    """Searches for existing products/services related to an idea."""
    
    def __init__(self, config, brave_client=None):
        """Initialize the WebSearcher.
        
        Args:
            config: Configuration object.
            brave_client: Brave Search client (optional).
        """
        self.config = config
        self.brave_client = brave_client or BraveSearchClient(config)
    
    def search_web(self, keywords):
        """Search for products/services related to the keywords.
        
        Args:
            keywords (str or list): Keywords to search for.
            
        Returns:
            list: List of search results.
        """
        results = self.brave_client.search(keywords)
        return self._parse_web_results(results)
    
    def _parse_web_results(self, results):
        """Parse the web search results from Brave Search API.
        
        Args:
            results (dict): Web search results.
            
        Returns:
            list: List of web search information.
        """
        web_results = []
        
        # Check if web results exist
        if not results.get("web", {}).get("results"):
            return web_results
            
        for result in results["web"]["results"]:
            # Extract basic information
            web_result = {
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "description": result.get("description", ""),
                "source": self._extract_source(result),
                "publication_date": self._extract_publication_date(result),
                "price": self._extract_price(result)
            }
            
            # Only add results with at least a title and a URL
            if web_result["title"] and web_result["url"]:
                web_results.append(web_result)
                
            # Limit to configured number of results
            if len(web_results) >= self.config.get("brave.results_limit"):
                break
                
        return web_results
    
    def _extract_source(self, result):
        """Extract source/brand information from result.
        
        Args:
            result (dict): Web search result.
            
        Returns:
            str: Source information or empty string if not found.
        """
        if "extra_snippets" in result:
            for snippet in result["extra_snippets"]:
                if "source" in snippet.lower():
                    return snippet
                    
        if "url" in result:
            url = result["url"]
            # Extract domain without protocol and www
            if "//" in url:
                domain = url.split("//", 1)[1]
            else:
                domain = url
                
            if domain.startswith("www."):
                domain = domain[4:]
                
            if "/" in domain:
                domain = domain.split("/", 1)[0]
                
            return domain
            
        return ""
    
    def _extract_publication_date(self, result):
        """Extract publication date from result.
        
        Args:
            result (dict): Web search result.
            
        Returns:
            str: Publication date or empty string if not found.
        """
        if "age" in result:
            return result["age"]
            
        return ""
    
    def _extract_price(self, result):
        """Extract price information from result.
        
        Args:
            result (dict): Web search result.
            
        Returns:
            str: Price information or empty string if not found.
        """
        if "description" in result:
            description = result["description"].lower()
            
            # Look for price patterns like $X, $X.XX, X dollars
            if "$" in description:
                # Simple extraction, could be improved with regex
                price_start = description.find("$")
                price_end = price_start + 1
                
                while price_end < len(description) and (description[price_end].isdigit() or description[price_end] == "."):
                    price_end += 1
                    
                if price_end > price_start + 1:
                    return description[price_start:price_end]
                    
        return ""
    
    def format_web_results(self, web_results, max_length=500):
        """Format web search results for analysis.
        
        Args:
            web_results (list): List of web search information.
            max_length (int): Maximum length for descriptions.
            
        Returns:
            str: Formatted web search results.
        """
        if not web_results:
            return "No relevant products or services found."
            
        formatted_results = []
        
        for i, result in enumerate(web_results):
            formatted_result = f"Product/Service {i+1}: {result['title']}\n"
            
            if result['source']:
                formatted_result += f"Source: {result['source']}\n"
                
            if result['publication_date']:
                formatted_result += f"Date: {result['publication_date']}\n"
                
            if result['price']:
                formatted_result += f"Price: {result['price']}\n"
                
            if result['description']:
                description = result['description']
                if len(description) > max_length:
                    description = description[:max_length] + "..."
                formatted_result += f"Description: {description}\n"
                
            formatted_result += f"URL: {result['url']}\n"
            
            formatted_results.append(formatted_result)
            
        return "\n\n".join(formatted_results)
    
    def extract_relevant_content(self, web_results):
        """Extract most relevant parts of web results for analysis.
        
        Args:
            web_results (list): List of web search information.
            
        Returns:
            list: List of relevant content strings.
        """
        relevant_content = []
        
        for result in web_results:
            content = f"{result['title']} - {result['description']}"
            
            if result['price']:
                content += f" Price: {result['price']}."
                
            relevant_content.append(content)
            
        return relevant_content
