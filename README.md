# Ollama Model Testing Framework

A framework for testing locally hosted Ollama models while respecting VRAM constraints (only one model at a time).

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

## Requirements
- Python 3.7+
- Ollama installed and running locally
- Models available in Ollama

## Files
- `test_framework.py` - Main test runner and framework
- `model_manager.py` - Handles model loading/unloading operations
- `test_runner.py` - Additional test execution utilities