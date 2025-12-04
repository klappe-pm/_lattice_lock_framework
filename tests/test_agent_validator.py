import pytest
import os
import tempfile
from src.lattice_lock_validator.agents import validate_agent_manifest

@pytest.fixture
def valid_agent_content():
    return """
agent:
  identity:
    name: "backend_developer"
    version: "1.0.0"
    description: "Implements backend logic"
    role: "engineer"

directive:
  primary_goal: "Write code"
  constraints: []

responsibilities:
  - name: "implement_api"
    description: "Create API endpoints"

scope:
  can_access: ["src/"]
  cannot_access: ["secrets/"]
"""

@pytest.fixture
def temp_agent_file(valid_agent_content):
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml') as f:
        f.write(valid_agent_content)
        path = f.name
    yield path
    os.remove(path)

def test_valid_agent(temp_agent_file):
    result = validate_agent_manifest(temp_agent_file)
    assert result.valid
    assert len(result.errors) == 0

def test_missing_required_section():
    content = """
agent:
  identity:
    name: "foo"
"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml') as f:
        f.write(content)
        path = f.name
    
    try:
        result = validate_agent_manifest(path)
        assert not result.valid
        error_msgs = [e.message for e in result.errors]
        assert "Missing required top-level section: directive" in error_msgs
        assert "Missing required top-level section: responsibilities" in error_msgs
    finally:
        os.remove(path)

def test_invalid_version_format():
    content = """
agent:
  identity:
    name: "backend_developer"
    version: "invalid"
    description: "desc"
    role: "role"
directive:
  primary_goal: "goal"
responsibilities: []
scope:
  can_access: []
  cannot_access: []
"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml') as f:
        f.write(content)
        path = f.name
    
    try:
        result = validate_agent_manifest(path)
        # Note: invalid version is an error in _validate_identity
        assert not result.valid
        assert any("Invalid version format" in e.message for e in result.errors)
    finally:
        os.remove(path)

def test_empty_required_field():
    content = """
agent:
  identity:
    name: ""
    version: "1.0.0"
    description: "desc"
    role: "role"
directive:
  primary_goal: "goal"
responsibilities: []
scope:
  can_access: []
  cannot_access: []
"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml') as f:
        f.write(content)
        path = f.name
    
    try:
        result = validate_agent_manifest(path)
        assert not result.valid
        assert any("Field 'agent.identity.name' must be a non-empty string" in e.message for e in result.errors)
    finally:
        os.remove(path)

def test_invalid_types():
    content = """
agent:
  identity: "not a dict"
directive: "not a dict"
responsibilities: "not a list"
scope: "not a dict"
"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml') as f:
        f.write(content)
        path = f.name
    
    try:
        result = validate_agent_manifest(path)
        assert not result.valid
        msgs = [e.message for e in result.errors]
        assert "agent.identity must be a dictionary" in msgs
        assert "directive section must be a dictionary" in msgs
        assert "responsibilities section must be a list" in msgs
        assert "scope section must be a dictionary" in msgs
    finally:
        os.remove(path)

def test_missing_nested_fields():
    content = """
agent:
  identity:
    name: "backend_developer"
    version: "1.0.0"
    description: "desc"
    role: "role"
directive:
  # missing primary_goal
  constraints: "not a list"
responsibilities:
  - name: "task1"
    # missing description
scope:
  # missing can_access
  cannot_access: []
"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml') as f:
        f.write(content)
        path = f.name
    
    try:
        result = validate_agent_manifest(path)
        assert not result.valid
        msgs = [e.message for e in result.errors]
        assert "Missing required field in directive: primary_goal" in msgs
        assert "Field 'directive.constraints' must be a list" in msgs
        assert "Responsibility item #1 missing required field: description" in msgs
        assert "Missing required field in scope: can_access" in msgs
    finally:
        os.remove(path)

def test_malformed_responsibility_item():
    content = """
agent:
  identity:
    name: "backend_developer"
    version: "1.0.0"
    description: "desc"
    role: "role"
directive:
  primary_goal: "goal"
responsibilities:
  - "not a dict"
scope:
  can_access: []
  cannot_access: []
"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml') as f:
        f.write(content)
        path = f.name
    
    try:
        result = validate_agent_manifest(path)
        assert not result.valid
        assert any("Responsibility item #1 must be a dictionary" in e.message for e in result.errors)
    finally:
        os.remove(path)
