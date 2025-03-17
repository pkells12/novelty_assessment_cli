"""
Cache management utilities for Patent Novelty Analyzer.
"""

import os
import json
import time
import hashlib
from pathlib import Path
from datetime import datetime, timedelta


class CacheManager:
    """Manager for caching API responses."""
    
    def __init__(self, config):
        """Initialize the CacheManager.
        
        Args:
            config: Configuration object.
        """
        self.enabled = config.get("cache.enabled", True)
        self.location = config.get("cache.location", ".cache")
        self.duration_days = config.get("cache.duration_days", 7)
        
        # Create cache directory if it doesn't exist
        if self.enabled:
            os.makedirs(self.location, exist_ok=True)
    
    def _get_cache_key(self, key):
        """Generate a cache key from a string.
        
        Args:
            key: String to generate cache key from.
        
        Returns:
            str: Cache key as a hex digest.
        """
        return hashlib.md5(key.encode('utf-8')).hexdigest()
    
    def _get_cache_path(self, key):
        """Get the file path for a cache key.
        
        Args:
            key: Cache key.
        
        Returns:
            Path: Path to cache file.
        """
        return Path(self.location) / f"{self._get_cache_key(key)}.json"
    
    def get(self, key):
        """Get a value from the cache.
        
        Args:
            key: Cache key.
        
        Returns:
            The cached value, or None if not found or expired.
        """
        if not self.enabled:
            return None
        
        cache_path = self._get_cache_path(key)
        
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, 'r') as f:
                cache_data = json.load(f)
            
            # Check if cache is expired
            timestamp = cache_data.get('timestamp', 0)
            now = time.time()
            age_days = (now - timestamp) / (60 * 60 * 24)
            
            if age_days > self.duration_days:
                # Cache is expired, remove it
                self.invalidate(key)
                return None
            
            return cache_data.get('value')
        
        except (json.JSONDecodeError, KeyError):
            # Cache file is corrupted, remove it
            self.invalidate(key)
            return None
    
    def set(self, key, value):
        """Set a value in the cache.
        
        Args:
            key: Cache key.
            value: Value to cache.
        """
        if not self.enabled:
            return
        
        cache_path = self._get_cache_path(key)
        
        cache_data = {
            'timestamp': time.time(),
            'value': value
        }
        
        with open(cache_path, 'w') as f:
            json.dump(cache_data, f)
    
    def is_valid(self, key):
        """Check if a cache key exists and is not expired.
        
        Args:
            key: Cache key.
        
        Returns:
            bool: True if cache is valid, False otherwise.
        """
        if not self.enabled:
            return False
        
        cache_path = self._get_cache_path(key)
        
        if not cache_path.exists():
            return False
        
        try:
            with open(cache_path, 'r') as f:
                cache_data = json.load(f)
            
            # Check if cache is expired
            timestamp = cache_data.get('timestamp', 0)
            now = time.time()
            age_days = (now - timestamp) / (60 * 60 * 24)
            
            return age_days <= self.duration_days
        
        except (json.JSONDecodeError, KeyError):
            return False
    
    def invalidate(self, key):
        """Remove a key from the cache.
        
        Args:
            key: Cache key.
        """
        if not self.enabled:
            return
        
        cache_path = self._get_cache_path(key)
        
        if cache_path.exists():
            try:
                os.remove(cache_path)
            except OSError:
                pass
    
    def clear(self):
        """Clear all cached items."""
        if not self.enabled:
            return
        
        for cache_file in Path(self.location).glob('*.json'):
            try:
                os.remove(cache_file)
            except OSError:
                pass
