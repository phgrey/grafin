# GraphIn

**GraphIn** is a framework-agnostic, manifest-driven execution graph engine for building, running, and managing AI agent workflows across **LangGraph**, **CrewAI**, and **Semantic Kernel** (Python).

Graph workflows are defined in the **`GraphInYAML`** format (`graphin.yaml` or `*.graphin.yaml`).

## Features

- **Semantic Markdown Chunking**: Parses `.md` documents by headings, paragraphs, and sense.
- **STEM Taxonomy Tagging**: Classifies chunks into Science, Technology, Engineering, and Mathematics fields with reasoning and confidence scores.
- **Dual LLM Provider Support**: Supports **Google Gemini 1.5** (`GEMINI_API_KEY`) and **Ollama** (`OLLAMA_API_KEY` / local endpoint).
- **Human-in-the-Loop (HITL) Interrupts**: Graph execution automatically pauses when classification confidence is below a configurable threshold, prompting user confirmation/override in the terminal before resuming.
- **Structured Results Output**: Exports tagged markdown documents with detailed YAML frontmatter and JSON metadata.

## Setup

```bash
# Initialize virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e ".[dev]"
```

## Environment Variables

Copy `.env.example` to `.env` and set your API keys:

```bash
cp .env.example .env
```

```env
GEMINI_API_KEY=your_gemini_api_key_here
OLLAMA_API_KEY=your_ollama_api_key_here
OLLAMA_BASE_URL=http://localhost:11434
```

## Usage

Run the graph processor on the source directory:

```bash
mac-graph process --source-dir data/source --output-dir data/results --confidence-threshold 0.75 --provider gemini
```

Or run with Ollama:

```bash
mac-graph process --provider ollama --ollama-model llama3.1
```
