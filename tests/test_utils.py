"""
Tests for utility modules.
"""

import os
import time
import pytest
import tempfile
import yaml
import json
from pathlib import Path

from src.utils.config import ConfigLoader
from src.utils.cache import CacheManager


class TestConfigLoader:
    """Tests for the ConfigLoader class."""
    
    def test_load_config(self):
        """Test loading configuration from a file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as temp:
            temp.write("""
            app:
              name: "Test App"
              version: "0.0.1"
            api_keys:
              test: "test_key"
            """)
            temp_path = temp.name
        
        try:
            config = ConfigLoader(temp_path)
            
            assert config.get("app.name") == "Test App"
            assert config.get("app.version") == "0.0.1"
            assert config.get("api_keys.test") == "test_key"
        finally:
            # Clean up
            os.unlink(temp_path)
    
    def test_get_nested_config(self):
        """Test getting nested configuration values."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as temp:
            temp.write("""
            nested:
              level1:
                level2:
                  value: "nested_value"
            """)
            temp_path = temp.name
        
        try:
            config = ConfigLoader(temp_path)
            
            assert config.get("nested.level1.level2.value") == "nested_value"
            assert config.get("nonexistent") is None
            assert config.get("nonexistent", "default") == "default"
        finally:
            # Clean up
            os.unlink(temp_path)
    
    def test_set_config(self):
        """Test setting configuration values."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as temp:
            temp.write("""
            app:
              name: "Test App"
            """)
            temp_path = temp.name
        
        try:
            config = ConfigLoader(temp_path)
            
            config.set("app.version", "0.0.2")
            config.set("new.key", "new_value")
            
            assert config.get("app.version") == "0.0.2"
            assert config.get("new.key") == "new_value"
        finally:
            # Clean up
            os.unlink(temp_path)
    
    def test_env_override(self, monkeypatch):
        """Test overriding configuration with environment variables."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as temp:
            temp.write("""
            api_keys:
              serpapi: null
              brave: null
              anthropic: null
            ollama:
              model: "llama2"
            cache:
              duration_days: 7
            serpapi:
              results_limit: 2
              patent_years: 30
            brave:
              results_limit: 2
            """)
            temp_path = temp.name
        
        try:
            monkeypatch.setenv("SERPAPI_API_KEY", "test_serpapi_key")
            monkeypatch.setenv("BRAVE_API_KEY", "test_brave_key")
            monkeypatch.setenv("ANTHROPIC_API_KEY", "test_anthropic_key")
            monkeypatch.setenv("OLLAMA_MODEL", "test_model")
            monkeypatch.setenv("CACHE_DURATION_DAYS", "14")
            monkeypatch.setenv("PATENT_SEARCH_YEARS", "20")
            monkeypatch.setenv("RESULTS_LIMIT", "5")
            
            config = ConfigLoader(temp_path)
            
            assert config.get("api_keys.serpapi") == "test_serpapi_key"
            assert config.get("api_keys.brave") == "test_brave_key"
            assert config.get("api_keys.anthropic") == "test_anthropic_key"
            assert config.get("ollama.model") == "test_model"
            assert config.get("cache.duration_days") == 14
            assert config.get("serpapi.patent_years") == 20
            assert config.get("serpapi.results_limit") == 5
            assert config.get("brave.results_limit") == 5
        finally:
            # Clean up
            os.unlink(temp_path)

class TestCacheManager:
    """Tests for the CacheManager class."""
    
    def setup_method(self):
        """Set up test environment."""
        # Create a temporary directory for cache
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_dir_name = self.temp_dir.name
        
        # Create a config with the temporary directory
        class MockConfig:
            def __init__(self, temp_dir_name):
                self.temp_dir_name = temp_dir_name
                
            def get(self, key, default=None):
                config_values = {
                    'cache.enabled': True,
                    'cache.location': self.temp_dir_name,
                    'cache.duration_days': 7
                }
                return config_values.get(key, default)
        
        self.config = MockConfig(self.temp_dir_name)
        
        # Create cache manager
        self.cache_manager = CacheManager(self.config)
    
    def teardown_method(self):
        """Clean up after test."""
        self.temp_dir.cleanup()
    
    def test_set_get(self):
        """Test setting and getting cache values."""
        # Test data
        key = "test_key"
        value = {"data": "test_value"}
        
        # Set the value in cache
        self.cache_manager.set(key, value)
        
        # Get the value from cache
        cached_value = self.cache_manager.get(key)
        
        # Assert the value is correct
        assert cached_value == value
    
    def test_is_valid(self):
        """Test checking if a cache key is valid."""
        # Test data
        key = "test_key"
        value = {"data": "test_value"}
        
        # Initially the key should not be valid
        assert not self.cache_manager.is_valid(key)
        
        # Set the value in cache
        self.cache_manager.set(key, value)
        
        # Now the key should be valid
        assert self.cache_manager.is_valid(key)
    
    def test_invalidate(self):
        """Test invalidating a cache key."""
        # Test data
        key = "test_key"
        value = {"data": "test_value"}
        
        # Set the value in cache
        self.cache_manager.set(key, value)
        
        # Key should be valid
        assert self.cache_manager.is_valid(key)
        
        # Invalidate the key
        self.cache_manager.invalidate(key)
        
        # Key should no longer be valid
        assert not self.cache_manager.is_valid(key)
    
    def test_clear(self):
        """Test clearing all cache."""
        # Test data
        keys = ["key1", "key2", "key3"]
        value = {"data": "test_value"}
        
        # Set multiple values in cache
        for key in keys:
            self.cache_manager.set(key, value)
        
        # All keys should be valid
        for key in keys:
            assert self.cache_manager.is_valid(key)
        
        # Clear all cache
        self.cache_manager.clear()
        
        # No keys should be valid
        for key in keys:
            assert not self.cache_manager.is_valid(key)
    
    def test_expiration(self, monkeypatch):
        """Test cache expiration."""
        # Test data
        key = "test_key"
        value = {"data": "test_value"}
        
        # Mock time.time to return a fixed timestamp
        monkeypatch.setattr(time, 'time', lambda: 1000)
        
        # Set the value in cache
        self.cache_manager.set(key, value)
        
        # Key should be valid
        assert self.cache_manager.is_valid(key)
        
        # Advance time by 8 days (duration is 7 days)
        monkeypatch.setattr(time, 'time', lambda: 1000 + 8 * 24 * 60 * 60)
        
        # Key should now be expired
        assert not self.cache_manager.is_valid(key)
        
        # Getting the value should return None
        assert self.cache_manager.get(key) is None
