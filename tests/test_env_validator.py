import pytest
import os
import tempfile
from src.lattice_lock_validator.env import validate_env_file

@pytest.fixture
def valid_env_content():
    return """
ORCHESTRATOR_STRATEGY=balanced
LOG_LEVEL=INFO
DB_PASSWORD=vault:secret/db/password
API_KEY=your-api-key-here
"""

@pytest.fixture
def temp_env_file(valid_env_content):
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write(valid_env_content)
        path = f.name
    yield path
    os.remove(path)

def test_valid_env(temp_env_file):
    result = validate_env_file(temp_env_file)
    assert result.valid
    assert len(result.errors) == 0

def test_plaintext_secret():
    content = """
ORCHESTRATOR_STRATEGY=balanced
LOG_LEVEL=INFO
MY_API_KEY=12345-actual-secret-key
"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write(content)
        path = f.name
    
    try:
        result = validate_env_file(path)
        assert not result.valid
        assert any("Potential plaintext secret detected" in e.message for e in result.errors)
    finally:
        os.remove(path)

def test_missing_required_variable():
    content = """
LOG_LEVEL=INFO
"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write(content)
        path = f.name
    
    try:
        result = validate_env_file(path)
        assert not result.valid
        assert any("Missing required environment variable: ORCHESTRATOR_STRATEGY" in e.message for e in result.errors)
    finally:
        os.remove(path)

def test_invalid_naming_convention():
    content = """
ORCHESTRATOR_STRATEGY=balanced
LOG_LEVEL=INFO
lowercase_var=value
"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write(content)
        path = f.name
    
    try:
        result = validate_env_file(path)
        # Warnings don't invalidate the result by default in our implementation, 
        # but let's check if the warning is present.
        assert len(result.warnings) > 0
        assert any("does not follow UPPER_SNAKE_CASE" in w.message for w in result.warnings)
    finally:
        os.remove(path)

def test_secret_manager_reference():
    content = """
ORCHESTRATOR_STRATEGY=balanced
LOG_LEVEL=INFO
AWS_SECRET=aws-secrets:my-secret-id
VAULT_SECRET=vault:secret/data/app
"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write(content)
        path = f.name
    
    try:
        result = validate_env_file(path)
        assert result.valid
        assert len(result.errors) == 0
    finally:
        os.remove(path)
