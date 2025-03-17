# 🚀 Patent Novelty Analyzer

A powerful CLI tool that helps inventors and researchers assess the novelty of patent ideas by comparing against existing patents and products using AI-powered analysis.

## ✨ Features

- 🔍 **Intelligent Keyword Extraction** - Automatically identify relevant keywords from your patent idea using Ollama (local LLM)
- 🔎 **Patent Database Search** - Search for similar existing patents using Google Patents API
- 🌐 **Product Search** - Discover existing commercial products using Brave Search API
- 🧠 **AI-Powered Analysis** - Get comprehensive novelty assessments using Claude 3 Opus
- 📊 **Flexible Output** - View results in text, markdown, or JSON format

## 📋 Requirements

- Python 3.10+
- Ollama with llama2 model (for local keyword extraction)
- API keys for SerpApi, Brave Search, and Anthropic

## 🔧 Installation

### Option 1: Install from PyPI (Coming Soon)
```bash
pip install patent-novelty-analyzer
```

### Option 2: Install from Source
```bash
# Clone the repository
git clone https://github.com/pkells12/novelty_assessment_cli.git
cd novelty_assessment_cli

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate

# Install as a package (recommended)
pip install -e .
```

## ⚙️ Configuration

1. Copy the example environment file and edit it with your API keys:
```bash
cp .env.example .env
```

2. Add your API keys to the `.env` file:
   - `SERPAPI_API_KEY`: Get from [SerpApi](https://serpapi.com/)
   - `BRAVE_API_KEY`: Get from [Brave Search API](https://brave.com/search/api/)
   - `ANTHROPIC_API_KEY`: Get from [Anthropic](https://www.anthropic.com/)

3. Install and run Ollama with the llama2 model:
```bash
# Install Ollama from https://ollama.com/
ollama pull llama2
```

## 🚀 Usage Examples

### Basic Analysis
Analyze a patent idea directly from the command line:
```bash
patent-novelty-analyzer analyze "A system for generating electricity using piezoelectric materials embedded in sidewalks"
```

### Using a File for Input
```bash
patent-novelty-analyzer analyze --idea-file my_patent_idea.txt
```

### Providing Custom Keywords
Skip the automatic keyword extraction by providing your own keywords:
```bash
patent-novelty-analyzer analyze "My solar panel innovation" --keywords "photovoltaic, efficiency, nano-coating, durability"
```

### Save Results to a File
```bash
patent-novelty-analyzer analyze "My patent idea" --output-file analysis_results.md --format markdown
```

### Choose Analysis Complexity
```bash
patent-novelty-analyzer analyze "My patent idea" --analysis-type complex
```

### Interactive Mode
Work through the analysis process step by step:
```bash
patent-novelty-analyzer interactive
```

## 📚 Command Options

```
analyze [IDEA]           Analyze a patent idea for novelty
  --idea-file FILE       Load patent idea from a file
  --output-file FILE     Save results to a file
  --analysis-type TYPE   Choose analysis complexity [simple|complex]
  --format FORMAT        Output format [text|markdown|json]
  --keywords KEYWORDS    Comma-separated list of keywords to use for search

interactive              Start an interactive analysis session
```

## 🧪 Development

Run tests:
```bash
pytest
```

## 📄 License

MIT 