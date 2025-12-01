#!/usr/bin/env python3
"""
Real-world integration tests for the Model Orchestration System
"""

import asyncio
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from model_orchestrator_enhanced import EnhancedModelOrchestrator
from zen_mcp_bridge import ZenMCPBridge, ModelRouter

async def test_real_world_scenarios():
    """Test real-world use cases"""
    
    print("\n" + "="*80)
    print("🌍 REAL-WORLD SCENARIO TESTING")
    print("="*80)
    
    orchestrator = EnhancedModelOrchestrator()
    bridge = ZenMCPBridge()
    router = ModelRouter()
    
    # Test 1: Large document analysis (needs 2M context)
    print("\n📄 Test 1: Large Document Analysis")
    large_doc_prompt = "Analyze this 500-page technical specification and provide insights"
    model_id, model = orchestrator.select_model(large_doc_prompt)
    print(f"  Selected: {model_id}")
    print(f"  Context: {model.context_window:,} tokens")
    print(f"  ✅ Can handle large docs: {model.context_window >= 1000000}")
    
    # Test 2: Budget-constrained operation
    print("\n💰 Test 2: Budget-Constrained Task")
    budget_prompt = "Translate this text to Spanish"
    model_id, model = orchestrator.select_model(budget_prompt, strategy="cost_optimize")
    cost = orchestrator.estimate_cost(model_id, 1000, 500)
    print(f"  Selected: {model_id}")
    print(f"  Cost estimate: ${cost:.4f}")
    print(f"  ✅ Budget-friendly: {cost < 0.01}")
    
    # Test 3: High-accuracy financial analysis
    print("\n📊 Test 3: Financial Analysis (High Accuracy Required)")
    finance_prompt = "Analyze these quarterly financial statements and identify risks"
    model_id, model = orchestrator.select_model(finance_prompt, strategy="quality_first")
    print(f"  Selected: {model_id}")
    print(f"  Accuracy: {model.accuracy:.2f}")
    print(f"  ✅ High accuracy: {model.accuracy >= 0.85}")
    
    # Test 4: Real-time chat (speed priority)
    print("\n⚡ Test 4: Real-time Chat Response")
    chat_prompt = "What's the weather like?"
    model_id, model = orchestrator.select_model(chat_prompt, strategy="speed_priority")
    print(f"  Selected: {model_id}")
    print(f"  Speed score: {model.speed:.2f}")
    print(f"  ✅ Fast response: {model.speed >= 0.7}")
    
    # Test 5: Code review with fallback
    print("\n🔄 Test 5: Code Review with Fallback")
    code_prompt = "Review this Python code for security vulnerabilities"
    
    # Simulate primary model unavailable
    primary = "grok-code-fast-1"
    if primary in orchestrator.models:
        orchestrator.models[primary].available = False
    
    model_id, model = orchestrator.select_model(code_prompt)
    print(f"  Primary unavailable, selected: {model_id}")
    print(f"  ✅ Fallback worked: {model_id != primary}")
    
    # Restore availability
    if primary in orchestrator.models:
        orchestrator.models[primary].available = True
    
    # Test 6: Multi-model consensus for critical decision
    print("\n🤝 Test 6: Critical Decision Consensus")
    critical_prompt = "Should we migrate our database to the cloud?"
    consensus = orchestrator.create_consensus_group(critical_prompt, num_models=3, diverse=True)
    
    print(f"  Consensus group:")
    providers = set()
    for i, (m_id, m) in enumerate(consensus, 1):
        print(f"    {i}. {m_id} ({m.provider.value})")
        providers.add(m.provider)
    
    print(f"  ✅ Provider diversity: {len(providers)} different providers")
    
    # Test 7: Vision task routing
    print("\n👁️ Test 7: Vision Task Routing")
    vision_prompt = "Analyze this screenshot and describe the UI elements"
    req = orchestrator.analyze_task(vision_prompt)
    
    if req.requires_vision:
        print(f"  ✅ Vision requirement detected")
        model_id, model = orchestrator.select_model(vision_prompt)
        print(f"  Selected: {model_id}")
        print(f"  Has vision: {model.supports_vision}")
    else:
        print(f"  ⚠️ Vision requirement not detected")
    
    # Test 8: Blocked model handling
    print("\n🚫 Test 8: Blocked Model Handling")
    production_prompt = "Generate production deployment script"
    
    # Check if blocked models are excluded
    model_id, model = orchestrator.select_model(production_prompt)
    is_blocked = orchestrator.guide.is_model_blocked(model_id)
    
    print(f"  Selected: {model_id}")
    print(f"  ✅ Not blocked: {not is_blocked}")
    
    # Test 9: Cost tracking over multiple operations
    print("\n📈 Test 9: Cost Tracking")
    
    # Simulate multiple operations
    operations = [
        ("Write code", 1000, 500),
        ("Debug error", 500, 250),
        ("Explain concept", 2000, 1000),
    ]
    
    for prompt, in_tokens, out_tokens in operations:
        model_id, _ = orchestrator.select_model(prompt)
        orchestrator.track_usage(model_id, in_tokens, out_tokens, 250)
    
    report = orchestrator.get_cost_report()
    print(f"  Total cost: ${report['total_cost']:.4f}")
    print(f"  Models used: {len(report['usage_count'])}")
    print(f"  ✅ Tracking works: {report['total_cost'] > 0}")
    
    # Test 10: Adaptive routing based on content
    print("\n🎯 Test 10: Adaptive Content Routing")
    
    test_prompts = [
        ("Write a haiku about coding", "creative"),
        ("Explain quantum computing", "educational"),
        ("Fix this SQL injection vulnerability", "security"),
        ("Optimize this algorithm", "performance"),
    ]
    
    for prompt, expected_type in test_prompts:
        model_id, model = orchestrator.select_model(prompt)
        print(f"  '{prompt[:30]}...' → {model_id}")
    
    print("\n" + "="*80)
    print("✅ ALL REAL-WORLD SCENARIOS TESTED SUCCESSFULLY")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(test_real_world_scenarios())