import os
import yaml
from dotenv import load_dotenv
from pathlib import Path


class ConfigLoader:
    """Configuration loader for Patent Novelty Analyzer.
    
    Loads configuration from YAML file and overrides with environment variables.
    """
    
    def __init__(self, config_path=None):
        """Initialize the ConfigLoader.
        
        Args:
            config_path (str, optional): Path to the config.yaml file.
                If None, will look in the default location.
        """
        # Default config path is in the config directory
        if config_path is None:
            base_dir = Path(__file__).resolve().parent.parent.parent
            config_path = base_dir / "config" / "config.yaml"
        
        self.config_path = config_path
        self.config = {}
        
        # Load environment variables
        load_dotenv()
        
        # Load configuration
        self._load_config()
        self._override_with_env()
        self._validate_config()
    
    def _load_config(self):
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, 'r') as file:
                self.config = yaml.safe_load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing config file: {e}")
    
    def _override_with_env(self):
        """Override configuration with environment variables."""
        # API Keys
        if os.getenv("SERPAPI_API_KEY"):
            self.set("api_keys.serpapi", os.getenv("SERPAPI_API_KEY"))
        
        if os.getenv("BRAVE_API_KEY"):
            self.set("api_keys.brave", os.getenv("BRAVE_API_KEY"))
        
        if os.getenv("ANTHROPIC_API_KEY"):
            self.set("api_keys.anthropic", os.getenv("ANTHROPIC_API_KEY"))
        
        # Optional Overrides
        if os.getenv("OLLAMA_MODEL"):
            self.set("ollama.model", os.getenv("OLLAMA_MODEL"))
        
        if os.getenv("CACHE_DURATION_DAYS"):
            self.set("cache.duration_days", int(os.getenv("CACHE_DURATION_DAYS")))
        
        if os.getenv("PATENT_SEARCH_YEARS"):
            self.set("serpapi.patent_years", int(os.getenv("PATENT_SEARCH_YEARS")))
        
        if os.getenv("RESULTS_LIMIT"):
            self.set("serpapi.results_limit", int(os.getenv("RESULTS_LIMIT")))
            self.set("brave.results_limit", int(os.getenv("RESULTS_LIMIT")))
    
    def _validate_config(self):
        """Validate that required configuration is present."""
        # These will be required when we use the respective services
        # For now, we'll just log warnings if they're missing
        missing = []
        
        # For Phase 3: SerpApi
        if not self.get("api_keys.serpapi"):
            missing.append("SERPAPI_API_KEY")
        
        # For Phase 4: Brave Search
        if not self.get("api_keys.brave"):
            missing.append("BRAVE_API_KEY")
        
        # For Phase 5: Claude
        if not self.get("api_keys.anthropic"):
            missing.append("ANTHROPIC_API_KEY")
        
        if missing:
            print(f"Warning: The following API keys are missing: {', '.join(missing)}")
            print("Some functionality may be limited.")
    
    def get(self, key_path, default=None):
        """Get a configuration value by its key path.
        
        Args:
            key_path (str): Dot-separated path to the config value.
            default: Value to return if the key is not found.
        
        Returns:
            The configuration value, or default if not found.
        """
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, key_path, value):
        """Set a configuration value by its key path.
        
        Args:
            key_path (str): Dot-separated path to the config value.
            value: Value to set.
        """
        keys = key_path.split('.')
        current = self.config
        
        # Navigate to the right depth
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # Set the value
        current[keys[-1]] = value
