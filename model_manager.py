#!/usr/bin/env python3
"""
Model manager for Ollama testing framework.
Handles model loading, unloading, and state management.
"""

import subprocess
import json
import time
from typing import List, Dict, Optional

class ModelManager:
    def __init__(self):
        self.current_model = None
    
    def get_available_models(self) -> List[Dict]:
        """Get list of available models from Ollama."""
        try:
            result = subprocess.run(
                ["ollama", "list", "--json"],
                capture_output=True,
                text=True,
                check=True
            )
            models = json.loads(result.stdout)
            return models.get("models", [])
        except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
            print(f"Error getting models: {e}")
            return []
    
    def load_model(self, model_name: str) -> bool:
        """Load a specific model."""
        if self.current_model == model_name:
            return True
            
        try:
            # First unload current model
            if self.current_model:
                subprocess.run(["ollama", "unload", self.current_model], 
                             capture_output=True, check=True)
            
            # Load new model
            result = subprocess.run(
                ["ollama", "run", model_name, "ping"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                self.current_model = model_name
                return True
            else:
                print(f"Failed to load model {model_name}: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"Timeout loading model {model_name}")
            return False
        except Exception as e:
            print(f"Error loading model {model_name}: {e}")
            return False
    
    def unload_model(self) -> bool:
        """Unload current model."""
        if self.current_model:
            try:
                subprocess.run(
                    ["ollama", "unload", self.current_model],
                    capture_output=True,
                    check=True
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