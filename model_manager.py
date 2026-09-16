#!/usr/bin/env python3
"""
Model manager for Ollama testing framework.
Handles model loading, unloading, and state management.
"""

import subprocess
import json
import time
import os
import re
from typing import List, Dict, Optional

class ModelManager:
    def __init__(self, ollama_host: Optional[str] = None):
        self.current_model = None
        self._env = None
        self.ollama_host = ollama_host or os.environ.get('OLLAMA_HOST', 'http://localhost:11434')
    
    def _ensure_env(self):
        if self._env is None:
            self._env = os.environ.copy()
            self._env['OLLAMA_HOST'] = self.ollama_host
    
    def get_available_models(self) -> List[Dict]:
        """Get list of available models from Ollama."""
        self._ensure_env()
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                env=self._env
            )
            if result.returncode != 0:
                print(f"Error getting models: {result.stderr}")
                return []
            
            lines = result.stdout.strip().split('\n')
            models = []
            for line in lines[1:]:
                parts = line.split()
                if len(parts) >= 5:
                    model_name = parts[0]
                    models.append({"name": model_name, "id": parts[1]})
            return models
        except Exception as e:
            print(f"Error getting models: {e}")
            return []
    
    def load_model(self, model_name: str) -> bool:
        """Load a specific model."""
        if self.current_model == model_name:
            return True
            
        self._ensure_env()
            
        try:
            # First unload current model
            if self.current_model:
                subprocess.run(["ollama", "unload", self.current_model], 
                             capture_output=True, env=self._env)
            
            # Load new model - just check if it exists
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                env=self._env
            )
            
            if model_name in result.stdout:
                self.current_model = model_name
                return True
            else:
                print(f"Model {model_name} not found")
                return False
                
        except Exception as e:
            print(f"Error checking model {model_name}: {e}")
            return False
    
    def unload_model(self) -> bool:
        """Unload current model."""
        if self.current_model:
            try:
                subprocess.run(
                    ["ollama", "unload", self.current_model],
                    capture_output=True,
                    env=self._env
                )
                self.current_model = None
                return True
            except Exception as e:
                print(f"Error unloading model: {e}")
                return False
        return True
    
    def is_model_loaded(self, model_name: str) -> bool:
        """Check if a model is currently loaded."""
        return self.current_model == model_name

if __name__ == "__main__":
    manager = ModelManager()
    models = manager.get_available_models()
    print("Available models:")
    for model in models:
        print(f"  - {model['name']}")