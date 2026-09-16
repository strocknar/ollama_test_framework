#!/usr/bin/env python3
"""
Complete Ollama Model Testing Framework
Demonstrates the concepts for evaluating local Ollama models.
"""

import subprocess
import time
import json
from typing import List, Dict, Any, Optional
import os
from model_manager import ModelManager

class OllamaTestFramework:
    """
    A framework for testing Ollama models with VRAM constraint handling.
    
    This framework is designed to work with the limitation that only one 
    model can be loaded in VRAM at a time, ensuring proper model switching
    and resource management.
    """
    
    def __init__(self, ollama_host: Optional[str] = None):
        self.model_manager = ModelManager(ollama_host)
        self.results = []
        self._env = os.environ.copy()
        if ollama_host:
            self._env['OLLAMA_HOST'] = ollama_host
    
    def get_available_models(self) -> List[Dict]:
        """Get all available Ollama models."""
        return self.model_manager.get_available_models()
    
    def run_model_test_suite(self, model_name: str) -> Dict[str, Any]:
        """
        Run complete test suite for a single model.
        
        This function respects VRAM constraints by:
        1. Loading the specified model
        2. Running all tests sequentially 
        3. Unloading the model when complete
        """
        print(f"Testing model: {model_name}")
        
        try:
            # Test 1: Performance benchmarking
            perf_results = self._run_performance_tests(model_name)
            
            # Test 2: Quality assessment 
            quality_results = self._run_quality_tests(model_name)
            
            # Test 3: Consistency testing
            consistency_results = self._run_consistency_tests(model_name)
            
            # Aggregate results
            final_result = {
                "model": model_name,
                "timestamp": time.time(),
                "performance": perf_results,
                "quality": quality_results,
                "consistency": consistency_results,
                "status": "completed"
            }
            
            self.results.append(final_result)
            return final_result
            
        except Exception as e:
            error_result = {
                "model": model_name,
                "error": str(e),
                "status": "failed"
            }
            self.results.append(error_result)
            return error_result
    
    def _run_performance_tests(self, model_name: str) -> Dict[str, Any]:
        """Performance metrics testing."""
        # Load model if not already loaded
        if not self.model_manager.is_model_loaded(model_name):
            if not self.model_manager.load_model(model_name):
                return {"error": "Failed to load model"}
        
        test_prompts = [
            "What is 2+2?",
            "Explain quantum computing in simple terms.",
            "Write a short poem about AI",
            "List 5 facts about space exploration"
        ]
        
        results = []
        for i, prompt in enumerate(test_prompts):
            start_time = time.time()
            
            try:
                result = subprocess.run(
                    ["ollama", "run", model_name, prompt],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    env=self._env
                )
                
                end_time = time.time()
                response_time = end_time - start_time
                
                results.append({
                    "test_id": i,
                    "prompt": prompt[:50] + "..." if len(prompt) > 50 else prompt,
                    "response_time": response_time,
                    "status_code": result.returncode,
                    "success": result.returncode == 0
                })
                
            except Exception as e:
                results.append({
                    "test_id": i,
                    "prompt": prompt[:50] + "..." if len(prompt) > 50 else prompt,
                    "error": str(e),
                    "success": False
                })
        
        # Calculate average response time
        successful_times = [r["response_time"] for r in results if r.get("success")]
        avg_time = sum(successful_times) / len(successful_times) if successful_times else 0
        
        # Cleanup after performance tests
        self.model_manager.unload_model()
        
        return {
            "test_count": len(test_prompts),
            "average_response_time": avg_time,
            "detailed_results": results
        }
    
    def _run_quality_tests(self, model_name: str) -> Dict[str, Any]:
        """Quality assessment metrics."""
        if not self.model_manager.is_model_loaded(model_name):
            if not self.model_manager.load_model(model_name):
                return {"error": "Failed to load model"}
        
        # Test prompts for quality assessment
        test_prompts = [
            ("Summarize the main points of quantum mechanics in 3 sentences.", "summary"),
            ("What are three key differences between Python and JavaScript?", "comparison"), 
            ("Explain why the sky is blue from a scientific perspective.", "explanation")
        ]
        
        results = []
        for prompt, task_type in test_prompts:
            start_time = time.time()
            
            try:
                result = subprocess.run(
                    ["ollama", "run", model_name, prompt],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    env=self._env
                )
                
                end_time = time.time()
                response_time = end_time - start_time
                
                # Simple quality check (in a real implementation we'd use more sophisticated metrics)
                response_length = len(result.stdout) if result.stdout else 0
                
                results.append({
                    "task_type": task_type,
                    "response_time": response_time,
                    "response_length": response_length,
                    "status_code": result.returncode,
                    "success": result.returncode == 0
                })
                
            except Exception as e:
                results.append({
                    "task_type": task_type,
                    "error": str(e),
                    "success": False
                })
        
        # Cleanup after quality tests
        self.model_manager.unload_model()
        
        return {
            "test_count": len(test_prompts),
            "detailed_results": results
        }
    
    def _run_consistency_tests(self, model_name: str) -> Dict[str, Any]:
        """Consistency and repeatability testing."""
        if not self.model_manager.is_model_loaded(model_name):
            if not self.model_manager.load_model(model_name):
                return {"error": "Failed to load model"}
        
        # Test with same prompt multiple times for consistency
        test_prompt = "What is the capital of France?"
        iterations = 3
        responses = []
        response_times = []
        
        for i in range(iterations):
            start_time = time.time()
            
            try:
                result = subprocess.run(
                    ["ollama", "run", model_name, test_prompt],
                    capture_output=True,
                    text=True,
                    timeout=15,
                    env=self._env
                )
                
                end_time = time.time()
                response_time = end_time - start_time
                
                responses.append(result.stdout.strip() if result.stdout else "")
                response_times.append(response_time)
                
            except Exception as e:
                return {"error": str(e)}
        
        # Calculate consistency (percentage of identical responses)
        unique_responses = len(set(responses))
        consistency_score = 1.0 - (unique_responses / iterations) if iterations > 0 else 1.0
        
        # Cleanup after consistency tests
        self.model_manager.unload_model()
        
        return {
            "test_prompt": test_prompt,
            "iterations": iterations,
            "consistency_score": consistency_score,
            "average_response_time": sum(response_times) / len(response_times) if response_times else 0,
            "responses": responses
        }
    
    def run_all_tests(self) -> List[Dict[str, Any]]:
        """Run tests for all available models."""
        print("Starting comprehensive Ollama model testing...")
        
        models = self.get_available_models()
        if not models:
            print("No models found in Ollama")
            return []
        
        # Test each model sequentially (respects VRAM constraint)
        for model in models:
            model_name = model['name']
            result = self.run_model_test_suite(model_name)
            print(f"Completed testing: {model_name}")
        
        print("All tests completed.")
        return self.results
    
    def save_results(self, filename: str = "ollama_test_results.json") -> None:
        """Save test results to JSON file."""
        if self.results:
            with open(filename, 'w') as f:
                json.dump(self.results, f, indent=2)
            print(f"Results saved to {filename}")

def main():
    """Main execution function."""
    framework = OllamaTestFramework()
    
    # Run all tests
    results = framework.run_all_tests()
    
    # Save results
    if results:
        print("\nSaving results...")
        framework.save_results("ollama_test_results.json")
        
        # Display summary
        print("\n=== TEST RESULTS SUMMARY ===")
        for result in results:
            model_name = result.get("model", "Unknown")
            status = result.get("status", "Unknown")
            perf_time = result.get("performance", {}).get("average_response_time", 0)
            print(f"Model: {model_name} - Status: {status} - Avg Time: {perf_time:.2f}s")

if __name__ == "__main__":
    main()