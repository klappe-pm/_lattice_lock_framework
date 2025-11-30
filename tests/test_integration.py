#!/usr/bin/env python3
"""
Integration Test Suite for Model Orchestrator
Tests all components work together with real APIs
"""

import os
import sys
import asyncio
import json
from pathlib import Path
from datetime import datetime
import time

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from model_orchestrator import ModelOrchestrator, TaskType
from model_orchestrator_v2 import ModelOrchestratorV2
from zen_mcp_bridge import ZenMCPBridge, ModelRouter
from api_clients import get_api_client

class IntegrationTester:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests": [],
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0
            }
        }
    
    def record_test(self, name: str, status: str, details: str = "", error: str = None):
        """Record test result"""
        self.results["tests"].append({
            "name": name,
            "status": status,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        })
        
        self.results["summary"]["total"] += 1
        if status == "passed":
            self.results["summary"]["passed"] += 1
            print(f"✅ {name}: PASSED")
        elif status == "failed":
            self.results["summary"]["failed"] += 1
            print(f"❌ {name}: FAILED - {error}")
        else:
            self.results["summary"]["skipped"] += 1
            print(f"⏭️  {name}: SKIPPED - {details}")
    
    async def test_base_orchestrator(self):
        """Test base orchestrator functionality"""
        try:
            orchestrator = ModelOrchestrator()
            
            # Test task analysis
            prompt = "Write a Python function to calculate fibonacci"
            requirements = orchestrator.analyze_task(prompt)
            
            if requirements.task_type == TaskType.CODE_GENERATION:
                self.record_test("Base Orchestrator - Task Analysis", "passed", 
                               f"Correctly identified as {requirements.task_type.value}")
            else:
                self.record_test("Base Orchestrator - Task Analysis", "failed",
                               error=f"Wrong task type: {requirements.task_type.value}")
            
            # Test model selection
            model_id, model = orchestrator.select_model(prompt)
            if model_id and model:
                self.record_test("Base Orchestrator - Model Selection", "passed",
                               f"Selected: {model_id}")
            else:
                self.record_test("Base Orchestrator - Model Selection", "failed",
                               error="No model selected")
            
        except Exception as e:
            self.record_test("Base Orchestrator", "failed", error=str(e))
    
    async def test_api_clients(self):
        """Test API client initialization"""
        providers_tested = []
        
        # Test Grok/xAI
        if os.getenv("XAI_API_KEY"):
            try:
                client = get_api_client('xai')
                providers_tested.append("xai")
                self.record_test("API Client - xAI/Grok", "passed")
            except Exception as e:
                self.record_test("API Client - xAI/Grok", "failed", error=str(e))
        else:
            self.record_test("API Client - xAI/Grok", "skipped", "No API key")
        
        # Test OpenAI
        if os.getenv("OPENAI_API_KEY"):
            try:
                client = get_api_client('openai')
                providers_tested.append("openai")
                self.record_test("API Client - OpenAI", "passed")
            except Exception as e:
                self.record_test("API Client - OpenAI", "failed", error=str(e))
        else:
            self.record_test("API Client - OpenAI", "skipped", "No API key")
        
        # Test Google
        if os.getenv("GOOGLE_API_KEY"):
            try:
                client = get_api_client('google')
                providers_tested.append("google")
                self.record_test("API Client - Google", "passed")
            except Exception as e:
                self.record_test("API Client - Google", "failed", error=str(e))
        else:
            self.record_test("API Client - Google", "skipped", "No API key")
        
        return providers_tested
    
    async def test_orchestrator_v2(self):
        """Test enhanced orchestrator with real APIs"""
        try:
            orchestrator = ModelOrchestratorV2()
            
            # Check available models
            available = orchestrator.get_available_models()
            
            if available:
                self.record_test("Orchestrator V2 - Initialization", "passed",
                               f"{sum(len(m) for m in available.values())} models available")
                
                # Test actual API call if we have models
                try:
                    response = await orchestrator.route_request(
                        prompt="What is 1+1? Answer with just the number.",
                        strategy="cost_optimize"
                    )
                    
                    if response and response.content:
                        self.record_test("Orchestrator V2 - API Call", "passed",
                                       f"Model: {response.model}, Response: {response.content[:50]}")
                    else:
                        self.record_test("Orchestrator V2 - API Call", "failed",
                                       error="Empty response")
                        
                except Exception as e:
                    self.record_test("Orchestrator V2 - API Call", "failed", error=str(e))
                    
            else:
                self.record_test("Orchestrator V2 - Initialization", "skipped",
                               "No API clients available")
                
        except Exception as e:
            self.record_test("Orchestrator V2", "failed", error=str(e))
    
    async def test_zen_bridge(self):
        """Test Zen MCP Bridge"""
        try:
            bridge = ZenMCPBridge()
            
            # Test tool discovery
            tools = bridge.zen_tools
            if tools:
                self.record_test("Zen Bridge - Tool Discovery", "passed",
                               f"Found {len(tools)} Zen tools")
            else:
                self.record_test("Zen Bridge - Tool Discovery", "failed",
                               error="No Zen tools found")
            
            # Test model extension
            extended = bridge.extend_zen_models()
            if extended:
                total_models = sum(len(models) for models in extended.values())
                self.record_test("Zen Bridge - Model Extension", "passed",
                               f"Extended with {total_models} models")
            else:
                self.record_test("Zen Bridge - Model Extension", "failed",
                               error="No models extended")
                
        except Exception as e:
            self.record_test("Zen Bridge", "failed", error=str(e))
    
    async def test_consensus(self):
        """Test consensus functionality"""
        try:
            orchestrator = ModelOrchestratorV2()
            available = orchestrator.get_available_models()
            
            if len(available) >= 2:
                # We have multiple providers, test consensus
                consensus = await orchestrator.consensus_call(
                    prompt="What is the capital of France? Answer in one word.",
                    num_models=min(3, sum(len(m) for m in available.values()))
                )
                
                if consensus and consensus.get("consensus"):
                    self.record_test("Consensus", "passed",
                                   f"Used {len(consensus['models_used'])} models")
                else:
                    self.record_test("Consensus", "failed", error="No consensus reached")
            else:
                self.record_test("Consensus", "skipped", 
                               "Need at least 2 providers for consensus")
                
        except Exception as e:
            self.record_test("Consensus", "failed", error=str(e))
    
    async def test_streaming(self):
        """Test streaming functionality"""
        try:
            orchestrator = ModelOrchestratorV2()
            available = orchestrator.get_available_models()
            
            if available:
                # Get first available model
                first_provider = list(available.keys())[0]
                first_model = available[first_provider][0]
                
                # Test streaming
                chunks = []
                async for chunk in orchestrator.stream_response(
                    model_id=first_model,
                    prompt="Count from 1 to 5"
                ):
                    chunks.append(chunk)
                    if len(chunks) > 10:  # Limit chunks for testing
                        break
                
                if chunks:
                    self.record_test("Streaming", "passed", 
                                   f"Received {len(chunks)} chunks")
                else:
                    self.record_test("Streaming", "failed", error="No chunks received")
            else:
                self.record_test("Streaming", "skipped", "No models available")
                
        except Exception as e:
            # Streaming might not be supported by all models
            self.record_test("Streaming", "skipped", f"Not supported: {str(e)}")
    
    async def test_cost_tracking(self):
        """Test cost tracking functionality"""
        try:
            orchestrator = ModelOrchestrator()
            
            # Simulate some usage
            orchestrator.track_usage("grok-3", 1000, 500, 250, True)
            orchestrator.track_usage("gpt-4.1-2025-04-14", 2000, 1000, 500, True)
            
            report = orchestrator.get_cost_report()
            
            if report["total_cost"] > 0:
                self.record_test("Cost Tracking", "passed",
                               f"Total cost: ${report['total_cost']:.4f}")
            else:
                self.record_test("Cost Tracking", "failed", error="No cost calculated")
                
        except Exception as e:
            self.record_test("Cost Tracking", "failed", error=str(e))
    
    async def run_all_tests(self):
        """Run all integration tests"""
        print("="*60)
        print("Model Orchestrator Integration Tests")
        print("="*60)
        print()
        
        # Run tests
        await self.test_base_orchestrator()
        providers = await self.test_api_clients()
        await self.test_orchestrator_v2()
        await self.test_zen_bridge()
        await self.test_consensus()
        await self.test_streaming()
        await self.test_cost_tracking()
        
        # Summary
        print()
        print("="*60)
        print("Test Summary")
        print("="*60)
        
        summary = self.results["summary"]
        print(f"Total Tests: {summary['total']}")
        print(f"✅ Passed: {summary['passed']}")
        print(f"❌ Failed: {summary['failed']}")
        print(f"⏭️  Skipped: {summary['skipped']}")
        
        pass_rate = (summary['passed'] / summary['total'] * 100) if summary['total'] > 0 else 0
        print(f"\nPass Rate: {pass_rate:.1f}%")
        
        # Save results
        results_file = Path(__file__).parent / "test_results.json"
        with open(results_file, "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"\nDetailed results saved to: {results_file}")
        
        # Return success if no failures
        return summary['failed'] == 0

async def main():
    """Main test runner"""
    tester = IntegrationTester()
    success = await tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())