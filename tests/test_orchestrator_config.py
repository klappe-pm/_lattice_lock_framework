
import pytest
import yaml
from pathlib import Path
from tempfile import NamedTemporaryFile

from lattice_lock.agents.prompt_architect.orchestrator import PromptArchitectOrchestrator
from lattice_lock.agents.prompt_architect.models import ToolType

def test_orchestrator_defaults_clean():
    """Verify that default initialization does NOT include pilot_projects ownership."""
    orchestrator = PromptArchitectOrchestrator()
    devin_tool = orchestrator.tool_matcher._capability_map[ToolType.DEVIN]
    
    # Check all ownerships for Devin
    has_examples = False
    for ownership in devin_tool.file_ownership:
        if "examples/*" in ownership.patterns:
            has_examples = True
            break
            
    assert not has_examples, "Default configuration should not own examples"

def test_orchestrator_loads_config():
    """Verify that orchestrator loads configuration correctly."""
    
    config_data = {
        "tool_capabilities": [
            {
                "tool": "devin",
                "file_ownership": [
                    {
                        "paths": [],
                        "patterns": ["examples/*"],
                        "description": "Test ownership"
                    }
                ]
            }
        ]
    }
    
    with NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(config_data, f)
        config_path = f.name
        
    try:
        orchestrator = PromptArchitectOrchestrator(config_path=config_path)
        devin_tool = orchestrator.tool_matcher._capability_map[ToolType.DEVIN]
        
        has_examples = False
        for ownership in devin_tool.file_ownership:
            if "examples/*" in ownership.patterns:
                has_examples = True
                break
                
        assert has_examples, "Configured orchestrator SHOULD own examples"
        
    finally:
        Path(config_path).unlink()

def test_integration_passes_config():
    """Verify that integration layer correctly passes config to orchestrator."""
    from lattice_lock.agents.prompt_architect.integration import PromptArchitectIntegration, IntegrationConfig
    
    config_data = {
        "tool_capabilities": [
            {
                "tool": "devin",
                "file_ownership": [
                    {
                        "paths": [],
                        "patterns": ["examples/*"],
                        "description": "Test integration ownership"
                    }
                ]
            }
        ]
    }
    
    with NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(config_data, f)
        config_path = f.name
        
    try:
        # Create integration with config pointing to our yaml
        integration_config = IntegrationConfig(config_path=config_path)
        integration = PromptArchitectIntegration(config=integration_config)
        
        # Access the underlying orchestrator's tool capabilities
        devin_tool = integration.orchestrator.tool_matcher._capability_map[ToolType.DEVIN]
        
        has_examples = False
        for ownership in devin_tool.file_ownership:
            if "examples/*" in ownership.patterns:
                has_examples = True
                break
                
        assert has_examples, "Integration should have passed config to orchestrator"
        
    finally:
        Path(config_path).unlink()
