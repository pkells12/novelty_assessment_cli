"""
Tests for keyword extraction.
"""

import pytest
from unittest.mock import MagicMock, patch
import requests

from src.keyword_extractor import OllamaClient, KeywordExtractor
from src.utils.error_handler import APIConnectionError


class TestOllamaClient:
    """Tests for the OllamaClient class."""
    
    def setup_method(self):
        """Set up test environment."""
        # Create mock config
        self.config = MagicMock()
        self.config.get.side_effect = lambda key, default=None: {
            "ollama.api_url": "http://localhost:11434/api",
            "ollama.model": "llama2",
            "ollama.temperature": 0.1,
            "ollama.max_tokens": 1000,
            "ollama.timeout": 30
        }.get(key, default)
        
        # Create client
        self.client = OllamaClient(self.config)
    
    @patch('src.keyword_extractor.requests.get')
    def test_is_available_true(self, mock_get):
        """Test is_available when Ollama is running."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        result = self.client.is_available()
        
        assert result is True
        mock_get.assert_called_once_with("http://localhost:11434", timeout=5)
    
    @patch('src.keyword_extractor.requests.get')
    def test_is_available_false_status_code(self, mock_get):
        """Test is_available when Ollama returns non-200 status code."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        result = self.client.is_available()
        
        assert result is False
    
    @patch('src.keyword_extractor.requests.get')
    def test_is_available_false_exception(self, mock_get):
        """Test is_available when Ollama connection fails."""
        # We need to use side_effect with a specific requests exception
        mock_get.side_effect = requests.exceptions.RequestException("Connection error")
        
        result = self.client.is_available()
        
        assert result is False
    
    @patch('src.keyword_extractor.requests.post')
    def test_generate_completion(self, mock_post):
        """Test generating a completion."""
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"response":"test1"}\n{"response":"test2"}'
        mock_post.return_value = mock_response
        
        # Test
        result = self.client.generate_completion("Test prompt")
        
        # Verify
        assert result == "test1test2"
        mock_post.assert_called_once_with(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama2",
                "prompt": "Test prompt",
                "temperature": 0.1,
                "num_predict": 1000,
            },
            timeout=30
        )
    
    @patch('src.keyword_extractor.requests.post')
    def test_generate_completion_error(self, mock_post):
        """Test generating a completion with an error."""
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response
        
        # Test
        with pytest.raises(APIConnectionError):
            self.client.generate_completion("Test prompt")


class TestKeywordExtractor:
    """Tests for the KeywordExtractor class."""
    
    def setup_method(self):
        """Set up test environment."""
        # Create mock config
        self.config = MagicMock()
        
        # Create mock Ollama client
        self.ollama_client = MagicMock()
        self.ollama_client.is_available.return_value = True
        
        # Create extractor
        self.extractor = KeywordExtractor(self.config, self.ollama_client)
    
    def test_clean_keywords(self):
        """Test cleaning keywords."""
        keywords = [
            "  Test  ",
            "Test!",
            "test-hyphen",
            "te$t*#",
            ""
        ]
        
        result = self.extractor.clean_keywords(keywords)
        
        assert result == ["test", "test", "test-hyphen", "tet"]
    
    def test_filter_keywords(self):
        """Test filtering keywords."""
        keywords = [
            "test",
            "and",
            "to",
            "the",
            "test",  # Duplicate
            "a",
            "ab",    # Too short
            "unique"
        ]
        
        result = self.extractor.filter_keywords(keywords)
        
        assert result == ["test", "unique"]
    
    def test_format_for_search(self):
        """Test formatting keywords for search."""
        keywords = ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5", "keyword6"]
        
        result = self.extractor.format_for_search(keywords)
        
        assert result == "keyword1 keyword2 keyword3 keyword4 keyword5"
        
        # Test with custom max_keywords
        result = self.extractor.format_for_search(keywords, max_keywords=3)
        
        assert result == "keyword1 keyword2 keyword3"
    
    def test_extract_keywords_from_completion(self):
        """Test extracting keywords from a completion."""
        completion = "keyword1, keyword2, keyword3"
        
        result = self.extractor._extract_keywords_from_completion(completion)
        
        assert result == ["keyword1", "keyword2", "keyword3"]
        
        # Test with empty completion
        assert self.extractor._extract_keywords_from_completion("") == []
        assert self.extractor._extract_keywords_from_completion(None) == []
    
    def test_create_prompt(self):
        """Test creating a prompt."""
        idea_text = "This is a test idea"
        
        result = self.extractor._create_prompt(idea_text)
        
        assert "extract 10 keywords" in result
        assert idea_text in result
    
    def test_extract_keywords(self):
        """Test extracting keywords from an idea."""
        # Mock Ollama client to return a completion
        self.ollama_client.generate_completion.return_value = "keyword1, keyword2, keyword3"
        
        # Test
        result = self.extractor.extract_keywords("This is a test idea")
        
        # Verify
        assert result == ["keyword1", "keyword2", "keyword3"]
        self.ollama_client.generate_completion.assert_called_once()
    
    def test_extract_keywords_ollama_not_available(self):
        """Test extracting keywords when Ollama is not available."""
        # Mock Ollama client to return not available
        self.ollama_client.is_available.return_value = False
        
        # Test
        with pytest.raises(APIConnectionError):
            self.extractor.extract_keywords("This is a test idea")
