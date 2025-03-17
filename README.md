# Novelty Assessment CLI

A CLI tool to analyze the novelty of ideas by comparing against existing patents and products.

## Features

- Extract keywords from patent ideas using Ollama (local LLM)
- Search for existing patents using Google Patents via SerpApi (coming soon)
- Search for existing products using Brave Search API (coming soon)
- Analyze novelty using Claude 3 Opus (coming soon)
- Output in text, markdown, or JSON format

## Current Implementation Status

- ✅ Phase 1: Environment Setup and Project Structure
- ✅ Phase 2: Implementing Local Model Integration (Ollama)
- 🔄 Phase 3: Implementing SerpApi Google Patents Integration (in progress)
- ⏳ Phase 4: Implementing Brave Search API Integration (planned)
- ⏳ Phase 5: Implementing Claude API Integration (planned)
- ⏳ Phase 6: Building the CLI Interface (partially implemented)
- ⏳ Phase 7: Error Handling and Resilience (partially implemented)
- ⏳ Phase 8: Performance Optimization (planned)
- ⏳ Phase 9: Final Testing and Documentation (planned)

## Installation

1. Ensure you have Python 3.10+ installed
2. Clone this repository
3. Install requirements:
```
pip install -r requirements.txt
```

## Configuration

1. Copy `.env.example` to `.env` and add your API keys:
```
cp .env.example .env
```
2. Edit `.env` with your API keys:
- SERPAPI_API_KEY: Get from [SerpApi](https://serpapi.com/)
- BRAVE_API_KEY: Get from [Brave Search API](https://brave.com/search/api/)
- ANTHROPIC_API_KEY: Get from [Anthropic](https://www.anthropic.com/)

3. Ensure Ollama is installed and running with the llama2 model:
```
ollama pull llama2
```

## Usage

### Basic Analysis

```
python -m src analyze "My patent idea description"
```

You can also provide keywords directly:
```
python -m src analyze "My patent idea description" --keywords "keyword1, keyword2, keyword3"
```

### Interactive Mode

```
python -m src interactive
```

### Options

- `--idea-file FILE`: Load idea from file
- `--output-file FILE`: Save results to file
- `--analysis-type [simple|complex]`: Choose analysis detail level
- `--format [text|markdown|json]`: Choose output format
- `--keywords`: Comma-separated keywords to use for search

## Development

Run tests:
```
pytest
```

## License

MIT 