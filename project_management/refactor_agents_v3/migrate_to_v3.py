#!/usr/bin/env python3
"""
Migrate agent definitions from v2 YAML to v3 YAML+JSON format

Usage:
    # Migrate single file
    python3 migrate_to_v3.py --file path/to/agent.yaml

    # Migrate entire domain
    python3 migrate_to_v3.py --domain engineering

    # Migrate all agents
    python3 migrate_to_v3.py --all

    # Dry run (preview changes)
    python3 migrate_to_v3.py --all --dry-run

    # Output to different location
    python3 migrate_to_v3.py --file agent.yaml --output new_agent.yaml
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from uuid import uuid4

import yaml

try:
    import frontmatter
except ImportError:
    print("Error: python-frontmatter required. Install with: pip3 install python-frontmatter")
    sys.exit(1)


class AgentMigrator:
    """Migrates agent definitions from v2 YAML to v3 YAML+JSON format"""

    VALID_DOMAINS = {
        "business_review",
        "cloud",
        "content",
        "context",
        "education",
        "engineering",
        "financial",
        "google_apps_script",
        "model_orchestration",
        "product",
        "product_management",
        "project",
        "project_management",
        "prompt_architect",
        "public_relations",
        "research",
        "ux",
    }

    def __init__(self, dry_run=False, verbose=False):
        self.dry_run = dry_run
        self.verbose = verbose
        self.stats = {"processed": 0, "succeeded": 0, "failed": 0, "skipped": 0}

    def migrate_file(self, input_path: Path, output_path: Path | None = None) -> bool:
        """Migrate a single agent file"""
        if not output_path:
            output_path = input_path

        try:
            # Read existing YAML
            with open(input_path) as f:
                v2_data = yaml.safe_load(f)

            if not v2_data or "agent" not in v2_data:
                print(f"⚠️  Skipping {input_path}: Not a valid agent file")
                self.stats["skipped"] += 1
                return False

            # Check if already v3
            if isinstance(v2_data, dict) and v2_data.get("version") == "3.0":
                print(f"✓ Already v3: {input_path}")
                self.stats["skipped"] += 1
                return True

            # Convert to v3 format
            v3_frontmatter, v3_body = self.convert_to_v3(v2_data, input_path)

            # Create the combined content
            content = self.format_output(v3_frontmatter, v3_body)

            # Write or display
            if self.dry_run:
                print(f"\n{'='*60}")
                print(f"DRY RUN - Would write to: {output_path}")
                print("=" * 60)
                if self.verbose:
                    print(content[:1000] + "..." if len(content) > 1000 else content)
            else:
                with open(output_path, "w") as f:
                    f.write(content)
                print(f"✓ Migrated: {input_path}")

            self.stats["succeeded"] += 1
            return True

        except Exception as e:
            print(f"✗ Failed to migrate {input_path}: {e}")
            self.stats["failed"] += 1
            return False
        finally:
            self.stats["processed"] += 1

    def convert_to_v3(self, v2_data: dict, file_path: Path) -> tuple:
        """Convert v2 YAML structure to v3 YAML frontmatter + JSON body"""

        agent_data = v2_data.get("agent", {})
        identity = agent_data.get("identity", {})
        directive = agent_data.get("directive", {})
        scope = agent_data.get("scope", {})
        delegation = agent_data.get("delegation", {})
        context = agent_data.get("context", {})

        # Extract domain from path
        domain = self.extract_domain(file_path)

        # Determine agent type
        agent_type = "sub" if "subagent" in str(file_path) else "primary"

        # Create YAML frontmatter
        frontmatter = {
            "version": 3.0,
            "id": str(uuid4()),
            "name": identity.get("name", file_path.stem),
            "domain": domain,
            "type": agent_type,
            "status": identity.get("status", "active"),
            "description": identity.get("description", ""),
            "author": identity.get("author", "team@lattice-lock.com"),
            "created": identity.get("created", datetime.now().isoformat() + "Z"),
            "modified": datetime.now().isoformat() + "Z",
            "tags": identity.get("tags", [domain, agent_type]),
            "dependencies": self.extract_dependencies(delegation),
            "legacy": {
                "version": identity.get("version", "2.1.0"),
                "migration_date": datetime.now().isoformat() + "Z",
                "breaking_changes": False,
            },
        }

        # Create JSON body
        body = {
            "agent": {
                "role": self.migrate_role(identity, directive),
                "capabilities": self.migrate_capabilities(agent_data),
                "constraints": self.migrate_constraints(directive, scope),
                "context": self.migrate_context(context, scope),
                "behaviors": self.migrate_behaviors(agent_data),
                "tools": self.migrate_tools(agent_data),
                "sub_agents": self.migrate_sub_agents(delegation),
                "evaluation": self.create_evaluation(),
                "adaptation": self.create_adaptation(),
            }
        }

        return frontmatter, body

    def extract_domain(self, file_path: Path) -> str:
        """Extract domain from file path"""
        path_str = str(file_path)
        for domain in self.VALID_DOMAINS:
            if f"agents_{domain}" in path_str:
                return domain
        return "unknown"

    def extract_dependencies(self, delegation: dict) -> list[dict]:
        """Extract dependencies from delegation info"""
        deps = []
        for subagent in delegation.get("allowed_subagents", []):
            deps.append({"agent_id": subagent, "version": ">=3.0", "optional": True})
        return deps

    def migrate_role(self, identity: dict, directive: dict) -> dict:
        """Migrate role information"""
        return {
            "primary_function": directive.get("primary_goal", "TODO: Define primary function"),
            "personality_traits": {
                "tone": "professional",
                "formality_level": "moderate",
                "verbosity": "concise",
                "emotional_intelligence": "moderate",
            },
            "expertise_areas": [
                {
                    "domain": identity.get("role", "general").lower().replace(" ", "_"),
                    "proficiency": 0.8,
                }
            ],
            "response_style": {
                "preferred_format": "structured",
                "use_examples": True,
                "include_reasoning": False,
                "max_response_length": 2000,
            },
        }

    def migrate_capabilities(self, agent_data: dict) -> dict:
        """Create capabilities section from v2 data"""

        # Try to infer capabilities from agent name and description
        identity = agent_data.get("identity", {})
        agent_name = identity.get("name", "")
        description = identity.get("description", "")

        # Create a basic capability
        core_capabilities = [
            {
                "id": "primary_task",
                "description": description or "Primary capability of this agent",
                "required_inputs": [{"name": "input", "type": "string", "required": True}],
                "expected_outputs": [{"name": "result", "type": "object"}],
                "error_handling": "retry_with_backoff",
            }
        ]

        # Add specific capabilities based on agent type
        if "engineering" in agent_name:
            core_capabilities.append(
                {
                    "id": "code_review",
                    "description": "Review code for quality and standards",
                    "required_inputs": [
                        {"name": "code", "type": "string", "required": True},
                        {"name": "language", "type": "string", "required": True},
                    ],
                    "expected_outputs": [
                        {"name": "issues", "type": "array"},
                        {"name": "suggestions", "type": "array"},
                    ],
                    "error_handling": "fail_fast",
                }
            )

        return {
            "core_capabilities": core_capabilities,
            "conditional_capabilities": [],
            "learning_capabilities": {
                "can_learn_from_interactions": False,
                "memory_type": "working",
                "retention_period": "session",
                "update_frequency": "never",
            },
        }

    def migrate_constraints(self, directive: dict, scope: dict) -> dict:
        """Migrate constraints from directive and scope"""

        # Extract existing constraints
        existing_constraints = directive.get("constraints", [])
        if not isinstance(existing_constraints, list):
            existing_constraints = [existing_constraints] if existing_constraints else []

        # Add scope-based constraints
        cannot_access = scope.get("cannot_access", [])
        cannot_modify = scope.get("cannot_modify", [])

        operational_boundaries = existing_constraints.copy()

        for path in cannot_access:
            operational_boundaries.append(f"Cannot access {path}")
        for path in cannot_modify:
            operational_boundaries.append(f"Cannot modify {path}")

        if not operational_boundaries:
            operational_boundaries = ["Must operate within defined scope"]

        return {
            "operational_boundaries": operational_boundaries,
            "ethical_guidelines": [
                {
                    "principle": "transparency",
                    "rules": [
                        "Always identify as an AI agent",
                        "Disclose limitations when relevant",
                    ],
                },
                {
                    "principle": "privacy",
                    "rules": [
                        "Never store personal information without consent",
                        "Anonymize data in logs",
                    ],
                },
            ],
            "resource_limits": {
                "max_tokens_per_response": 2000,
                "max_api_calls_per_minute": 30,
                "max_sub_agent_depth": 3,
                "timeout_seconds": directive.get("timeout_seconds", 60),
            },
            "safety_rules": {
                "content_filtering": "moderate",
                "prohibited_topics": [],
                "escalation_required": ["emergency", "threat"],
            },
        }

    def migrate_context(self, context: dict, scope: dict) -> dict:
        """Migrate context management"""

        memory_persistence = context.get("memory_persistence", {})
        knowledge_sources = context.get("knowledge_sources", [])

        # Build initial context from scope
        can_access = scope.get("can_access", [])
        system_prompts = context.get("required_context", [])

        if not system_prompts:
            system_prompts = ["You are an AI agent operating within the Lattice Lock Framework"]

        return {
            "initial_context": {
                "system_prompts": system_prompts,
                "knowledge_bases": can_access[:3] if can_access else [],
            },
            "memory_management": {
                "working_memory": {
                    "capacity": "last_10_messages",
                    "retention_strategy": "sliding_window",
                },
                "long_term_memory": {
                    "enabled": bool(memory_persistence.get("long_term")),
                    "storage_backend": "vector_database",
                    "retrieval_method": "semantic_similarity",
                    "relevance_threshold": 0.7,
                },
            },
            "context_injection": [],
        }

    def migrate_behaviors(self, agent_data: dict) -> dict:
        """Create behavior specifications"""

        identity = agent_data.get("identity", {})
        agent_name = identity.get("name", "Agent")

        return {
            "greeting_protocol": {
                "initial_greeting": f"Hello! I'm the {agent_name}. How can I assist you?",
                "returning_user": "Welcome back! How can I help?",
                "context_aware": False,
            },
            "problem_solving_approach": {
                "steps": [
                    {"action": "analyze", "description": "Analyze the request"},
                    {"action": "plan", "description": "Create execution plan"},
                    {"action": "execute", "description": "Execute the task"},
                    {"action": "verify", "description": "Verify results"},
                ]
            },
            "escalation_behavior": {
                "triggers": [
                    {"condition": "confidence < 0.5", "action": "request_review"},
                    {"condition": "error_count > 3", "action": "escalate"},
                ],
                "escalation_message": "I need to escalate this issue for further assistance.",
            },
            "error_handling": {
                "unknown_error": "An unexpected error occurred. Please try again.",
                "rate_limit": "Rate limit reached. Please wait before retrying.",
                "timeout": "Operation timed out. Please try again.",
            },
        }

    def migrate_tools(self, agent_data: dict) -> dict:
        """Create tools configuration"""
        return {
            "available_tools": [],
            "tool_selection_strategy": {
                "method": "best_match",
                "fallback_behavior": "return_error",
                "parallel_execution": False,
                "max_concurrent_tools": 1,
            },
        }

    def migrate_sub_agents(self, delegation: dict) -> list[dict]:
        """Migrate sub-agent configuration"""

        if not delegation.get("enabled"):
            return []

        sub_agents = []
        for subagent in delegation.get("allowed_subagents", []):
            # Handle both string and dict formats
            if isinstance(subagent, str):
                agent_id = subagent
                agent_file = f"subagents/{subagent}_definition.yaml"
            else:
                agent_id = subagent.get("name", subagent)
                agent_file = subagent.get("file", f"subagents/{agent_id}_definition.yaml")

            sub_agents.append(
                {
                    "agent_id": agent_id,
                    "agent_file": agent_file,
                    "trigger_conditions": [f"task_requires('{agent_id}')"],
                    "handoff_protocol": {
                        "context_transfer": "selective",
                        "included_context": ["requirements", "constraints"],
                        "return_control": "on_completion",
                        "timeout": 300,
                        "max_retries": 2,
                    },
                }
            )

        return sub_agents

    def create_evaluation(self) -> dict:
        """Create default evaluation metrics"""
        return {
            "success_metrics": [
                {
                    "metric": "task_completion_rate",
                    "target": 0.95,
                    "measurement_window": "daily",
                    "calculation_method": "completed / total",
                }
            ],
            "quality_checks": [
                {"check": "response_quality", "method": "rule_based", "threshold": 0.8}
            ],
        }

    def create_adaptation(self) -> dict:
        """Create default adaptation configuration"""
        return {
            "learning_mechanism": {
                "type": "none",
                "feedback_sources": [],
                "update_frequency": "never",
            },
            "personalization": {"enabled": False, "parameters_tracked": [], "adaptation_rate": 0.0},
            "a_b_testing": {
                "enabled": False,
                "test_allocation": "none",
                "metrics_tracked": [],
                "minimum_sample_size": 0,
            },
        }

    def format_output(self, frontmatter: dict, body: dict) -> str:
        """Format the output as YAML frontmatter + JSON body"""

        # Format YAML frontmatter
        yaml_str = yaml.dump(frontmatter, default_flow_style=False, sort_keys=False)

        # Format JSON body with proper indentation
        json_str = json.dumps(body, indent=2, ensure_ascii=False)

        # Combine with proper separators
        output = "---\n"
        output += "# YAML Frontmatter - Metadata and configuration\n"
        output += yaml_str
        output += "---\n"
        output += json_str

        return output

    def migrate_domain(self, domain: str) -> bool:
        """Migrate all agents in a domain"""

        if domain not in self.VALID_DOMAINS:
            print(f"✗ Invalid domain: {domain}")
            return False

        base_path = Path(f"../../agents/agent_definitions/agents_{domain}")

        if not base_path.exists():
            print(f"✗ Domain path not found: {base_path}")
            return False

        # Find all YAML files in domain
        yaml_files = list(base_path.glob("**/*.yaml"))

        print(f"\nMigrating {len(yaml_files)} files in {domain} domain...")

        for yaml_file in yaml_files:
            self.migrate_file(yaml_file)

        return True

    def migrate_all(self) -> bool:
        """Migrate all agent domains"""

        print("Migrating all agent domains...")

        for domain in sorted(self.VALID_DOMAINS):
            print(f"\n{'='*60}")
            print(f"Domain: {domain}")
            print("=" * 60)
            self.migrate_domain(domain)

        return True

    def print_summary(self):
        """Print migration summary"""
        print(f"\n{'='*60}")
        print("Migration Summary")
        print("=" * 60)
        print(f"Total processed: {self.stats['processed']}")
        print(f"✓ Succeeded: {self.stats['succeeded']}")
        print(f"✗ Failed: {self.stats['failed']}")
        print(f"⚠ Skipped: {self.stats['skipped']}")

        if self.dry_run:
            print("\n🔍 This was a DRY RUN - no files were modified")

        success_rate = (
            (self.stats["succeeded"] / self.stats["processed"] * 100)
            if self.stats["processed"] > 0
            else 0
        )
        print(f"\nSuccess rate: {success_rate:.1f}%")


def main():
    parser = argparse.ArgumentParser(
        description="Migrate agent definitions from v2 YAML to v3 YAML+JSON format"
    )

    # Input options (mutually exclusive)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--file", help="Single file to migrate")
    group.add_argument("--domain", help="Migrate entire domain")
    group.add_argument("--all", action="store_true", help="Migrate all agents")

    # Other options
    parser.add_argument("--output", help="Output file (for single file migration)")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    parser.add_argument("--verbose", action="store_true", help="Show detailed output")

    args = parser.parse_args()

    # Create migrator
    migrator = AgentMigrator(dry_run=args.dry_run, verbose=args.verbose)

    # Execute migration
    if args.file:
        input_path = Path(args.file)
        output_path = Path(args.output) if args.output else None
        migrator.migrate_file(input_path, output_path)

    elif args.domain:
        migrator.migrate_domain(args.domain)

    elif args.all:
        migrator.migrate_all()

    # Print summary
    migrator.print_summary()


if __name__ == "__main__":
    main()
