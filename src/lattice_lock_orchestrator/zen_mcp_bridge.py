#!/usr/bin/env python3
"""
Zen MCP Bridge
Integrates Model Orchestrator with Zen MCP tools for seamless multi-model operations
"""

import os
import json
import asyncio
import subprocess
from typing import Dict, List, Optional, Any
from pathlib import Path
from model_orchestrator import ModelOrchestrator, TaskType, ModelProvider

class ZenMCPBridge:
    """Bridge between Model Orchestrator and Zen MCP tools"""
    
    def __init__(self):
        self.orchestrator = ModelOrchestrator()
        self.zen_tools = self._discover_zen_tools()
        
    def _discover_zen_tools(self) -> List[str]:
        """Discover available Zen MCP tools"""
        # These are the Zen MCP tools available in your system
        return [
            "mcp__zen__chat",
            "mcp__zen__thinkdeep", 
            "mcp__zen__planner",
            "mcp__zen__consensus",
            "mcp__zen__codereview",
            "mcp__zen__precommit",
            "mcp__zen__debug",
            "mcp__zen__secaudit",
            "mcp__zen__docgen",
            "mcp__zen__analyze",
            "mcp__zen__refactor",
            "mcp__zen__tracer",
            "mcp__zen__testgen",
            "mcp__zen__challenge",
            "mcp__zen__listmodels",
            "mcp__zen__version"
        ]
    
    def extend_zen_models(self) -> Dict[str, Any]:
        """Extend Zen MCP with all Grok models"""
        
        # Get all models from orchestrator
        all_models = {}
        
        for model_id, model in self.orchestrator.models.items():
            provider = model.provider.value
            
            if provider not in all_models:
                all_models[provider] = []
            
            all_models[provider].append({
                "id": model_id,
                "context_window": model.context_window,
                "capabilities": {
                    "vision": model.supports_vision,
                    "function_calling": model.supports_function_calling,
                    "reasoning": model.supports_reasoning,
                    "code_specialized": model.code_specialized,
                },
                "cost": {
                    "input": model.input_cost,
                    "output": model.output_cost
                }
            })
        
        return all_models
    
    async def intelligent_zen_call(self,
                                  tool: str,
                                  prompt: str,
                                  auto_select_model: bool = True,
                                  **kwargs) -> Any:
        """Intelligently call Zen MCP tools with optimal model selection"""
        
        # Map Zen tools to task types
        tool_task_map = {
            "mcp__zen__chat": TaskType.CONVERSATION,
            "mcp__zen__thinkdeep": TaskType.REASONING,
            "mcp__zen__codereview": TaskType.CODE_REVIEW,
            "mcp__zen__debug": TaskType.DEBUGGING,
            "mcp__zen__analyze": TaskType.ANALYSIS,
            "mcp__zen__testgen": TaskType.CODE_GENERATION,
            "mcp__zen__refactor": TaskType.CODE_REVIEW,
            "mcp__zen__secaudit": TaskType.ANALYSIS,
        }
        
        if auto_select_model and tool in tool_task_map:
            # Auto-select best model for this Zen tool
            task_type = tool_task_map[tool]
            
            # Override task type detection with known mapping
            model_id, model = self.orchestrator.select_model(
                prompt,
                context={"task_type": task_type}
            )
            
            # Add model to kwargs
            kwargs["model"] = model_id
            
            print(f"Auto-selected {model_id} for {tool}")
        
        # Construct Zen MCP call parameters
        params = {
            "prompt": prompt,
            **kwargs
        }
        
        # Here you would make the actual Zen MCP call
        # For now, returning mock response
        return {
            "tool": tool,
            "model": kwargs.get("model"),
            "response": f"Response from {tool} using {kwargs.get('model')}"
        }
    
    def create_model_config_update(self) -> str:
        """Generate configuration update for Zen MCP to include all models"""
        
        config = {
            "models": {
                "xai": {
                    "grok-4-fast-reasoning": {
                        "context": 2000000,
                        "description": "Fast reasoning with 2M context",
                        "aliases": ["grok4-fast", "grok-reason"]
                    },
                    "grok-4-fast-non-reasoning": {
                        "context": 2000000,
                        "description": "Fast non-reasoning with 2M context",
                        "aliases": ["grok4-fast-nr"]
                    },
                    "grok-4-0709": {
                        "context": 256000,
                        "description": "Grok-4 July 2025 release",
                        "aliases": ["grok4"]
                    },
                    "grok-code-fast-1": {
                        "context": 256000,
                        "description": "Code-optimized fast model",
                        "aliases": ["grok-code"]
                    },
                    "grok-3-mini": {
                        "context": 131072,
                        "description": "Compact efficient model",
                        "aliases": ["grok-mini"]
                    },
                    "grok-2-vision-1212": {
                        "context": 32768,
                        "description": "Vision model with image input",
                        "aliases": ["grok-vision"]
                    },
                    "grok-2-image-1212": {
                        "context": 0,
                        "description": "Image generation model",
                        "aliases": ["grok-image"]
                    }
                }
            },
            "model_selection": {
                "auto_select": True,
                "strategy": "balanced",
                "cost_threshold": 100.0,
                "quality_threshold": 0.7
            }
        }
        
        return json.dumps(config, indent=2)
    
    async def multi_model_consensus(self,
                                   prompt: str,
                                   num_models: int = 3) -> Dict[str, Any]:
        """Use Zen consensus tool with intelligent model selection"""
        
        # Select diverse models for consensus
        models = self.orchestrator.create_consensus_group(prompt, num_models, diverse=True)
        
        # Prepare model configurations for Zen consensus
        model_configs = []
        for model_id, model in models:
            model_configs.append({
                "model": model_id,
                "stance": "neutral",  # Can be for/against/neutral
                "weight": model.accuracy  # Weight by accuracy
            })
        
        # Call Zen consensus with selected models
        result = await self.intelligent_zen_call(
            "mcp__zen__consensus",
            prompt,
            auto_select_model=False,  # We're providing multiple models
            models=model_configs
        )
        
        return result
    
    async def adaptive_analysis(self,
                              prompt: str,
                              depth: str = "auto") -> Dict[str, Any]:
        """Adaptive analysis using best model for complexity"""
        
        # Analyze prompt complexity
        requirements = self.orchestrator.analyze_task(prompt)
        
        # Determine analysis depth based on requirements
        if depth == "auto":
            if requirements.requires_reasoning:
                depth = "high"
            elif len(prompt) > 1000:
                depth = "medium"
            else:
                depth = "low"
        
        # Select appropriate Zen tool and model
        if depth == "high":
            tool = "mcp__zen__thinkdeep"
            strategy = "quality_first"
        elif depth == "medium":
            tool = "mcp__zen__analyze"
            strategy = "balanced"
        else:
            tool = "mcp__zen__chat"
            strategy = "speed_priority"
        
        # Get optimal model
        model_id, _ = self.orchestrator.select_model(prompt, strategy=strategy)
        
        # Execute analysis
        result = await self.intelligent_zen_call(
            tool,
            prompt,
            auto_select_model=False,
            model=model_id,
            thinking_mode=depth
        )
        
        return result
    
    def generate_unified_config(self) -> Dict[str, Any]:
        """Generate unified configuration for all models and providers"""
        
        config = {
            "providers": {
                "anthropic": {
                    "enabled": os.getenv("ANTHROPIC_API_KEY") is not None,
                    "models": []
                },
                "openai": {
                    "enabled": os.getenv("OPENAI_API_KEY") is not None,
                    "models": []
                },
                "google": {
                    "enabled": os.getenv("GOOGLE_API_KEY") is not None,
                    "models": []
                },
                "xai": {
                    "enabled": os.getenv("XAI_API_KEY") is not None,
                    "models": []
                },
                "dial": {
                    "enabled": os.getenv("DIAL_API_KEY") is not None,
                    "models": []
                },
                "local": {
                    "enabled": True,
                    "endpoint": os.getenv("CUSTOM_API_URL", "http://localhost:11434/v1"),
                    "models": []
                }
            },
            "orchestration": {
                "auto_select": True,
                "fallback_enabled": True,
                "parallel_enabled": True,
                "consensus_enabled": True,
                "cost_tracking": True
            },
            "zen_mcp_integration": {
                "enabled": True,
                "auto_model_selection": True,
                "tools": self.zen_tools
            }
        }
        
        # Populate models for each provider
        for model_id, model in self.orchestrator.models.items():
            provider = model.provider.value
            
            model_info = {
                "id": model_id,
                "context_window": model.context_window,
                "capabilities": {
                    "vision": model.supports_vision,
                    "function_calling": model.supports_function_calling,
                    "reasoning": model.supports_reasoning,
                    "code_specialized": model.code_specialized
                },
                "performance": {
                    "speed": model.speed,
                    "accuracy": model.accuracy,
                    "reasoning_depth": model.reasoning_depth
                },
                "cost": {
                    "input_per_million": model.input_cost,
                    "output_per_million": model.output_cost
                }
            }
            
            if provider in config["providers"]:
                config["providers"][provider]["models"].append(model_info)
        
        return config

class ModelRouter:
    """High-level routing interface"""
    
    def __init__(self):
        self.bridge = ZenMCPBridge()
        self.orchestrator = self.bridge.orchestrator
        
    async def route(self,
                   prompt: str,
                   mode: str = "auto",
                   **kwargs) -> Any:
        """Route request to optimal model/tool combination"""
        
        if mode == "auto":
            # Fully automatic routing
            requirements = self.orchestrator.analyze_task(prompt)
            
            # Determine best approach
            if requirements.requires_reasoning and requirements.min_context_window > 500000:
                # Use Grok-4 fast reasoning for large context reasoning
                return await self._use_grok_reasoning(prompt, **kwargs)
            elif requirements.requires_vision:
                # Use vision model
                return await self._use_vision_model(prompt, **kwargs)
            elif requirements.task_type == TaskType.CODE_GENERATION:
                # Use code-specialized model
                return await self._use_code_model(prompt, **kwargs)
            else:
                # Use standard chat with best model
                return await self._use_chat(prompt, **kwargs)
        
        elif mode == "consensus":
            # Multi-model consensus
            return await self.bridge.multi_model_consensus(prompt, **kwargs)
        
        elif mode == "chain":
            # Chain of thought
            return await self._use_chain(prompt, **kwargs)
        
        elif mode == "adaptive":
            # Adaptive depth analysis
            return await self.bridge.adaptive_analysis(prompt, **kwargs)
        
        else:
            raise ValueError(f"Unknown mode: {mode}")
    
    async def _use_grok_reasoning(self, prompt: str, **kwargs) -> Any:
        """Use Grok-4 fast reasoning model"""
        return await self.bridge.intelligent_zen_call(
            "mcp__zen__thinkdeep",
            prompt,
            auto_select_model=False,
            model="grok-4-fast-reasoning",
            thinking_mode="high",
            **kwargs
        )
    
    async def _use_vision_model(self, prompt: str, **kwargs) -> Any:
        """Use vision model"""
        return await self.bridge.intelligent_zen_call(
            "mcp__zen__analyze",
            prompt,
            auto_select_model=False,
            model="grok-2-vision-1212",
            **kwargs
        )
    
    async def _use_code_model(self, prompt: str, **kwargs) -> Any:
        """Use code-specialized model"""
        return await self.bridge.intelligent_zen_call(
            "mcp__zen__testgen" if "test" in prompt.lower() else "mcp__zen__chat",
            prompt,
            auto_select_model=False,
            model="grok-code-fast-1",
            **kwargs
        )
    
    async def _use_chat(self, prompt: str, **kwargs) -> Any:
        """Use standard chat with best model"""
        return await self.bridge.intelligent_zen_call(
            "mcp__zen__chat",
            prompt,
            auto_select_model=True,
            **kwargs
        )
    
    async def _use_chain(self, prompt: str, tasks: List[str], **kwargs) -> Any:
        """Use chain of thought across models"""
        chain = self.orchestrator.create_model_chain(tasks)
        results = []
        
        for task, (model_id, model) in zip(tasks, chain):
            result = await self.bridge.intelligent_zen_call(
                "mcp__zen__chat",
                task,
                auto_select_model=False,
                model=model_id,
                **kwargs
            )
            results.append(result)
        
        return results

async def main():
    """Demo the unified system"""
    
    router = ModelRouter()
    
    print("="*80)
    print("Unified Model Orchestration System")
    print("="*80)
    
    # Test scenarios
    tests = [
        ("Explain quantum computing in simple terms", "auto"),
        ("Analyze this complex codebase for security issues", "adaptive"),
        ("What's the best approach to optimize this algorithm?", "consensus"),
        ("Write tests for this Python function", "auto"),
    ]
    
    for prompt, mode in tests:
        print(f"\nPrompt: {prompt[:50]}...")
        print(f"Mode: {mode}")
        
        result = await router.route(prompt, mode=mode)
        print(f"Result: {result}")
    
    # Show cost report
    print("\n" + "="*80)
    print("Cost Report")
    print("="*80)
    
    report = router.orchestrator.get_cost_report()
    print(f"Total Estimated Cost: ${report['total_cost']:.4f}")
    
    # Generate configuration
    bridge = ZenMCPBridge()
    config = bridge.generate_unified_config()
    
    # Save configuration
    config_path = Path(__file__).parent / "unified_model_config.json"
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
    
    print(f"\nUnified configuration saved to: {config_path}")

if __name__ == "__main__":
    asyncio.run(main())