"""
Tests for CLI interface.
"""

import os
import tempfile
import pytest
from unittest.mock import MagicMock, patch

from src.cli import PatentAnalyzerCLI
from src.utils.error_handler import InputValidationError


class TestPatentAnalyzerCLI:
    """Tests for the PatentAnalyzerCLI class."""
    
    def setup_method(self):
        """Set up test environment."""
        # Create mock config
        self.config = MagicMock()
        
        # Create mock OllamaClient and KeywordExtractor
        self.mock_ollama_client = MagicMock()
        self.mock_ollama_client.is_available.return_value = True  # Default to available
        self.mock_keyword_extractor = MagicMock()
        
        # Create CLI instance with patch
        with patch('src.cli.OllamaClient', return_value=self.mock_ollama_client), \
             patch('src.cli.KeywordExtractor', return_value=self.mock_keyword_extractor):
            self.cli = PatentAnalyzerCLI(self.config)
    
    def test_get_idea_text_from_argument(self):
        """Test getting idea text from argument."""
        idea = "This is a test idea"
        result = self.cli._get_idea_text(idea, None)
        assert result == idea
    
    def test_get_idea_text_from_file(self):
        """Test getting idea text from file."""
        idea = "This is a test idea from file"
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp:
            temp.write(idea)
            temp_path = temp.name
        
        try:
            result = self.cli._get_idea_text(None, temp_path)
            assert result == idea
        finally:
            # Clean up
            os.unlink(temp_path)
    
    def test_get_idea_text_empty(self):
        """Test getting idea text when none provided."""
        result = self.cli._get_idea_text(None, None)
        assert result is None
    
    def test_get_idea_text_file_not_found(self):
        """Test getting idea text from non-existent file."""
        with pytest.raises(InputValidationError):
            self.cli._get_idea_text(None, "nonexistent_file.txt")
    
    def test_extract_keywords_with_provided_keywords(self):
        """Test extracting keywords when provided directly."""
        keywords = "keyword1, keyword2, keyword3"
        result = self.cli._extract_keywords("Test idea", keywords)
        assert result == ["keyword1", "keyword2", "keyword3"]
        # Ensure the extractor was not called
        self.mock_keyword_extractor.extract_keywords.assert_not_called()
    
    def test_extract_keywords_with_ollama(self):
        """Test extracting keywords using Ollama."""
        # Mock the keyword extractor
        self.mock_keyword_extractor.extract_keywords.return_value = ["keyword1", "keyword2", "keyword3"]
        
        # Test
        result = self.cli._extract_keywords("Test idea")
        
        # Verify
        assert result == ["keyword1", "keyword2", "keyword3"]
        self.mock_keyword_extractor.extract_keywords.assert_called_once_with("Test idea")
    
    def test_extract_keywords_fallback(self):
        """Test fallback keyword extraction when Ollama fails."""
        # Mock the keyword extractor to raise an exception
        from src.utils.error_handler import APIConnectionError
        self.mock_keyword_extractor.extract_keywords.side_effect = APIConnectionError("Test error")
        
        # Test
        result = self.cli._extract_keywords("This is a test idea with some words")
        
        # Verify
        # Should extract words from the idea text
        assert len(result) <= 5
        assert "this" not in result  # Common words should be filtered out
        assert "test" in result
        assert "idea" in result
        assert "with" not in result  # Common words should be filtered out
        assert "some" in result
        assert "words" in result
    
    def test_extract_keywords_ollama_not_available(self):
        """Test keyword extraction when Ollama is not available."""
        # Create a new CLI instance with Ollama not available
        self.mock_ollama_client.is_available.return_value = False
        
        with patch('src.cli.OllamaClient', return_value=self.mock_ollama_client), \
             patch('src.cli.KeywordExtractor', return_value=self.mock_keyword_extractor):
            cli = PatentAnalyzerCLI(self.config)
        
        # Test
        result = cli._extract_keywords("This is a test idea with some words")
        
        # Verify
        # Should use fallback method
        assert len(result) <= 5
        assert "test" in result
        assert "idea" in result
        
        # Ensure the extractor was not called
        self.mock_keyword_extractor.extract_keywords.assert_not_called()
    
    def test_extract_keywords_fallback_method(self):
        """Test the fallback keyword extraction method directly."""
        result = self.cli._extract_keywords_fallback("This is a test idea with some words")
        
        # Verify
        assert len(result) <= 5
        assert "this" not in result  # Common words should be filtered out
        assert "test" in result
        assert "idea" in result
        assert "with" not in result  # Common words should be filtered out
        assert "some" in result
        assert "words" in result
    
    @patch('src.cli.click.Group')
    def test_run_cli(self, mock_click_group):
        """Test running the CLI."""
        # Setup mock
        mock_cli = MagicMock()
        mock_click_group.return_value = mock_cli
        
        # Run CLI
        self.cli.run()
        
        # Verify command was called
        mock_cli.assert_called_once()
