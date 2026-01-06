# Documentation Shadow Map

Generated report linking source files to documentation.

## Documentation with IDs

| File ID | Document Path |
|---------|---------------|
| `api-admin-001` | `docs/02-technical/api/api_admin.md` |
| `api-compiler-001` | `docs/02-technical/api/api_compiler.md` |
| `api-gauntlet-001` | `docs/02-technical/api/api_gauntlet.md` |
| `api-index-001` | `docs/02-technical/api/api_index.md` |
| `api-orch-001` | `docs/02-technical/api/api_orchestrator.md` |
| `api-sheriff-001` | `docs/02-technical/api/api_sheriff.md` |
| `api-validator-001` | `docs/02-technical/api/api_validator.md` |
| `cap-contract-001` | `docs/01-concepts/design/orchestrator_capabilities_contract.md` |
| `cli-admin-001` | `docs/02-technical/reference/cli/admin.md` |
| `cli-compile-001` | `docs/02-technical/reference/cli/compile.md` |
| `cli-doctor-001` | `docs/02-technical/reference/cli/doctor.md` |
| `cli-feedback-001` | `docs/02-technical/reference/cli/feedback.md` |
| `cli-gauntlet-001` | `docs/02-technical/reference/cli/gauntlet.md` |
| `cli-index-001` | `docs/02-technical/reference/cli/index.md` |
| `cli-init-001` | `docs/02-technical/reference/cli/init.md` |
| `cli-orch-001` | `docs/02-technical/reference/cli/orchestrator.md` |
| `cli-sheriff-001` | `docs/02-technical/reference/cli/sheriff.md` |
| `cli-validate-001` | `docs/02-technical/reference/cli/validate.md` |
| `concept-agents-001` | `docs/01-concepts/agents.md` |
| `concept-features-001` | `docs/01-concepts/features/FEATURES.md` |
| `concept-features-002` | `docs/01-concepts/features/lattice_lock_features.md` |
| `concept-models-001` | `docs/01-concepts/models.md` |
| `config-ref-001` | `docs/02-technical/reference/configuration.md` |
| `cost-telemetry-001` | `docs/01-concepts/design/cost_telemetry_strategy.md` |
| `db-migration-001` | `docs/02-technical/reference/database/migration_strategy.md` |
| `db-readiness-001` | `docs/02-technical/reference/database/readiness_checklist.md` |
| `doc-index-001` | `docs/index.md` |
| `domain-model-001` | `docs/01-concepts/architecture/domain_model.md` |
| `fallback-strat-001` | `docs/01-concepts/design/provider_fallback_strategy.md` |
| `framework-spec-001` | `docs/02-technical/reference/lattice_lock_framework_specifications.md` |
| `gov-core-001` | `docs/02-technical/reference/governance_core_spec.md` |
| `guide-config-001` | `docs/02-guides/guides/configuration.md` |
| `guide-gov-001` | `docs/02-guides/guides/governance.md` |
| `guide-install-001` | `docs/02-guides/guides/installation.md` |
| `guide-quickstart-001` | `docs/02-guides/guides/quick_start.md` |
| `guide-troubleshoot-001` | `docs/02-guides/guides/troubleshooting.md` |
| `mod-consensus-001` | `docs/02-technical/reference/modules/consensus.md` |
| `mod-orchestrator-001` | `docs/02-technical/reference/modules/orchestrator.md` |
| `mod-sheriff-001` | `docs/02-technical/reference/modules/sheriff.md` |
| `orch-arch-001` | `docs/01-concepts/architecture/model_orchestrator_architecture.md` |
| `sys-design-001` | `docs/01-concepts/architecture/system_design.md` |
| `token-storage-001` | `docs/01-concepts/design/token_storage_production.md` |
| `tut-ci-001` | `docs/02-guides/tutorials/ci_integration.md` |
| `tut-first-proj-001` | `docs/02-guides/tutorials/first_project.md` |
| `tut-getting-started-001` | `docs/02-guides/tutorials/getting_started.md` |
| `tut-model-sel-001` | `docs/02-guides/tutorials/tutorial_1__basic_model_selection.md` |
| `tut-validation-001` | `docs/02-guides/tutorials/adding_validation.md` |
| `unique-uuid-v4` | `docs/04-meta/metadata_standards.md` |

## User-Facing Source Files Scan

Total Python files found: 308

## Potential Gaps (Heuristic Match)

| Source File | Potential Doc Match (by name) | Status |
|-------------|-------------------------------|--------|
| `src/admin/api.py` | `docs/02-technical/api/api_sheriff.md` (`api-sheriff-001`) | ✅ |
| `src/admin/auth/api_keys.py` | - | ⚠️ |
| `src/admin/auth/config.py` | `docs/02-guides/guides/configuration.md` (`guide-config-001`) | ✅ |
| `src/admin/auth/dependencies.py` | - | ⚠️ |
| `src/admin/auth/models.py` | `docs/01-concepts/models.md` (`concept-models-001`) | ✅ |
| `src/admin/auth/passwords.py` | - | ⚠️ |
| `src/admin/auth/service.py` | - | ⚠️ |
| `src/admin/auth/storage.py` | `docs/01-concepts/design/token_storage_production.md` (`token-storage-001`) | ✅ |
| `src/admin/auth/tokens.py` | - | ⚠️ |
| `src/admin/auth/users.py` | - | ⚠️ |
| `src/admin/auth_routes.py` | - | ⚠️ |
| `src/admin/db.py` | `docs/02-technical/reference/database/readiness_checklist.md` (`db-readiness-001`) | ✅ |
| `src/admin/models.py` | `docs/01-concepts/models.md` (`concept-models-001`) | ✅ |
| `src/admin/routes.py` | - | ⚠️ |
| `src/admin/schemas.py` | - | ⚠️ |
| `src/admin/services.py` | - | ⚠️ |
| `src/admin/ui.py` | `docs/02-guides/guides/troubleshooting.md` (`guide-troubleshoot-001`) | ✅ |
| `src/agents/prompt_architect/agent.py` | `docs/01-concepts/agents.md` (`concept-agents-001`) | ✅ |
| `src/agents/prompt_architect/cli.py` | `docs/02-technical/reference/cli/compile.md` (`cli-compile-001`) | ✅ |
| `src/agents/prompt_architect/engine.py` | - | ⚠️ |
| `src/agents/prompt_architect/integrations/project_agent.py` | - | ⚠️ |
| `src/agents/prompt_architect/models.py` | `docs/01-concepts/models.md` (`concept-models-001`) | ✅ |
| `src/agents/prompt_architect/orchestrator.py` | `docs/02-technical/reference/modules/orchestrator.md` (`mod-orchestrator-001`) | ✅ |
| `src/agents/prompt_architect/subagents/models.py` | `docs/01-concepts/models.md` (`concept-models-001`) | ✅ |
| `src/agents/prompt_architect/subagents/parsers/roadmap_parser.py` | - | ⚠️ |
| `src/agents/prompt_architect/subagents/parsers/spec_parser.py` | - | ⚠️ |
| `src/agents/prompt_architect/subagents/prompt_generator.py` | - | ⚠️ |
| `src/agents/prompt_architect/subagents/roadmap_parser.py` | - | ⚠️ |
| `src/agents/prompt_architect/subagents/spec_analyzer.py` | - | ⚠️ |
| `src/agents/prompt_architect/subagents/tool_matcher.py` | - | ⚠️ |
| `src/agents/prompt_architect/subagents/tool_profiles.py` | - | ⚠️ |
| `src/agents/prompt_architect/tracker_client.py` | - | ⚠️ |
| `src/agents/prompt_architect/validators/convention_checker.py` | - | ⚠️ |
| `src/agents/prompt_architect/validators/prompt_validator.py` | - | ⚠️ |
| `src/agents/prompt_architect/validators/quality_scorer.py` | - | ⚠️ |
| `src/agents/prompt_architect/validators/utils.py` | - | ⚠️ |
| `src/cli/__main__.py` | - | ⚠️ |
| `src/cli/commands/admin.py` | `docs/02-technical/api/api_admin.md` (`api-admin-001`) | ✅ |
| `src/cli/commands/ask.py` | - | ⚠️ |
| `src/cli/commands/chain.py` | - | ⚠️ |
| `src/cli/commands/compile.py` | `docs/02-technical/api/api_compiler.md` (`api-compiler-001`) | ✅ |
| `src/cli/commands/doctor.py` | `docs/02-technical/reference/cli/doctor.md` (`cli-doctor-001`) | ✅ |
| `src/cli/commands/feedback.py` | `docs/02-technical/reference/cli/feedback.md` (`cli-feedback-001`) | ✅ |
| `src/cli/commands/gauntlet.py` | `docs/02-technical/api/api_gauntlet.md` (`api-gauntlet-001`) | ✅ |
| `src/cli/commands/handoff.py` | - | ⚠️ |
| `src/cli/commands/init.py` | `docs/02-technical/reference/cli/init.md` (`cli-init-001`) | ✅ |
| `src/cli/commands/mcp.py` | - | ⚠️ |
| `src/cli/commands/rollback.py` | - | ⚠️ |
| `src/cli/commands/sheriff.py` | `docs/02-technical/api/api_sheriff.md` (`api-sheriff-001`) | ✅ |
| `src/cli/commands/validate.py` | `docs/02-technical/reference/cli/validate.md` (`cli-validate-001`) | ✅ |
| `src/cli/groups/admin.py` | `docs/02-technical/api/api_admin.md` (`api-admin-001`) | ✅ |
| `src/cli/groups/orchestrator.py` | `docs/02-technical/reference/modules/orchestrator.md` (`mod-orchestrator-001`) | ✅ |
| `src/cli/utils/console.py` | - | ⚠️ |
| `src/compile.py` | `docs/02-technical/api/api_compiler.md` (`api-compiler-001`) | ✅ |
| `src/compiler/core.py` | `docs/02-technical/reference/governance_core_spec.md` (`gov-core-001`) | ✅ |
| `src/compiler/formats.py` | - | ⚠️ |
| `src/compiler/normalizer.py` | - | ⚠️ |
| `src/config/app_config.py` | - | ⚠️ |
| `src/config/compiler.py` | `docs/02-technical/api/api_compiler.md` (`api-compiler-001`) | ✅ |
| `src/config/feature_flags.py` | - | ⚠️ |
| `src/config/frontmatter.py` | - | ⚠️ |
| `src/config/inheritance.py` | - | ⚠️ |
| `src/config/normalizer.py` | - | ⚠️ |
| `src/consensus/engine.py` | - | ⚠️ |
| `src/consensus/templates.py` | - | ⚠️ |
| `src/consensus/types.py` | - | ⚠️ |
| `src/context/serialization.py` | - | ⚠️ |
| `src/dashboard/aggregator.py` | - | ⚠️ |
| `src/dashboard/backend.py` | - | ⚠️ |
| `src/dashboard/generator.py` | - | ⚠️ |
| `src/dashboard/metrics.py` | - | ⚠️ |
| `src/dashboard/mock_data.py` | - | ⚠️ |
| `src/dashboard/websocket.py` | - | ⚠️ |
| `src/database/connection.py` | - | ⚠️ |
| `src/database/gcp_clients.py` | - | ⚠️ |
| `src/database/health.py` | - | ⚠️ |
| `src/database/models/base.py` | - | ⚠️ |
| `src/database/models/models.py` | `docs/01-concepts/models.md` (`concept-models-001`) | ✅ |
| `src/database/models/user.py` | - | ⚠️ |
| `src/database/repositories/base.py` | - | ⚠️ |
| `src/database/repositories/preferences_repository.py` | - | ⚠️ |
| `src/database/repositories/user_repository.py` | - | ⚠️ |
| `src/database/repository.py` | - | ⚠️ |
| `src/database/transaction.py` | - | ⚠️ |
| `src/errors/classification.py` | - | ⚠️ |
| `src/errors/middleware.py` | - | ⚠️ |
| `src/errors/remediation.py` | - | ⚠️ |
| `src/errors/types.py` | - | ⚠️ |
| `src/exceptions.py` | - | ⚠️ |
| `src/feedback/collector.py` | - | ⚠️ |
| `src/feedback/schemas.py` | - | ⚠️ |
| `src/gauntlet/generator.py` | - | ⚠️ |
| `src/gauntlet/parser.py` | - | ⚠️ |
| `src/gauntlet/plugin.py` | - | ⚠️ |
| `src/gauntlet/validator.py` | `docs/02-technical/api/api_validator.md` (`api-validator-001`) | ✅ |
| `src/generated/src.generated_pydantic.py` | - | ⚠️ |
| `src/generated/tests/test_contract_Customer.py` | - | ⚠️ |
| `src/generated/tests/test_contract_Order.py` | - | ⚠️ |
| `src/generated/tests/test_contract_user.py` | - | ⚠️ |
| `src/generated/types.py` | - | ⚠️ |
| `src/generated/types_v2_pydantic.py` | - | ⚠️ |
| `src/lattice_lock/admin/api.py` | `docs/02-technical/api/api_sheriff.md` (`api-sheriff-001`) | ✅ |
| `src/lattice_lock/admin/auth/api_keys.py` | - | ⚠️ |
| `src/lattice_lock/admin/auth/config.py` | `docs/02-guides/guides/configuration.md` (`guide-config-001`) | ✅ |
| `src/lattice_lock/admin/auth/dependencies.py` | - | ⚠️ |
| `src/lattice_lock/admin/auth/models.py` | `docs/01-concepts/models.md` (`concept-models-001`) | ✅ |
| `src/lattice_lock/admin/auth/passwords.py` | - | ⚠️ |
| `src/lattice_lock/admin/auth/service.py` | - | ⚠️ |
| `src/lattice_lock/admin/auth/storage.py` | `docs/01-concepts/design/token_storage_production.md` (`token-storage-001`) | ✅ |
| `src/lattice_lock/admin/auth/tokens.py` | - | ⚠️ |
| `src/lattice_lock/admin/auth/users.py` | - | ⚠️ |
| `src/lattice_lock/admin/auth_routes.py` | - | ⚠️ |
| `src/lattice_lock/admin/db.py` | `docs/02-technical/reference/database/readiness_checklist.md` (`db-readiness-001`) | ✅ |
| `src/lattice_lock/admin/models.py` | `docs/01-concepts/models.md` (`concept-models-001`) | ✅ |
| `src/lattice_lock/admin/routes.py` | - | ⚠️ |
| `src/lattice_lock/admin/schemas.py` | - | ⚠️ |
| `src/lattice_lock/admin/services.py` | - | ⚠️ |
| `src/lattice_lock/admin/ui.py` | `docs/02-guides/guides/troubleshooting.md` (`guide-troubleshoot-001`) | ✅ |
| `src/lattice_lock/agents/prompt_architect/agent.py` | `docs/01-concepts/agents.md` (`concept-agents-001`) | ✅ |
| `src/lattice_lock/agents/prompt_architect/cli.py` | `docs/02-technical/reference/cli/compile.md` (`cli-compile-001`) | ✅ |
| `src/lattice_lock/agents/prompt_architect/engine.py` | - | ⚠️ |
| `src/lattice_lock/agents/prompt_architect/integrations/project_agent.py` | - | ⚠️ |
| `src/lattice_lock/agents/prompt_architect/models.py` | `docs/01-concepts/models.md` (`concept-models-001`) | ✅ |
| `src/lattice_lock/agents/prompt_architect/orchestrator.py` | `docs/02-technical/reference/modules/orchestrator.md` (`mod-orchestrator-001`) | ✅ |
| `src/lattice_lock/agents/prompt_architect/subagents/models.py` | `docs/01-concepts/models.md` (`concept-models-001`) | ✅ |
| `src/lattice_lock/agents/prompt_architect/subagents/parsers/roadmap_parser.py` | - | ⚠️ |
| `src/lattice_lock/agents/prompt_architect/subagents/parsers/spec_parser.py` | - | ⚠️ |
| `src/lattice_lock/agents/prompt_architect/subagents/prompt_generator.py` | - | ⚠️ |
| `src/lattice_lock/agents/prompt_architect/subagents/roadmap_parser.py` | - | ⚠️ |
| `src/lattice_lock/agents/prompt_architect/subagents/spec_analyzer.py` | - | ⚠️ |
| `src/lattice_lock/agents/prompt_architect/subagents/tool_matcher.py` | - | ⚠️ |
| `src/lattice_lock/agents/prompt_architect/subagents/tool_profiles.py` | - | ⚠️ |
| `src/lattice_lock/agents/prompt_architect/tracker_client.py` | - | ⚠️ |
| `src/lattice_lock/agents/prompt_architect/validators/convention_checker.py` | - | ⚠️ |
| `src/lattice_lock/agents/prompt_architect/validators/prompt_validator.py` | - | ⚠️ |
| `src/lattice_lock/agents/prompt_architect/validators/quality_scorer.py` | - | ⚠️ |
| `src/lattice_lock/agents/prompt_architect/validators/utils.py` | - | ⚠️ |
| `src/lattice_lock/cli/__main__.py` | - | ⚠️ |
| `src/lattice_lock/cli/commands/admin.py` | `docs/02-technical/api/api_admin.md` (`api-admin-001`) | ✅ |
| `src/lattice_lock/cli/commands/ask.py` | - | ⚠️ |
| `src/lattice_lock/cli/commands/chain.py` | - | ⚠️ |
| `src/lattice_lock/cli/commands/compile.py` | `docs/02-technical/api/api_compiler.md` (`api-compiler-001`) | ✅ |
| `src/lattice_lock/cli/commands/config.py` | `docs/02-guides/guides/configuration.md` (`guide-config-001`) | ✅ |
| `src/lattice_lock/cli/commands/doctor.py` | `docs/02-technical/reference/cli/doctor.md` (`cli-doctor-001`) | ✅ |
| `src/lattice_lock/cli/commands/feedback.py` | `docs/02-technical/reference/cli/feedback.md` (`cli-feedback-001`) | ✅ |
| `src/lattice_lock/cli/commands/gauntlet.py` | `docs/02-technical/api/api_gauntlet.md` (`api-gauntlet-001`) | ✅ |
| `src/lattice_lock/cli/commands/handoff.py` | - | ⚠️ |
| `src/lattice_lock/cli/commands/init.py` | `docs/02-technical/reference/cli/init.md` (`cli-init-001`) | ✅ |
| `src/lattice_lock/cli/commands/mcp.py` | - | ⚠️ |
| `src/lattice_lock/cli/commands/rollback.py` | - | ⚠️ |
| `src/lattice_lock/cli/commands/sheriff.py` | `docs/02-technical/api/api_sheriff.md` (`api-sheriff-001`) | ✅ |
| `src/lattice_lock/cli/commands/validate.py` | `docs/02-technical/reference/cli/validate.md` (`cli-validate-001`) | ✅ |
| `src/lattice_lock/cli/groups/admin.py` | `docs/02-technical/api/api_admin.md` (`api-admin-001`) | ✅ |
| `src/lattice_lock/cli/groups/orchestrator.py` | `docs/02-technical/reference/modules/orchestrator.md` (`mod-orchestrator-001`) | ✅ |
| `src/lattice_lock/cli/utils/console.py` | - | ⚠️ |
| `src/lattice_lock/compile.py` | `docs/02-technical/api/api_compiler.md` (`api-compiler-001`) | ✅ |
| `src/lattice_lock/config/app_config.py` | - | ⚠️ |
| `src/lattice_lock/config/compiler.py` | `docs/02-technical/api/api_compiler.md` (`api-compiler-001`) | ✅ |
| `src/lattice_lock/config/feature_flags.py` | - | ⚠️ |
| `src/lattice_lock/config/frontmatter.py` | - | ⚠️ |
| `src/lattice_lock/config/inheritance.py` | - | ⚠️ |
| `src/lattice_lock/config/normalizer.py` | - | ⚠️ |
| `src/lattice_lock/context/serialization.py` | - | ⚠️ |
| `src/lattice_lock/dashboard/aggregator.py` | - | ⚠️ |
| `src/lattice_lock/dashboard/backend.py` | - | ⚠️ |
| `src/lattice_lock/dashboard/generator.py` | - | ⚠️ |
| `src/lattice_lock/dashboard/metrics.py` | - | ⚠️ |
| `src/lattice_lock/dashboard/mock_data.py` | - | ⚠️ |
| `src/lattice_lock/dashboard/websocket.py` | - | ⚠️ |
| `src/lattice_lock/database/connection.py` | - | ⚠️ |
| `src/lattice_lock/database/gcp_clients.py` | - | ⚠️ |
| `src/lattice_lock/database/health.py` | - | ⚠️ |
| `src/lattice_lock/database/models/base.py` | - | ⚠️ |
| `src/lattice_lock/database/models/models.py` | `docs/01-concepts/models.md` (`concept-models-001`) | ✅ |
| `src/lattice_lock/database/models/user.py` | - | ⚠️ |
| `src/lattice_lock/database/repositories/base.py` | - | ⚠️ |
| `src/lattice_lock/database/repositories/preferences_repository.py` | - | ⚠️ |
| `src/lattice_lock/database/repositories/user_repository.py` | - | ⚠️ |
| `src/lattice_lock/database/repository.py` | - | ⚠️ |
| `src/lattice_lock/database/transaction.py` | - | ⚠️ |
| `src/lattice_lock/errors/classification.py` | - | ⚠️ |
| `src/lattice_lock/errors/middleware.py` | - | ⚠️ |
| `src/lattice_lock/errors/remediation.py` | - | ⚠️ |
| `src/lattice_lock/errors/types.py` | - | ⚠️ |
| `src/lattice_lock/exceptions.py` | - | ⚠️ |
| `src/lattice_lock/feedback/collector.py` | - | ⚠️ |
| `src/lattice_lock/feedback/schemas.py` | - | ⚠️ |
| `src/lattice_lock/gauntlet/generator.py` | - | ⚠️ |
| `src/lattice_lock/gauntlet/parser.py` | - | ⚠️ |
| `src/lattice_lock/gauntlet/plugin.py` | - | ⚠️ |
| `src/lattice_lock/gauntlet/validator.py` | `docs/02-technical/api/api_validator.md` (`api-validator-001`) | ✅ |
| `src/lattice_lock/logging_config.py` | - | ⚠️ |
| `src/lattice_lock/mcp/context.py` | - | ⚠️ |
| `src/lattice_lock/mcp/server.py` | - | ⚠️ |
| `src/lattice_lock/mcp/templates.py` | - | ⚠️ |
| `src/lattice_lock/mcp/tools.py` | - | ⚠️ |
| `src/lattice_lock/orchestrator/analysis/analyzer.py` | - | ⚠️ |
| `src/lattice_lock/orchestrator/analysis/semantic_router.py` | - | ⚠️ |
| `src/lattice_lock/orchestrator/analysis/types.py` | - | ⚠️ |
| `src/lattice_lock/orchestrator/api_clients.py` | - | ⚠️ |
| `src/lattice_lock/orchestrator/chain.py` | - | ⚠️ |
| `src/lattice_lock/orchestrator/cli/cost_command.py` | - | ⚠️ |
| `src/lattice_lock/orchestrator/consensus/engine.py` | - | ⚠️ |
| `src/lattice_lock/orchestrator/core.py` | `docs/02-technical/reference/governance_core_spec.md` (`gov-core-001`) | ✅ |
| `src/lattice_lock/orchestrator/cost/models.py` | `docs/01-concepts/models.md` (`concept-models-001`) | ✅ |
| `src/lattice_lock/orchestrator/cost/storage.py` | `docs/01-concepts/design/token_storage_production.md` (`token-storage-001`) | ✅ |
| `src/lattice_lock/orchestrator/cost/tracker.py` | - | ⚠️ |
| `src/lattice_lock/orchestrator/exceptions.py` | - | ⚠️ |
| `src/lattice_lock/orchestrator/execution/client_pool.py` | - | ⚠️ |
| `src/lattice_lock/orchestrator/execution/conversation.py` | - | ⚠️ |
| `src/lattice_lock/orchestrator/function_calling.py` | - | ⚠️ |
| `src/lattice_lock/orchestrator/grok_api.py` | - | ⚠️ |
| `src/lattice_lock/orchestrator/guide.py` | `docs/02-guides/guides/troubleshooting.md` (`guide-troubleshoot-001`) | ✅ |
| `src/lattice_lock/orchestrator/models_schema.py` | - | ⚠️ |
| `src/lattice_lock/orchestrator/providers/anthropic.py` | - | ⚠️ |
| `src/lattice_lock/orchestrator/providers/azure.py` | - | ⚠️ |
| `src/lattice_lock/orchestrator/providers/base.py` | - | ⚠️ |
| `src/lattice_lock/orchestrator/providers/bedrock.py` | - | ⚠️ |
| `src/lattice_lock/orchestrator/providers/factory.py` | - | ⚠️ |
| `src/lattice_lock/orchestrator/providers/fallback.py` | `docs/01-concepts/design/provider_fallback_strategy.md` (`fallback-strat-001`) | ✅ |
| `src/lattice_lock/orchestrator/providers/google.py` | - | ⚠️ |
| `src/lattice_lock/orchestrator/providers/local.py` | - | ⚠️ |
| `src/lattice_lock/orchestrator/providers/openai.py` | - | ⚠️ |
| `src/lattice_lock/orchestrator/providers/xai.py` | - | ⚠️ |
| `src/lattice_lock/orchestrator/registry.py` | - | ⚠️ |
| `src/lattice_lock/orchestrator/routing/analyzer.py` | - | ⚠️ |
| `src/lattice_lock/orchestrator/scorer.py` | - | ⚠️ |
| `src/lattice_lock/orchestrator/scoring/model_scorer.py` | - | ⚠️ |
| `src/lattice_lock/orchestrator/selection/model_selector.py` | - | ⚠️ |
| `src/lattice_lock/orchestrator/types.py` | - | ⚠️ |
| `src/lattice_lock/rollback/checkpoint.py` | - | ⚠️ |
| `src/lattice_lock/rollback/state.py` | - | ⚠️ |
| `src/lattice_lock/rollback/storage.py` | `docs/01-concepts/design/token_storage_production.md` (`token-storage-001`) | ✅ |
| `src/lattice_lock/rollback/trigger.py` | - | ⚠️ |
| `src/lattice_lock/sheriff/ast_visitor.py` | - | ⚠️ |
| `src/lattice_lock/sheriff/cache.py` | - | ⚠️ |
| `src/lattice_lock/sheriff/config.py` | `docs/02-guides/guides/configuration.md` (`guide-config-001`) | ✅ |
| `src/lattice_lock/sheriff/formatters.py` | - | ⚠️ |
| `src/lattice_lock/sheriff/rules.py` | - | ⚠️ |
| `src/lattice_lock/sheriff/sheriff.py` | `docs/02-technical/api/api_sheriff.md` (`api-sheriff-001`) | ✅ |
| `src/lattice_lock/tracing.py` | - | ⚠️ |
| `src/lattice_lock/types.py` | - | ⚠️ |
| `src/lattice_lock/utils/async_compat.py` | - | ⚠️ |
| `src/lattice_lock/utils/jinja.py` | - | ⚠️ |
| `src/lattice_lock/utils/logging.py` | - | ⚠️ |
| `src/lattice_lock/utils/safe_path.py` | - | ⚠️ |
| `src/lattice_lock/validator/agents.py` | `docs/01-concepts/agents.md` (`concept-agents-001`) | ✅ |
| `src/lattice_lock/validator/env.py` | - | ⚠️ |
| `src/lattice_lock/validator/schema.py` | - | ⚠️ |
| `src/lattice_lock/validator/structure.py` | - | ⚠️ |
| `src/lattice_mcp/context.py` | - | ⚠️ |
| `src/lattice_mcp/server.py` | - | ⚠️ |
| `src/lattice_mcp/templates.py` | - | ⚠️ |
| `src/lattice_mcp/tools.py` | - | ⚠️ |
| `src/logging_config.py` | - | ⚠️ |
| `src/orchestrator/analysis/analyzer.py` | - | ⚠️ |
| `src/orchestrator/analysis/semantic_router.py` | - | ⚠️ |
| `src/orchestrator/analysis/types.py` | - | ⚠️ |
| `src/orchestrator/api_clients.py` | - | ⚠️ |
| `src/orchestrator/chain.py` | - | ⚠️ |
| `src/orchestrator/cli/cost_command.py` | - | ⚠️ |
| `src/orchestrator/consensus/engine.py` | - | ⚠️ |
| `src/orchestrator/core.py` | `docs/02-technical/reference/governance_core_spec.md` (`gov-core-001`) | ✅ |
| `src/orchestrator/cost/models.py` | `docs/01-concepts/models.md` (`concept-models-001`) | ✅ |
| `src/orchestrator/cost/storage.py` | `docs/01-concepts/design/token_storage_production.md` (`token-storage-001`) | ✅ |
| `src/orchestrator/cost/tracker.py` | - | ⚠️ |
| `src/orchestrator/exceptions.py` | - | ⚠️ |
| `src/orchestrator/execution/client_pool.py` | - | ⚠️ |
| `src/orchestrator/execution/conversation.py` | - | ⚠️ |
| `src/orchestrator/function_calling.py` | - | ⚠️ |
| `src/orchestrator/grok_api.py` | - | ⚠️ |
| `src/orchestrator/guide.py` | `docs/02-guides/guides/troubleshooting.md` (`guide-troubleshoot-001`) | ✅ |
| `src/orchestrator/models_schema.py` | - | ⚠️ |
| `src/orchestrator/providers/anthropic.py` | - | ⚠️ |
| `src/orchestrator/providers/azure.py` | - | ⚠️ |
| `src/orchestrator/providers/base.py` | - | ⚠️ |
| `src/orchestrator/providers/bedrock.py` | - | ⚠️ |
| `src/orchestrator/providers/factory.py` | - | ⚠️ |
| `src/orchestrator/providers/fallback.py` | `docs/01-concepts/design/provider_fallback_strategy.md` (`fallback-strat-001`) | ✅ |
| `src/orchestrator/providers/google.py` | - | ⚠️ |
| `src/orchestrator/providers/local.py` | - | ⚠️ |
| `src/orchestrator/providers/openai.py` | - | ⚠️ |
| `src/orchestrator/providers/xai.py` | - | ⚠️ |
| `src/orchestrator/registry.py` | - | ⚠️ |
| `src/orchestrator/routing/analyzer.py` | - | ⚠️ |
| `src/orchestrator/scorer.py` | - | ⚠️ |
| `src/orchestrator/scoring/model_scorer.py` | - | ⚠️ |
| `src/orchestrator/selection/model_selector.py` | - | ⚠️ |
| `src/orchestrator/types.py` | - | ⚠️ |
| `src/rollback/checkpoint.py` | - | ⚠️ |
| `src/rollback/state.py` | - | ⚠️ |
| `src/rollback/storage.py` | `docs/01-concepts/design/token_storage_production.md` (`token-storage-001`) | ✅ |
| `src/rollback/trigger.py` | - | ⚠️ |
| `src/sheriff/ast_visitor.py` | - | ⚠️ |
| `src/sheriff/cache.py` | - | ⚠️ |
| `src/sheriff/config.py` | `docs/02-guides/guides/configuration.md` (`guide-config-001`) | ✅ |
| `src/sheriff/formatters.py` | - | ⚠️ |
| `src/sheriff/rules.py` | - | ⚠️ |
| `src/sheriff/sheriff.py` | `docs/02-technical/api/api_sheriff.md` (`api-sheriff-001`) | ✅ |
| `src/tracing.py` | - | ⚠️ |
| `src/utils/async_compat.py` | - | ⚠️ |
| `src/utils/jinja.py` | - | ⚠️ |
| `src/utils/logging.py` | - | ⚠️ |
| `src/utils/safe_path.py` | - | ⚠️ |
| `src/validator/agents.py` | `docs/01-concepts/agents.md` (`concept-agents-001`) | ✅ |
| `src/validator/env.py` | - | ⚠️ |
| `src/validator/schema.py` | - | ⚠️ |
| `src/validator/structure.py` | - | ⚠️ |
