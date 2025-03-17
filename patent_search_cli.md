# Patent Novelty Analyzer: Enhanced Development Roadmap

## Project Progress Log

```
Project: Patent Novelty Analyzer
Start Date: May 17, 2023
Status: In Progress

Key Milestones:
- Environment Setup: Completed
- Ollama Integration: Completed
- SerpApi Google Patents Integration: Not Started
- Brave Search API Integration: Not Started
- Claude API Integration: Not Started
- CLI Interface: Partially Implemented
- Error Handling: Partially Implemented
- Performance Optimization: Not Started
- Testing & Documentation: Partially Implemented
```

## Phase 1: Environment Setup and Project Structure

### 1.1 Create Project Directory and Virtual Environment (Estimated time: 1 day)

1. Create a new directory for the project:
   ```
   mkdir patent-novelty-analyzer
   cd patent-novelty-analyzer
   ```

2. Set up a Python 3.10+ virtual environment:
   ```
   python3.10 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Create the following directory structure:
   ```
   patent-novelty-analyzer/
   ├── src/
   │   ├── __init__.py
   │   ├── __main__.py
   │   ├── keyword_extractor.py
   │   ├── patent_searcher.py
   │   ├── web_searcher.py
   │   ├── novelty_analyzer.py
   │   ├── cli.py
   │   └── utils/
   │       ├── __init__.py
   │       ├── config.py
   │       ├── cache.py
   │       └── error_handler.py
   ├── tests/
   │   ├── __init__.py
   │   ├── test_keyword_extractor.py
   │   ├── test_patent_searcher.py
   │   ├── test_web_searcher.py
   │   ├── test_novelty_analyzer.py
   │   ├── test_cli.py
   │   └── test_utils.py
   ├── config/
   │   └── config.yaml
   ├── .env.example
   ├── requirements.txt
   ├── setup.py
   ├── README.md
   └── .gitignore
   ```

**Testing**: Verify the virtual environment is activated by running `python -V` and checking the installation path.

### 1.2 Install Base Dependencies (Estimated time: 0.5 days)

Create `requirements.txt` with the following specific versions:

```
python-dotenv==1.0.0
requests==2.31.0
anthropic==0.5.0
click==8.1.3
pytest==7.3.1
rich==13.3.5
pyyaml==6.0
tenacity==8.2.2
google-search-results==2.4.2
pytest-mock==3.10.0
pytest-cov==4.1.0
```

Install dependencies:
```
pip install -r requirements.txt
```

**Testing**: Verify all packages installed correctly with `pip list`.

### 1.3 Set Up Configuration Management (Estimated time: 1 day)

1. Create a comprehensive `config.yaml` template:

```yaml
# Application Settings
app:
  name: "Patent Novelty Analyzer"
  version: "0.1.0"

# API Keys (will be overridden by environment variables)
api_keys:
  serpapi: null
  brave: null
  anthropic: null

# Ollama Settings
ollama:
  model: "llama2"
  api_url: "http://localhost:11434/api"
  temperature: 0.1
  max_tokens: 1000
  timeout: 30

# SerpApi Settings
serpapi:
  engine: "google_patents"
  results_limit: 2
  patent_years: 30
  country: "US"
  timeout: 30

# Brave Search Settings
brave:
  results_limit: 2
  search_focus: "products_services"
  timeout: 30

# Claude API Settings
claude:
  model: "claude-3-opus-20240229"
  temperature: 0.2
  max_tokens: 4000
  timeout: 60

# Cache Settings
cache:
  enabled: true
  duration_days: 7
  location: ".cache"

# Output Settings
output:
  simple_score_range: [1, 10]
  formats: ["text", "markdown", "json"]
```

2. Create `.env.example` file:

```
# API Keys
SERPAPI_API_KEY=your_serpapi_key_here
BRAVE_API_KEY=your_brave_api_key_here
ANTHROPIC_API_KEY=your_claude_api_key_here

# Optional Overrides
OLLAMA_MODEL=llama2
CACHE_DURATION_DAYS=7
PATENT_SEARCH_YEARS=30
RESULTS_LIMIT=2
```

3. Implement `src/utils/config.py`:
   - Create `ConfigLoader` class that loads from YAML
   - Override with environment variables using python-dotenv
  │   - Validate required settings like API keys
  │   - Provide getter methods for accessing nested configuration

**Testing**: Create `tests/test_utils.py` with tests for:
- Loading config from YAML
- Environment variable overrides
- Required settings validation
- Accessing nested configuration values

### 1.4 Create Initial Project Structure (Estimated time: 1 day)

1. Create minimalist placeholder files for all modules to establish structure
2. Implement `__main__.py` as entry point:
   - Import CLI class
   - Set up basic argument structure
   - Execute main CLI entrypoint

3. Create `setup.py` for package installation:
   - Name: patent-novelty-analyzer
   - Entry points for CLI command
   - Dependencies matching requirements.txt
   - README reference

**Testing**: Verify project structure can be imported without errors.

## Phase 2: Implementing Local Model Integration (Ollama) (Estimated time: 3 days)

### 2.1 Set Up Ollama Client

1. Implement `OllamaClient` class in `src/keyword_extractor.py`:
   ```python
   class OllamaClient:
       def __init__(self, config):
           self.api_url = config.get("ollama.api_url")
           self.model = config.get("ollama.model")  # Should be llama2
           self.temperature = config.get("ollama.temperature")
           self.max_tokens = config.get("ollama.max_tokens")
           self.timeout = config.get("ollama.timeout")
   ```

2. Implement methods:
   - `is_available()`: Check if Ollama service is running
   - `generate_completion(prompt)`: Send prompt to Ollama API
   - `_handle_response(response)`: Extract text from response

3. Add retry mechanism using tenacity:
   - Retry on connection errors
   - Exponential backoff starting at 1 second
   - Maximum 3 retries

**Testing**: Write unit tests mocking Ollama API responses and ensuring proper error handling.

### 2.2 Implement Keyword Extraction

1. Create the `KeywordExtractor` class:
   ```python
   class KeywordExtractor:
       def __init__(self, config, ollama_client):
           self.ollama_client = ollama_client
           self.keyword_count = 10  # Extract more than needed, filter later
   ```

2. Create patent-focused prompt template:
   ```
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
   ```

3. Implement extraction method with error handling

**Testing**: Test with diverse inputs, including technical ideas, simple concepts, and edge cases.

### 2.3 Implement Keyword Validation and Cleaning

1. Add methods to process extracted keywords:
   - `clean_keywords(keywords)`: Remove punctuation, normalize case
   - `filter_keywords(keywords)`: Remove common words, duplicates
   - `validate_keywords(keywords)`: Ensure meaningful keywords remain
   - `format_for_search(keywords)`: Format for API consumption

2. Create fallback keyword lists for common technology domains

**Testing**: Test cleaning logic with various keyword outputs, including edge cases.

## Phase 3: Implementing SerpApi Google Patents Integration (Estimated time: 3 days)

### 3.1 Create SerpApi Client

1. Implement `SerpApiClient` class in `src/patent_searcher.py`:
   ```python
   class SerpApiClient:
       def __init__(self, config):
           self.api_key = config.get("api_keys.serpapi")
           self.engine = config.get("serpapi.engine")
           self.timeout = config.get("serpapi.timeout")
           self.results_limit = config.get("serpapi.results_limit")
   ```

2. Implement methods:
   - `validate_credentials()`: Check API key
   - `build_search_params(keywords)`: Create SerpApi parameters

**Testing**: Write tests verifying parameter building with different keyword inputs.

### 3.2 Implement Patent Search

1. Create `PatentSearcher` class with search configuration:
   - Set search timeframe to 30 years
   - Limit to US patents
   - Return top 2 most relevant results

2. Implement `search_patents(keywords)` method:
   - Build search query from keywords
   - Execute search via SerpApi
   - Parse and validate results
   - Handle API errors with appropriate retries

3. Create parser for patent results to extract:
   - Patent title
   - Patent number
   - Filing date
   - Inventors
   - Abstract
   - Link to patent
   - Key claims/excerpts

**Testing**: Create tests with mock SerpApi responses, including various result formats.

### 3.3 Implement Patent Result Formatter

1. Implement `format_patent_results(patents)` method:
   - Format consistently for Claude analysis
   - Include critical patent information
   - Structure for easy comparison

2. Create a `summarize_patent(patent, max_length)` method for lengthy patents

**Testing**: Verify formatter handles different patent responses correctly.

## Phase 4: Implementing Brave Search API Integration (Estimated time: 3 days)

### 4.1 Create Brave Search Client

1. Implement `BraveSearchClient` class in `src/web_searcher.py`:
   ```python
   class BraveSearchClient:
       def __init__(self, config):
           self.api_key = config.get("api_keys.brave")
           self.timeout = config.get("brave.timeout")
           self.results_limit = config.get("brave.results_limit")
           self.search_focus = config.get("brave.search_focus")
   ```

2. Implement API communication methods:
   - `validate_credentials()`: Verify API key
   - `build_search_params(keywords)`: Create search parameters focused on products/services

**Testing**: Verify parameter building and credential validation.

### 4.2 Implement Web Search

1. Create `WebSearcher` class:
   ```python
   class WebSearcher:
       def __init__(self, config, brave_client):
           self.brave_client = brave_client
           self.config = config
   ```

2. Implement `search_web(keywords)` method:
   - Construct search query optimized for finding products/services
   - Add query modifiers like "product", "service", "available"
   - Process results to extract relevant data

3. Implement response parsing to extract:
   - Title
   - URL
   - Description
   - Source/brand information
   - Publication date

**Testing**: Test with mock Brave Search responses and verify parsing logic.

### 4.3 Implement Web Result Formatter

1. Create `format_web_results(results)` method:
   - Format data for Claude analysis
   - Structure information about existing products
   - Extract pricing/availability when present

2. Implement content extraction logic for most relevant parts

**Testing**: Verify formatter handles various web result formats correctly.

## Phase 5: Implementing Claude API Integration (Estimated time: 4 days)

### 5.1 Create Claude API Client

1. Implement `ClaudeClient` class in `src/novelty_analyzer.py`:
   ```python
   class ClaudeClient:
       def __init__(self, config):
           self.api_key = config.get("api_keys.anthropic")
           self.model = config.get("claude.model")
           self.temperature = config.get("claude.temperature")
           self.max_tokens = config.get("claude.max_tokens")
           self.timeout = config.get("claude.timeout")
   ```

2. Implement methods:
   - `validate_credentials()`: Check API key
   - `generate_analysis(user_prompt, system_prompt)`: Send prompt to Claude

**Testing**: Test with mock Claude API responses for various prompt inputs.

### 5.2 Implement Novelty Analysis

1. Create `NoveltyAnalyzer` class:
   ```python
   class NoveltyAnalyzer:
       def __init__(self, config, claude_client):
           self.claude_client = claude_client
           self.config = config
           self.score_range = config.get("output.simple_score_range")
   ```

2. Implement system prompt for novelty analysis:
   ```
   You are a patent and product novelty analyzer. Your task is to analyze a user's idea and compare it against existing patents and products to determine novelty.

   Analyze the following:
   1. How similar is the user's idea to the existing patents/products?
   2. What unique aspects does the user's idea have?
   3. What common elements exist between the idea and existing items?
   4. How technically feasible is the user's idea?
   5. Assign a novelty score from {min_score} to {max_score}, where {min_score} means "already exists" and {max_score} means "completely novel".

   Provide your analysis in {output_format} format.
   ```

3. Create two analysis methods:
   - `generate_simple_analysis(idea, patents, web_results)`: Return score 1-10 with brief explanation
   - `generate_complex_analysis(idea, patents, web_results)`: Detailed analysis with tables and scores

**Testing**: Test with various combinations of ideas, patents, and web results.

### 5.3 Implement Analysis Result Formatter

1. Create formatters for different output types:
   - `format_simple_analysis(analysis)`: Score with concise explanation 
   - `format_complex_analysis(analysis)`: Executive summary with tables

2. Implement output formats (text, markdown, JSON) based on user preference

**Testing**: Verify formatters produce correct output for different analysis types.

## Phase 6: Building the CLI Interface (Estimated time: 3 days)

### 6.1 Set Up CLI Framework

1. Implement CLI using Click in `src/cli.py`:
   ```python
   class PatentAnalyzerCLI:
       def __init__(self, config):
           self.config = config
   ```

2. Configure base CLI options:
   - Verbosity levels (--verbose, --quiet)
   - Output format (--format [text|markdown|json])
   - Config file path (--config)

**Testing**: Verify CLI initialization and option parsing.

### 6.2 Implement Main Command

1. Create `analyze` command:
   ```
   patent-novelty-analyzer analyze [OPTIONS] [IDEA]
   ```

2. Implement options:
   - `--idea-file`: Load idea from file
   - `--output-file`: Save results to file
   - `--analysis-type`: Simple or complex analysis
   - `--keywords`: Manually specify keywords

3. Create progress display with Rich:
   - Show spinner during API calls
   - Display extracted keywords
   - Show progress through pipeline stages

**Testing**: Test command with various option combinations.

### 6.3 Implement Interactive Mode

1. Create `interactive` command:
   ```
   patent-novelty-analyzer interactive
   ```

2. Implement flow:
   - Prompt for idea text
   - Show and allow editing of extracted keywords
   - Display search progress
   - Allow choosing simple/complex analysis
   - Present results with highlighting

**Testing**: Test interactive mode with various user inputs.

### 6.4 Implement Result Viewing and Export

1. Create formatters for different output types:
   - Text (for terminal)
   - Markdown (for documentation)
   - JSON (for programmatic use)

2. Implement save options:
   - Save to file with timestamp
   - Specify custom filename
   - Auto-generate filename based on idea

**Testing**: Verify export functionality with different formats.

## Phase 7: Error Handling and Resilience (Estimated time: 2 days)

### 7.1 Implement Global Exception Handling

1. Create custom exceptions in `src/utils/error_handler.py`:
   - `APIConnectionError`: For API connection issues
   - `APIAuthenticationError`: For authentication failures
   - `APIRateLimitError`: For rate limiting issues
   - `InputValidationError`: For invalid user input
   - `ConfigurationError`: For missing/invalid configuration

2. Implement global exception handler for CLI

**Testing**: Trigger various exceptions and verify handling.

### 7.2 Implement Retry Logic

1. Configure retry policies with tenacity:
   - SerpApi: 3 retries, 2-second initial delay
   - Brave Search: 3 retries, 2-second initial delay
   - Claude: 2 retries, 5-second initial delay
   - Ollama: 3 retries, 1-second initial delay

2. Implement exponential backoff with jitter

**Testing**: Simulate network failures and verify retry behavior.

### 7.3 Implement Graceful Degradation

1. Update the main processing pipeline to handle partial results:
   - Continue if Ollama keyword extraction fails (use backup keywords)
   - Continue if only one API (SerpApi or Brave) succeeds
   - Wait for confirmed API failure before proceeding with partial results
   - Clearly indicate missing components in final report

2. Implement feature flags to selectively disable components

**Testing**: Test pipeline with various failure scenarios.

## Phase 8: Performance Optimization (Estimated time: 2 days)

### 8.1 Implement Caching

1. Create `CacheManager` in `src/utils/cache.py`:
   ```python
   class CacheManager:
       def __init__(self, config):
           self.enabled = config.get("cache.enabled")
           self.location = config.get("cache.location")
           self.duration_days = config.get("cache.duration_days")  # 7 days
   ```

2. Implement cache operations:
   - `get(key)`: Retrieve cached item
   - `set(key, value)`: Store item in cache
   - `is_valid(key)`: Check if item exists and is not expired
   - `invalidate(key)`: Remove item from cache
   - `clear()`: Clear entire cache

3. Cache implementation:
   - Use filesystem-based cache with JSON serialization
   - Store timestamps with cached data
   - Auto-invalidate after 7 days

**Testing**: Test cache operations, especially expiration behavior.

### 8.2 Implement Parallel Processing

1. Use `concurrent.futures` for parallel API calls:
   - Patent search and web search in parallel
   - Multiple keyword searches in parallel when appropriate

2. Implement task coordinator to manage parallel operations

**Testing**: Verify parallel execution and measure performance improvement.

### 8.3 Implement Resource Management

1. Add API rate limiting compliance:
   - Track API call timestamps
   - Enforce minimum delay between calls
   - Batch requests when possible

2. Implement timeout handling for all API calls

**Testing**: Verify rate limiting and timeout behavior.

## Phase 9: Final Testing and Documentation (Estimated time: 3 days)

### 9.1 Conduct Integration Testing

1. Create end-to-end test scenarios:
   - Simple idea, expecting high novelty
   - Common idea, expecting low novelty
   - Technical idea with specific domain terminology
   - Idea with obvious existing patents

2. Implement integration test suite

**Testing**: Execute integration tests with real API endpoints.

### 9.2 Conduct User Acceptance Testing

1. Create test script with diverse scenarios:
   - Simple consumer product idea
   - Complex software algorithm idea
   - Mechanical device improvement
   - Service-based business concept

2. Have test users evaluate the application

**Testing**: Gather feedback and make necessary adjustments.

### 9.3 Create Comprehensive Documentation

1. Create detailed README.md:
   - Installation instructions
   - Configuration guide
   - Usage examples with screenshots
   - API key acquisition instructions
   - Troubleshooting section

2. Create developer documentation:
   - Architecture diagram
   - Module descriptions
   - Extension points
   - Testing instructions

**Testing**: Have a new user follow documentation to verify clarity.

### 9.4 Finalize Release Preparation

1. Create version 0.1.0 release:
   - Verify all tests pass
   - Generate requirements.txt with exact versions
   - Create distributable package
   - Document known limitations

2. Prepare contribution guidelines

**Testing**: Install package in clean environment and verify functionality.

---

## Progress Tracking Approach

Maintain the Project Progress Log at the top of this document, updating after completing each phase. For each component, record:

1. Completion status (Not Started, In Progress, Completed)
2. Start/completion dates
3. Any blockers encountered
4. Testing results summary

## Software Requirements

- Python 3.10+
- Ollama 0.1.14+ running locally with llama2 model
- SerpApi account with Google Patents access
- Brave Search API key
- Anthropic API key with Claude 3 Opus access
- Disk space: Minimum 500MB (including model cache)
- Memory: Minimum 8GB RAM

## Implementation Notes

1. **Keyword Extraction**: Focus on patent-specific terminology that will yield relevant search results rather than generic terms. The prompt should explicitly ask for technical terms useful for patent searches.

2. **Patent Search Focus**: Focus on US patents from the last 30 years, returning the top 2 most relevant results.

3. **Brave Search Strategy**: Optimize queries to find existing products and services related to the user's idea.

4. **Novelty Analysis Approach**: Claude will assess similarity between the user's idea and existing patents/products, providing a novelty score and detailed analysis.

5. **Output Formats**: Implement both simple (1-10 score with brief explanation) and complex (executive summary with scores and tables) output options.

6. **Error Handling**: Continue processing with partial results if one API fails, but clearly indicate missing components in the final report. Wait for confirmed API failure before proceeding.

7. **Caching**: Cache all API results for 7 days to improve performance and reduce API costs.

8. **Authentication**: Use .env file for API key management, with config.yaml for other settings.

The modular architecture allows easy extension with additional search engines or analysis capabilities in future versions.