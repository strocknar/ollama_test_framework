# Ollama Model Testing Framework

A framework for testing Ollama models while respecting VRAM constraints (only one model at a time).

## Features
- Automated model switching between tests
- Performance benchmarking
- Quality assessment metrics
- Cross-model comparison capabilities
- VRAM management for single-model constraint

## Usage
```bash
python3 test_framework.py
```

The framework will:
1. Detect all available Ollama models
2. Test each model individually (respecting VRAM constraints)
3. Collect comprehensive metrics for each test type
4. Save results to a JSON file for further analysis

## Configuration

### OLLAMA_HOST Configuration
The framework supports connecting to a remote Ollama server:

```bash
# Using environment variable
OLLAMA_HOST=http://your-server:11434 python3 test_framework.py

# Or programmatically
from test_framework import OllamaTestFramework
framework = OllamaTestFramework('http://your-server:11434')
```

## Requirements
- Python 3.7+
- Ollama client installed
- Ollama server running (local or remote)
- Models available in Ollama

## Files
- `test_framework.py` - Main test runner and framework
- `model_manager.py` - Handles model loading/unloading operations
