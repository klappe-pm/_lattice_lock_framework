import pytest
import os
import yaml
from lattice_lock.config.frontmatter import FrontmatterParser
from lattice_lock.config.inheritance import InheritanceResolver
from lattice_lock.config.normalizer import JSONNormalizer
from lattice_lock.config.compiler import YAMLCompiler

class TestFrontmatterParser:
    def test_parse_frontmatter_and_vars(self, tmp_path):
        f = tmp_path / "test.yaml"
        # Use quote to force string type for version if we want string, 
        # or accepted that 1.0.0 is string but 1.0 is float.
        # Let's match typical semver usage which is often string.
        f.write_text("""---
vars:
  name: test_agent
  version: "1.0.0"
---
agent:
  name: ${vars.name}
  version: ${vars.version}
  fallback: ${vars.unknown:-default}
""", encoding='utf-8')
        
        parser = FrontmatterParser()
        frontmatter, content = parser.parse(str(f))
        
        assert frontmatter['vars']['name'] == 'test_agent'
        assert content['agent']['name'] == 'test_agent'
        assert content['agent']['version'] == "1.0.0"
        assert content['agent']['fallback'] == 'default'

class TestInheritanceResolver:
    def test_deep_merge_basic(self):
        resolver = InheritanceResolver()
        base = {'a': 1, 'b': {'c': 2}}
        override = {'b': {'d': 3}, 'e': 4}
        merged = resolver.deep_merge(base, override)
        
        assert merged == {'a': 1, 'b': {'c': 2, 'd': 3}, 'e': 4}

    def test_list_directives_append(self):
        resolver = InheritanceResolver()
        base = {'items': [1, 2]}
        override = {'items': {'+append': [3, 4]}}
        merged = resolver.deep_merge(base, override)
        assert merged['items'] == [1, 2, 3, 4]

    def test_list_directives_replace(self):
        resolver = InheritanceResolver()
        base = {'items': [1, 2]}
        override = {'items': {'+replace': [3, 4]}}
        merged = resolver.deep_merge(base, override)
        assert merged['items'] == [3, 4]
        
    def test_list_directives_remove(self):
        resolver = InheritanceResolver()
        base = {'items': [1, 2, 3]}
        override = {'items': {'+remove': [2]}}
        merged = resolver.deep_merge(base, override)
        assert merged['items'] == [1, 3]

class TestJSONNormalizer:
    def test_normalize_agents(self):
        normalizer = JSONNormalizer()
        data = {
            'agents': [
                {
                    'name': 'test',
                    'subagents': [{'name': 'sub1'}, {'name': 'sub2'}],
                    'provider_preferences': [{'provider': 'openai'}]
                }
            ]
        }
        normalized = normalizer.normalize(data)
        
        agent = normalized['agents'][0]
        assert 'id' in agent
        
        # Check extraction
        assert isinstance(agent['subagents'], list)
        assert isinstance(agent['subagents'][0], str) # IDs
        
        assert 'subagent_refs' in normalized
        assert len(normalized['subagent_refs']) == 2
        assert normalized['subagent_refs'][0]['agent_id'] == agent['id']

class TestYAMLCompiler:
    def test_compile_full_chain(self, tmp_path):
        # Create structure
        base_dir = tmp_path / "config"
        base_dir.mkdir()
        
        (base_dir / "base.yaml").write_text("""---
vars:
  role: base
---
agent:
  role: ${vars.role}
  skills: [basic]
""", encoding='utf-8')

        # Add a placeholder key in frontmatter to ensure regex matches
        # or just correct spacing.
        (base_dir / "mixin.yaml").write_text("""---
vars: {}
---
agent:
  skills: {+append: [mixin_skill]}
""", encoding='utf-8')

        (base_dir / "final.yaml").write_text("""---
extends: base.yaml
mixins:
  - mixin.yaml
vars:
  role: final_role
---
agent:
  name: final_agent
""", encoding='utf-8')

        compiler = YAMLCompiler(base_path=str(base_dir))
        result = compiler.compile("final.yaml")
        
        # Check 'role'.
        # Parent 'base.yaml' is compiled first. vars={role:base}.
        # Content 'agent.role' becomes 'base'.
        # Child 'final.yaml' compiles. vars={role:final_role}.
        # Content 'agent.name' is set. 
        # Child does NOT override 'role' in content.
        # Merging: Base has role='base'. Child has name='final_agent'.
        # Result should have role='base'.
        assert result['agent']['role'] == 'base'
        
        # Verify skills
        assert 'basic' in result['agent']['skills']
        assert 'mixin_skill' in result['agent']['skills']
        assert result['agent']['name'] == 'final_agent'
        assert result['_meta']['source'] == str(base_dir / "final.yaml")
