# Agent System v3.0 Migration Guide

## Overview
This guide provides instructions for migrating the Lattice Lock Framework's agent definitions from the current minimal structure to the comprehensive v3.0 specification while maintaining backward compatibility and git history.

## New Format: YAML Frontmatter + JSON Body

### Why This Format?
- **YAML frontmatter**: Human-readable metadata and configuration
- **JSON body**: Structured, schema-validated agent definition
- **Best of both worlds**: Easy editing + strict validation
- **Compatibility**: Works with existing tooling and git diff

### File Structure Example
```yaml
---
# YAML Frontmatter - Human-editable metadata
version: 3.0
id: a7b3c9d1-4f2e-4a8b-9c3d-1a2b3c4d5e6f
name: engineering_agent
domain: engineering
type: primary
status: active
author: engineering-team@lattice-lock.com
created: 2024-01-15T09:30:00Z
modified: 2026-01-10T14:45:00Z
tags:
  - engineering
  - orchestrator
  - primary
---
```
```json
{
  "agent": {
    "role": {
      "primary_function": "Orchestrate engineering tasks and manage technical sub-agents",
      "personality_traits": {
        "tone": "professional, technical",
        "formality_level": "moderate",
        "verbosity": "concise",
        "emotional_intelligence": "moderate"
      },
      "expertise_areas": [
        {"domain": "software_engineering", "proficiency": 0.9},
        {"domain": "system_architecture", "proficiency": 0.85},
        {"domain": "code_review", "proficiency": 0.95}
      ],
      "response_style": {
        "preferred_format": "structured",
        "use_examples": true,
        "include_reasoning": true,
        "max_response_length": 2000
      }
    },
    "capabilities": {
      "core_capabilities": [
        {
          "id": "code_review",
          "description": "Review code for quality, security, and standards compliance",
          "required_inputs": [
            {"name": "code", "type": "string", "required": true},
            {"name": "language", "type": "string", "required": true},
            {"name": "standards", "type": "object", "required": false}
          ],
          "expected_outputs": [
            {"name": "review_result", "type": "object"},
            {"name": "issues", "type": "array"},
            {"name": "suggestions", "type": "array"}
          ],
          "error_handling": "retry_with_backoff"
        }
      ]
    }
  }
}
```

## Migration Strategy

### Approach: In-Place Progressive Enhancement
- **Update existing files** in their current locations
- **Maintain git history** for all changes
- **Progressive enhancement** - add new fields without breaking existing functionality
- **Backward compatible** - v2 agents continue to work during migration

## Directory Structure (No Changes)
```
agents/
├── agent_definitions/          # Keep existing structure
│   ├── agents_business_review/
│   ├── agents_cloud/
│   ├── agents_content/
│   ├── agents_context/
│   ├── agents_engineering/
│   ├── agents_financial/
│   └── ...
├── agents_config/              # Configuration and inheritance
├── templates_agents/           # Templates for new agents
└── validation/                 # New validation tools (add)
```

## Migration Phases

### Phase 1: Core Structure Enhancement (Week 1)
Convert files to YAML frontmatter + JSON format, preserving all existing data.

### Phase 2: Capabilities & Constraints (Week 2)
Define explicit capabilities and constraints for each agent.

### Phase 3: Tool Integration & Context (Week 3)
Add tool definitions and enhanced context management.

### Phase 4: Behavioral Specifications (Week 4)
Implement detailed behavioral patterns and error handling.

### Phase 5: Validation & Testing (Week 5)
Validate all agents and fix any issues.

## Step-by-Step Migration Process

### Step 1: Backup Current State
```bash
# Create a backup branch
git checkout -b agent-v3-migration-backup
git push origin agent-v3-migration-backup

# Switch to migration branch
git checkout -b feature/agent-v3-migration
```

### Step 2: Install Migration Tools
```bash
cd agents/
pip install -r requirements.txt
pip install pyyaml jsonschema python-frontmatter
```

### Step 3: Run Migration Script
```bash
# Dry run first
python3 migrate_to_v3.py --dry-run --domain engineering

# Actual migration
python3 migrate_to_v3.py --domain engineering

# Or migrate all
python3 migrate_to_v3.py --all
```

### Step 4: Validate Migrated Files
```bash
# Validate single file
python3 validate_v3.py agents/agent_definitions/agents_engineering/engineering_agent_definition.yaml

# Validate domain
python3 validate_v3.py --domain engineering

# Validate all
python3 validate_v3.py --all
```

### Step 5: Git Commit Strategy
```bash
# Commit each domain separately
git add agents/agent_definitions/agents_engineering/
git commit -m "feat(agents): migrate engineering agents to v3 format (YAML+JSON)"

# Commit each enhancement separately
git add agents/agent_definitions/agents_engineering/
git commit -m "feat(agents): add capabilities to engineering agents"

git add agents/agent_definitions/agents_engineering/
git commit -m "feat(agents): add tool definitions to engineering agents"
```

## Conversion Guide: v2 YAML to v3 YAML+JSON

### Current v2 Format:
```yaml
agent:
  identity:
    name: engineering_agent
    version: 2.1.0
    description: Manages engineering tasks
    role: Engineering Manager
  directive:
    primary_goal: Orchestrate engineering work
  scope:
    can_access:
      - /src
    can_modify:
      - /src
  delegation:
    enabled: true
    allowed_subagents:
      - backend_developer
      - frontend_developer
```

### New v3 Format:

#### File: `engineering_agent_definition.yaml`
```yaml
---
# YAML Frontmatter - Metadata and configuration
version: 3.0
id: a7b3c9d1-4f2e-4a8b-9c3d-1a2b3c4d5e6f
name: engineering_agent
domain: engineering
type: primary
status: active
description: Orchestrates engineering tasks and manages technical sub-agents
author: engineering-team@lattice-lock.com
created: 2024-01-15T09:30:00Z
modified: 2026-01-10T14:45:00Z
tags:
  - engineering
  - orchestrator
  - primary
dependencies:
  - agent_id: context_agent
    version: ">=3.0"
    optional: true
legacy:
  version: "2.1.0"
  migration_date: 2026-01-10T14:45:00Z
  breaking_changes: false
---
```
```json
{
  "agent": {
    "role": {
      "primary_function": "Orchestrate engineering tasks and manage technical sub-agents for software development",
      "personality_traits": {
        "tone": "professional, technical, collaborative",
        "formality_level": "moderate",
        "verbosity": "concise",
        "emotional_intelligence": "moderate"
      },
      "expertise_areas": [
        {"domain": "software_engineering", "proficiency": 0.9},
        {"domain": "system_architecture", "proficiency": 0.85},
        {"domain": "code_review", "proficiency": 0.95},
        {"domain": "team_coordination", "proficiency": 0.8}
      ],
      "response_style": {
        "preferred_format": "structured",
        "use_examples": true,
        "include_reasoning": true,
        "max_response_length": 2000
      }
    },
    "capabilities": {
      "core_capabilities": [
        {
          "id": "task_orchestration",
          "description": "Coordinate and delegate engineering tasks to appropriate sub-agents",
          "required_inputs": [
            {"name": "task_description", "type": "string", "required": true},
            {"name": "requirements", "type": "object", "required": true},
            {"name": "constraints", "type": "object", "required": false}
          ],
          "expected_outputs": [
            {"name": "execution_plan", "type": "object"},
            {"name": "delegations", "type": "array"},
            {"name": "timeline", "type": "object"}
          ],
          "error_handling": "retry_with_backoff"
        },
        {
          "id": "code_review",
          "description": "Review code for quality, security, and standards compliance",
          "required_inputs": [
            {"name": "code", "type": "string", "required": true},
            {"name": "language", "type": "string", "required": true}
          ],
          "expected_outputs": [
            {"name": "review_result", "type": "object"},
            {"name": "issues", "type": "array"}
          ],
          "error_handling": "fail_fast"
        }
      ],
      "conditional_capabilities": [
        {
          "id": "emergency_escalation",
          "description": "Escalate critical issues to human supervisors",
          "trigger_conditions": [
            "severity == 'critical'",
            "confidence < 0.3",
            "user_request == 'escalate'"
          ],
          "required_inputs": [
            {"name": "issue_context", "type": "object", "required": true}
          ]
        }
      ],
      "learning_capabilities": {
        "can_learn_from_interactions": true,
        "memory_type": "episodic",
        "retention_period": "30_days",
        "update_frequency": "after_each_session"
      }
    },
    "constraints": {
      "operational_boundaries": [
        "Cannot deploy to production without approval",
        "Must follow coding standards defined in /standards",
        "Cannot access sensitive customer data",
        "Must validate all code changes through tests"
      ],
      "ethical_guidelines": [
        {
          "principle": "code_quality",
          "rules": [
            "Never compromise on security for speed",
            "Always consider maintainability in solutions",
            "Document all significant decisions"
          ]
        },
        {
          "principle": "transparency",
          "rules": [
            "Log all automated changes",
            "Provide clear reasoning for technical decisions",
            "Acknowledge limitations and uncertainties"
          ]
        }
      ],
      "resource_limits": {
        "max_tokens_per_response": 4000,
        "max_api_calls_per_minute": 30,
        "max_sub_agent_depth": 3,
        "timeout_seconds": 120,
        "max_concurrent_operations": 5
      },
      "safety_rules": {
        "content_filtering": "minimal",
        "prohibited_topics": ["malware", "exploits", "unauthorized_access"],
        "escalation_required": ["security_breach", "data_loss", "system_failure"]
      }
    },
    "context": {
      "initial_context": {
        "system_prompts": [
          "You are the Engineering Agent for the Lattice Lock Framework",
          "You coordinate engineering tasks and ensure code quality",
          "You delegate specialized tasks to appropriate sub-agents"
        ],
        "knowledge_bases": [
          "/docs/engineering-standards",
          "/docs/api-reference",
          "/docs/architecture"
        ]
      },
      "memory_management": {
        "working_memory": {
          "capacity": "last_20_messages",
          "retention_strategy": "sliding_window"
        },
        "long_term_memory": {
          "enabled": true,
          "storage_backend": "vector_database",
          "retrieval_method": "semantic_similarity",
          "relevance_threshold": 0.75
        }
      },
      "context_injection": [
        {
          "source": "project_context",
          "trigger": "automatic",
          "max_items": 10,
          "relevance_threshold": 0.7
        },
        {
          "source": "recent_commits",
          "trigger": "on_demand",
          "lookback_period": "7_days"
        }
      ]
    },
    "behaviors": {
      "greeting_protocol": {
        "initial_greeting": "Hello! I'm the Engineering Agent. I can help with code reviews, architecture decisions, and task coordination.",
        "returning_user": "Welcome back! Ready to continue with {{last_task}}?",
        "context_aware": true
      },
      "problem_solving_approach": {
        "steps": [
          {
            "action": "analyze_request",
            "description": "Parse and understand the engineering task"
          },
          {
            "action": "assess_complexity",
            "description": "Determine if delegation is needed"
          },
          {
            "action": "create_plan",
            "description": "Develop execution strategy"
          },
          {
            "action": "delegate_or_execute",
            "description": "Either handle directly or delegate to sub-agents"
          },
          {
            "action": "validate_results",
            "description": "Ensure quality standards are met"
          },
          {
            "action": "report_completion",
            "description": "Provide summary and next steps"
          }
        ]
      },
      "escalation_behavior": {
        "triggers": [
          {"condition": "task_complexity > 0.9", "action": "request_human_review"},
          {"condition": "security_risk_detected", "action": "immediate_escalation"},
          {"condition": "repeated_failures > 3", "action": "escalate_with_context"}
        ],
        "escalation_message": "This requires human intervention. Escalating to {{supervisor}} with full context."
      },
      "error_handling": {
        "compilation_error": "I've detected a compilation error: {{error}}. Let me help you fix it.",
        "test_failure": "Tests are failing. Here's my analysis: {{analysis}}",
        "unknown_technology": "I'm not familiar with {{technology}}. Let me research or delegate to a specialist.",
        "rate_limit": "I've hit a rate limit. Please wait {{seconds}} seconds.",
        "timeout": "The operation timed out. Would you like me to retry with adjusted parameters?"
      }
    },
    "tools": {
      "available_tools": [
        {
          "tool_id": "code_analyzer",
          "type": "analysis",
          "endpoint": "internal://code-analyzer",
          "parameters": [
            {"name": "code", "type": "string", "required": true},
            {"name": "language", "type": "string", "required": true},
            {"name": "rules", "type": "array", "required": false}
          ],
          "response_format": "json",
          "error_handling": "retry_with_backoff",
          "timeout": 30
        },
        {
          "tool_id": "test_runner",
          "type": "execution",
          "endpoint": "internal://test-runner", 
          "parameters": [
            {"name": "test_suite", "type": "string", "required": true},
            {"name": "coverage", "type": "boolean", "default": true}
          ],
          "response_format": "json",
          "error_handling": "fail_fast",
          "timeout": 120
        },
        {
          "tool_id": "git_operations",
          "type": "vcs",
          "endpoint": "internal://git",
          "operations": ["status", "diff", "commit", "branch"],
          "authentication": "token",
          "rate_limit": "100/hour"
        }
      ],
      "tool_selection_strategy": {
        "method": "task_based",
        "fallback_behavior": "delegate_to_specialist",
        "parallel_execution": true,
        "max_concurrent_tools": 3
      }
    },
    "sub_agents": [
      {
        "agent_id": "backend_developer",
        "agent_file": "subagents/engineering_agent_backend_developer_definition.yaml",
        "trigger_conditions": [
          "task_type == 'backend'",
          "involves(['api', 'database', 'server'])",
          "language in ['python', 'java', 'go']"
        ],
        "handoff_protocol": {
          "context_transfer": "selective",
          "included_context": ["requirements", "constraints", "existing_code"],
          "return_control": "on_completion",
          "timeout": 300,
          "max_retries": 2
        }
      },
      {
        "agent_id": "frontend_developer",
        "agent_file": "subagents/engineering_agent_frontend_developer_definition.yaml",
        "trigger_conditions": [
          "task_type == 'frontend'",
          "involves(['ui', 'ux', 'client'])",
          "language in ['javascript', 'typescript', 'react']"
        ],
        "handoff_protocol": {
          "context_transfer": "selective",
          "included_context": ["requirements", "design_specs", "api_contracts"],
          "return_control": "on_completion",
          "timeout": 300,
          "max_retries": 2
        }
      },
      {
        "agent_id": "devops_engineer",
        "agent_file": "subagents/engineering_agent_devops_engineer_definition.yaml",
        "trigger_conditions": [
          "task_type == 'deployment'",
          "involves(['ci', 'cd', 'infrastructure'])",
          "platform in ['aws', 'kubernetes', 'docker']"
        ],
        "handoff_protocol": {
          "context_transfer": "full_conversation",
          "return_control": "on_completion",
          "timeout": 600,
          "max_retries": 3
        }
      }
    ],
    "evaluation": {
      "success_metrics": [
        {
          "metric": "task_completion_rate",
          "target": 0.95,
          "measurement_window": "weekly",
          "calculation_method": "completed_tasks / total_tasks"
        },
        {
          "metric": "code_quality_score",
          "target": 0.85,
          "measurement_window": "daily",
          "calculation_method": "weighted_average(lint_score, test_coverage, complexity)"
        },
        {
          "metric": "delegation_efficiency",
          "target": 0.9,
          "measurement_window": "daily",
          "calculation_method": "successful_delegations / total_delegations"
        }
      ],
      "quality_checks": [
        {
          "check": "response_relevance",
          "method": "semantic_similarity",
          "threshold": 0.8
        },
        {
          "check": "code_standards_compliance",
          "method": "rule_based",
          "rules_file": "/standards/coding-standards.yaml"
        }
      ]
    },
    "adaptation": {
      "learning_mechanism": {
        "type": "reinforcement",
        "feedback_sources": ["user_ratings", "task_success", "code_review_outcomes"],
        "update_frequency": "weekly",
        "model": "contextual_bandit"
      },
      "personalization": {
        "enabled": true,
        "parameters_tracked": ["preferred_languages", "coding_style", "communication_preferences"],
        "adaptation_rate": 0.1,
        "min_interactions": 10
      },
      "a_b_testing": {
        "enabled": true,
        "test_allocation": "stratified",
        "metrics_tracked": ["completion_time", "user_satisfaction", "code_quality"],
        "minimum_sample_size": 100,
        "confidence_level": 0.95
      }
    }
  }
}
```

## Benefits of YAML+JSON Format

### 1. **Separation of Concerns**
- **YAML frontmatter**: Metadata, versioning, authorship
- **JSON body**: Agent logic and configuration

### 2. **Better Tooling**
- YAML frontmatter parsers are widely available
- JSON Schema validation for the body
- IDE support with autocomplete

### 3. **Human Readability**
- Metadata is easy to scan in YAML
- Complex nested structures are clearer in JSON

### 4. **Git-Friendly**
- Clear diffs for both sections
- Easier conflict resolution
- Better blame tracking

### 5. **Migration Path**
- Can progressively migrate sections
- Old tools can ignore frontmatter
- New tools get richer metadata

## Validation Rules for v3 Format

### YAML Frontmatter Requirements
```yaml
---
version: 3.0                    # REQUIRED: Must be 3.0 or higher
id: uuid-v4                     # REQUIRED: Unique identifier
name: agent_name                # REQUIRED: Matches filename
domain: domain_name             # REQUIRED: Valid domain
type: primary|sub|specialist    # REQUIRED: Agent type
status: active|deprecated|beta  # REQUIRED: Current status
author: email                    # REQUIRED: Author contact
created: ISO-8601               # REQUIRED: Creation date
modified: ISO-8601              # REQUIRED: Last modified
tags: []                        # REQUIRED: At least one tag
---
```

### JSON Body Requirements
- Must be valid JSON
- Must validate against agent-schema-v3.json
- Must include all required sections
- Must have at least one core capability
- Must define operational boundaries

## Migration Script Usage

### migrate_to_v3.py
```python
#!/usr/bin/env python3
"""
Migrate agent definitions from v2 YAML to v3 YAML+JSON format
"""

import argparse
import json
import yaml
import frontmatter
from pathlib import Path
from uuid import uuid4
from datetime import datetime

def migrate_agent(input_path, output_path=None, dry_run=False):
    """
    Migrate a single agent file to v3 format
    """
    # Implementation provided separately
    pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", help="Single file to migrate")
    parser.add_argument("--domain", help="Migrate entire domain")
    parser.add_argument("--all", action="store_true", help="Migrate all agents")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes")
    args = parser.parse_args()
    
    # Migration logic
```

## Testing After Migration

### 1. Schema Validation
```bash
python3 validate_v3.py --file agent.yaml --schema agent-schema-v3.json
```

### 2. Backwards Compatibility Test
```bash
python3 test_compatibility.py --v2-agent old.yaml --v3-agent new.yaml
```

### 3. Integration Testing
```bash
pytest tests/agent_v3_tests.py
```

## Rollback Plan

If issues arise:

```bash
# Revert to backup branch
git checkout agent-v3-migration-backup

# Cherry-pick specific successful migrations
git cherry-pick <commit-hash>

# Or revert specific files
git checkout main -- agents/agent_definitions/problematic_agent.yaml
```

## Support Resources

- **Schema**: `agent-schema-v3.json`
- **Templates**: `templates/base_agent_template_v3.yaml`
- **Examples**: `examples/fully_migrated_agent_v3.yaml`
- **Validation**: `validate_v3.py`
- **Migration**: `migrate_to_v3.py`
- **Testing**: `tests/agent_v3_tests.py`

## Timeline

- **Week 1**: Migrate base templates and engineering domain
- **Week 2**: Migrate product, project, and research domains
- **Week 3**: Migrate financial and business domains
- **Week 4**: Migrate remaining domains
- **Week 5**: Validation, testing, and documentation

## Questions?

Contact the Framework Team or open an issue in the repository.
