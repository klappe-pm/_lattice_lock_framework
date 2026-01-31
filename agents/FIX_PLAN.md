# Agent Validation Fix Plan

**Generated**: 2026-01-10
**Total Agents**: 762
**Valid**: 736 (96.6%)
**Invalid**: 26 (3.4%)
**Average Score**: 88.8/100

---

## Executive Summary

| Priority | Issue Type | Count | Auto-Fixable | Effort |
|----------|------------|-------|--------------|--------|
| P0 | Schema compliance errors | 26 files | Partial | 2-3 hours |
| P1 | Delegation/placeholder | 4 files | Manual | 30 min |
| P2 | Missing tags | 610 files | **Yes** | 5 min |
| P3 | Naming convention | 521 files | **Yes** | 5 min |
| P4 | Directive verb | 171 files | Partial | 1 hour |

**Total estimated effort**: 4-5 hours (with automation)

---

## Phase 1: Critical Fixes (P0) - Schema Compliance

### 26 Files Need Manual Attention

These files are missing required sections (`directive`, `scope`) or required fields (`version`, `description`).

#### Group A: Main Agents Missing Multiple Sections (5 files)

| File | Missing |
|------|---------|
| `agents_business_review/business_review_agent_definition.yaml` | directive, scope, version, description |
| `agents_engineering/engineering_agent_definition.yaml` | directive, scope, version, description |
| `agents_product_management/product_agent_definition.yaml` | directive, scope, version, description |
| `agents_project_management/project_agent_definition.yaml` | directive, version, description |
| `agents_research/research_agent_definition.yaml` | directive, scope, version, description |

**Action**: Add missing sections using template:
```yaml
  directive:
    primary_goal: "[Verb] [domain] operations and coordinate subagents."

  scope:
    can_access:
      - /agents/definitions
      - /docs
    can_modify:
      - /agents/outputs
```

#### Group B: Subagents Missing Scope (19 files)

```
agents_content/subagents/content_agent_localization_expert_definition.yaml
agents_content/subagents/content_agent_seo_specialist_definition.yaml
agents_context/subagents/context_agent_chat_summary_definition.yaml
agents_context/subagents/context_agent_information_gatherer_definition.yaml
agents_context/subagents/context_agent_knowledge_synthesizer_definition.yaml
agents_context/subagents/context_agent_llm_memory_specialist_definition.yaml
agents_context/subagents/context_agent_memory_storage_definition.yaml
agents_product_management/subagents/product_agent_business_case_owner_definition.yaml
agents_product_management/subagents/product_agent_dashboard_designer_definition.yaml
agents_product_management/subagents/product_agent_operations_definition.yaml
agents_prompt_architect/subagents/prompt_architect_agent_prompt_generator_definition.yaml
agents_prompt_architect/subagents/prompt_architect_agent_tool_matcher_definition.yaml
agents_public_relations/subagents/public_relations_agent_press_release_writer_definition.yaml
agents_research/subagents/research_agent_report_writer_definition.yaml
agents_ux/subagents/ux_agent_customer_journey_mapper_definition.yaml
agents_ux/subagents/ux_agent_interaction_designer_definition.yaml
agents_ux/subagents/ux_agent_prototype_builder_definition.yaml
agents_ux/subagents/ux_agent_user_persona_developer_definition.yaml
agents_ux/subagents/ux_agent_wireframe_creator_definition.yaml
```

**Action**: Run auto-fix script (see below) or manually add:
```yaml
  scope:
    can_access:
      - /docs
      - /src
```

#### Group C: Delegation Without Targets (2 files)

```
agents_financial/subagents/financial_agent_tech_security_manager_definition.yaml
agents_model_orchestration/model_orchestration_agent_definition.yaml
```

**Action**: Either add `allowed_subagents` list OR set `delegation.enabled: false`

---

## Phase 2: High Priority (P1) - Delegation & Placeholders

### Placeholder Text (2 files)

Files containing "TBD" or similar:
```bash
grep -r "TBD\|TODO\|PLACEHOLDER" agent_definitions/ --include="*.yaml"
```

**Action**: Replace placeholder text with actual content.

---

## Phase 3: Auto-Fixable Issues (P2/P3)

### Tag Consistency (610 files)

**Issues**:
- 381 files: No tags defined
- 229 files: Missing 'subagent' tag
- 213 files: Missing domain tag

**Auto-fix command**:
```bash
python3 fix_agents.py --fix tags --all
```

### Naming Convention (521 files)

**Issue**: `identity.name` doesn't match filename pattern.

**Two strategies**:

**Option A (Recommended)**: Update `identity.name` to match filename
```bash
python3 fix_agents.py --fix names --strategy update-identity --all
```

**Option B**: Rename files to match `identity.name`
```bash
python3 fix_agents.py --fix names --strategy rename-files --all --dry-run
```

---

## Phase 4: Directive Improvements (P4)

### Missing Action Verbs (171 files)

**Common non-verbs found**:
| Word | Count | Replacement |
|------|-------|-------------|
| maximize | 32 | Optimize to maximize |
| automate | 6 | (already verb - add to allowed list) |
| oversee | 6 | (already verb - add to allowed list) |
| determine | 5 | Analyze to determine |
| minimize | 5 | Optimize to minimize |

**Action**: Update validation script to include more verbs, then manually review remaining.

---

## Execution Order

### Step 1: Run Auto-Fix Script (5 minutes)
```bash
# Preview changes
python3 fix_agents.py --all --dry-run

# Apply tag fixes
python3 fix_agents.py --fix tags --all

# Apply naming fixes
python3 fix_agents.py --fix names --all
```

### Step 2: Manual Fixes - Main Agents (1 hour)
Fix the 5 main agent files missing core sections:
1. `business_review_agent_definition.yaml`
2. `engineering_agent_definition.yaml`
3. `product_agent_definition.yaml`
4. `project_agent_definition.yaml`
5. `research_agent_definition.yaml`

### Step 3: Manual Fixes - Subagent Scopes (30 minutes)
Run scope auto-fix or manually add to 19 files:
```bash
python3 fix_agents.py --fix scope --all
```

### Step 4: Delegation Fixes (10 minutes)
Fix 2 files with delegation issues.

### Step 5: Placeholder Cleanup (10 minutes)
Find and replace TBD text in 2 files.

### Step 6: Validate (5 minutes)
```bash
python3 validate_agents.py --all --json --output final_report.json
```

---

## Fix Script Commands

```bash
# Full auto-fix (safe operations only)
python3 fix_agents.py --all

# Preview all changes without applying
python3 fix_agents.py --all --dry-run

# Fix specific domain
python3 fix_agents.py --domain engineering

# Fix specific issue type
python3 fix_agents.py --fix tags --all
python3 fix_agents.py --fix names --all
python3 fix_agents.py --fix scope --all
python3 fix_agents.py --fix version --all

# Generate fix report
python3 fix_agents.py --all --report fixes_applied.json
```

---

## Verification Checklist

After fixes, run validation and confirm:

- [ ] All 762 files valid (0 errors)
- [ ] Average score > 95
- [ ] No schema compliance issues
- [ ] No delegation issues
- [ ] No placeholder text
- [ ] Tags include domain for all files
- [ ] Subagent files have 'subagent' tag
- [ ] All names match filename pattern

---

## Files to Fix (By Domain)

### High Priority (Has Errors)

| Domain | Files with Errors | Primary Issue |
|--------|-------------------|---------------|
| business_review | 1 | Missing directive, scope |
| content | 2 | Missing scope |
| context | 5 | Missing scope |
| engineering | 1 | Missing directive, scope |
| financial | 1 | Delegation without targets |
| model_orchestration | 1 | Delegation without targets |
| product_management | 4 | Missing scope |
| project_management | 1 | Missing directive |
| prompt_architect | 2 | Missing scope |
| public_relations | 1 | Missing scope |
| research | 2 | Missing scope |
| ux | 5 | Missing scope |

### Warnings Only (Lower Priority)

All other 736 files have warnings only (tags, naming, directive format).

---

## Post-Fix Actions

1. **Re-sync to Claude Code**:
   ```bash
   python3 sync_agents_to_claude.py
   ```

2. **Update PROJECT_INDEX.md** with new validation stats

3. **Commit changes**:
   ```bash
   git add agent_definitions/
   git commit -m "fix: resolve agent validation issues (762 files)"
   ```

---

*Fix plan generated from validation report on 2026-01-10*
