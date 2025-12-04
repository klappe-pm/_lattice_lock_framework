import pytest
import os
import yaml
from jinja2 import Template

TEMPLATE_DIR = "src/lattice_lock_cli/templates/ci/aws"

def test_buildspec_exists():
    path = os.path.join(TEMPLATE_DIR, "buildspec.yml.j2")
    assert os.path.exists(path)

def test_pipeline_exists():
    path = os.path.join(TEMPLATE_DIR, "pipeline.yml.j2")
    assert os.path.exists(path)

def test_codebuild_project_exists():
    path = os.path.join(TEMPLATE_DIR, "codebuild-project.yml.j2")
    assert os.path.exists(path)

def test_buildspec_valid_yaml():
    path = os.path.join(TEMPLATE_DIR, "buildspec.yml.j2")
    with open(path, 'r') as f:
        content = f.read()
    
    # Render with dummy context if needed (none used currently)
    template = Template(content)
    rendered = template.render()
    
    # Parse YAML
    try:
        yaml.safe_load(rendered)
    except yaml.YAMLError as e:
        pytest.fail(f"Invalid YAML in buildspec: {e}")

def test_codebuild_valid_yaml():
    path = os.path.join(TEMPLATE_DIR, "codebuild-project.yml.j2")
    with open(path, 'r') as f:
        content = f.read()
    
    template = Template(content)
    rendered = template.render()
    
    # CloudFormation uses !Ref, !Sub etc which are not standard YAML.
    # We need a custom loader or just check if it parses as generic YAML if we handle tags.
    # Or we can just check basic parsing without tags if we treat them as strings?
    # PyYAML safe_load fails on !Ref.
    # Let's use a loader that ignores unknown tags or converts them.
    
    class SafeLoaderIgnoreUnknown(yaml.SafeLoader):
        def ignore_unknown(self, node):
            return None 
    
    SafeLoaderIgnoreUnknown.add_constructor(None, SafeLoaderIgnoreUnknown.ignore_unknown)
    
    # Actually, easiest way to validate CloudFormation YAML locally without cfn-lint is tricky.
    # But we can try to register the tags.
    for tag in ['!Ref', '!Sub', '!GetAtt', '!ImportValue']:
        yaml.add_constructor(tag, lambda loader, node: str(node), Loader=yaml.SafeLoader)

    try:
        yaml.safe_load(rendered)
    except yaml.YAMLError as e:
        pytest.fail(f"Invalid YAML in codebuild project: {e}")

def test_pipeline_valid_yaml():
    path = os.path.join(TEMPLATE_DIR, "pipeline.yml.j2")
    with open(path, 'r') as f:
        content = f.read()
    
    template = Template(content)
    rendered = template.render()
    
    # Register tags again just in case (global state)
    for tag in ['!Ref', '!Sub', '!GetAtt', '!ImportValue']:
        try:
            yaml.add_constructor(tag, lambda loader, node: str(node), Loader=yaml.SafeLoader)
        except:
            pass # already added

    try:
        yaml.safe_load(rendered)
    except yaml.YAMLError as e:
        pytest.fail(f"Invalid YAML in pipeline: {e}")
