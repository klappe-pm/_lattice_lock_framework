
import pytest
import yaml
from pathlib import Path
from tempfile import NamedTemporaryFile

from lattice_lock.agents.prompt_architect.agent import PromptArchitectAgent as PromptArchitectOrchestrator



def test_orchestrator_defaults_clean():
    """Verify that default initialization does NOT include pilot_projects ownership."""
    orchestrator = PromptArchitectOrchestrator()
    # Check if devin profile exists
    if "devin" not in orchestrator.tool_matcher.profiles:
        # If devin not in defaults, skip or check something else
        return

    devin_profile = orchestrator.tool_matcher.profiles["devin"]
    
    # Check preferred files for Devin
    has_examples = False
    for pattern in devin_profile.preferred_files:
        if "examples/*" in pattern:
            has_examples = True
            break
            
    assert not has_examples, "Default configuration should not own examples"

def test_orchestrator_loads_config():
    """Verify that orchestrator loads configuration correctly."""
    
    config_data = {
        "tool_profiles": {
            "devin": {
                "name": "Devin",
                "identifier": "devin",
                "strengths": ["coding"],
                "preferred_files": ["examples/*"]
            }
        }
    }
    
    with NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(config_data, f)
        config_path = f.name
        
    try:
        # PromptArchitectAgent takes definition_path, but tool_matcher takes config separately.
        # But Agent initializes ToolMatcher with DEFAULT_TOOL_PROFILES_PATH.
        # The test tries to pass `config_path` to Agent/Orchestrator.
        # PromptArchitectAgent __init__ takes definition_path, NOT tool_profiles config path directly.
        # It has tool_matcher property that lazy loads.
        
        # We need to monkeypatch the DEFAULT_TOOL_PROFILES_PATH or instantiate ToolMatcher manually for test?
        # Or instantiate Agent and mock the path.
        
        # Actually Agent constructor doesn't take config_path for tools.
        # Let's see how we can inject it.
        # Agent class has DEFAULT_TOOL_PROFILES_PATH class attribute.
        
        PromptArchitectOrchestrator.DEFAULT_TOOL_PROFILES_PATH = config_path # Monkeypatch based on local file for test
        
        orchestrator = PromptArchitectOrchestrator()
        # Force load
        _ = orchestrator.tool_matcher
        
        devin_profile = orchestrator.tool_matcher.profiles["devin"]
        
        has_examples = False
        for pattern in devin_profile.preferred_files:
            if "examples/*" in pattern:
                has_examples = True
                break
                
        assert has_examples, "Configured orchestrator SHOULD own examples"
        
    finally:
        Path(config_path).unlink()

# Removed test_integration_passes_config because integration module is gone.

