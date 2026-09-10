#!/usr/bin/env python3
"""
Main test runner for Ollama model evaluation.
"""

import subprocess
import time
import json
from typing import Dict, List, Any
from model_manager import ModelManager

class TestRunner:
    def __init__(self):
        self.model_manager = ModelManager()
    
    def run_performance_test(self, model_name: str, prompt: str) -> Dict[str, Any]:
        """Run a performance test on the specified model."""
        # Load model if needed
        if not self.model_manager.is_model_loaded(model_name):
            if not self.model_manager.load_model(model_name):
                return {"error": "Failed to load model"}
        
        # Measure response time
        start_time = time.time()
        
        try:
            result = subprocess.run(
                ["ollama", "run", model_name, prompt],
                capture_output=True,
                text=True,
                timeout=60  # 60 second timeout
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            return {
                "model": model_name,
                "response_time": response_time,
                "status_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0
            }
            
        except subprocess.TimeoutExpired:
            return {"error": "Timeout occurred"}
        except Exception as e:
            return {"error": str(e)}
    
    def run_quality_test(self, model_name: str, prompt: str, iterations: int = 3) -> Dict[str, Any]:
        """Run quality test with repeated prompts to measure consistency."""
        if not self.model_manager.is_model_loaded(model_name):
            if not self.model_manager.load_model(model_name):
                return {"error": "Failed to load model"}
        
        responses = []
        times = []
        
        for i in range(iterations):
            start_time = time.time()
            try:
                result = subprocess.run(
                    ["ollama", "run", model_name, prompt],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                end_time = time.time()
                
                responses.append(result.stdout)
                times.append(end_time - start_time)
                
            except Exception as e:
                return {"error": str(e)}
        
        # Calculate consistency score (simple approach: count unique responses)
        unique_responses = len(set(responses))
        consistency_score = unique_responses / iterations if iterations > 0 else 0
        
        return {
            "model": model_name,
            "iterations": iterations,
            "avg_response_time": sum(times) / len(times) if times else 0,
            "consistency_score": consistency_score,
            "responses": responses,
            "success": True
        }
    
    def run_comprehensive_test(self, model_name: str) -> Dict[str, Any]:
        """Run a comprehensive test suite for a single model."""
        print(f"Running comprehensive tests for {model_name}")
        
        # Performance test
        perf_result = self.run_performance_test(model_name, "What is 2+2?")
        
        # Quality test
        quality_result = self.run_quality_test(model_name, "Explain quantum computing in simple terms.", 3)
        
        # Cleanup
        self.model_manager.unload_model()
        
        return {
            "model": model_name,
            "performance": perf_result,
            "quality": quality_result
        }

if __name__ == "__main__":
    runner = TestRunner()
    
    # Get available models
    models = runner.model_manager.get_available_models()
    
    if not models:
        print("No models found in Ollama")
    else:
        results = []
        for model in models:
            model_name = model['name']
            result = runner.run_comprehensive_test(model_name)
            results.append(result)
            print(f"Tested {model_name}: Success={result.get('performance', {}).get('success', False)}")
        
        # Save results to file
        with open("test_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        print("Test results saved to test_results.json")