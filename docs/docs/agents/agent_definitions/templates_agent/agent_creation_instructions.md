---
dateCreated: 2025-10-05
documentType: Catalog
category: Agent Library
status: Active
---

# Agent Template Catalog

Comprehensive catalog of all available agent templates for creating new agents quickly and consistently.

## Base Templates

### Base Agent Template

**Location**: `gitignore/Agent Library/templates/base-templates/base-agent-template.md`
**Purpose**: Foundation template for all agents
**Use When**: Creating any new agent from scratch
**Customization Required**: All sections (this is a blank template)

**Sections**:
- Agent Identity (name, role, type, tier)
- Core Responsibilities (4-5 key areas)
- Scope Contract (permitted/forbidden directories, files, operations)
- Scope Boundaries (can access, cannot access, handoff requirements)
- Model Preferences (primary, fallback, concurrent compatibility)
- Output Specifications (format, location, validation criteria)
- Sub-Agents (if applicable)
- Operational Workflow (phase-by-phase procedures)
- Success Metrics (measurable outcomes)

## Domain Specialist Templates

### Analysis Agent Template

**Location**: `gitignore/Agent Library/templates/analysis-agent-template.md`
**Purpose**: Template for agents that discover, analyze, and map project structure
**Use When**: Creating agents for file discovery, dependency analysis, code analysis
**Version**: 1.0
**Created**: 2025-10-05

**Pre-configured For**:
- Read-only access to all project files
- Analysis and discovery operations
- Architecture and diagram output
- Report generation
- Sub-agent spawning for parallel analysis
- Evidence-based findings
- Systematic investigation workflow

**Example Agents Using This Template**:
- Architecture Discovery Agent
- Code Quality Analyzer
- Performance Profiler
- Security Auditor

**Key Features**:
- 5-phase analysis workflow (Preparation → Discovery → Deep Analysis → Synthesis → Reporting)
- Evidence collection framework
- Hypothesis validation structure
- Metrics and measurement templates

### Implementation Agent Template

**Location**: `gitignore/Agent Library/templates/implementation-agent-template.md`
**Purpose**: Template for agents that create or modify code
**Use When**: Creating agents for code development, API integration, feature implementation
**Version**: 1.0
**Created**: 2025-10-05

**Pre-configured For**:
- Read/write access to specific directories
- Code modification operations
- Testing and validation (≥80% coverage requirement)
- Sub-agent spawning for specialized tasks
- Implementation notes generation
- Quality gates and validation

**Example Agents Using This Template**:
- Model Orchestrator Tool Agent
- API Integration Specialist
- Feature Developer
- Bug Fix Specialist

**Key Features**:
- 5-phase implementation workflow (Planning → Implementation → Testing → Refinement → Handoff)
- Test coverage requirements built-in
- Code quality validation checklist
- Handoff protocol for documentation

### Documentation Agent Template

**Location**: `gitignore/Agent Library/templates/documentation-agent-template.md`
**Purpose**: Template for agents that create or update documentation
**Use When**: Creating agents for user guides, API docs, technical writing
**Version**: 1.0
**Created**: 2025-10-05

**Pre-configured For**:
- Read access to all code for understanding
- Write access to documentation directories (ONLY)
- Markdown and text file operations
- Style guide adherence
- Example generation and validation
- Audience-appropriate content

**Example Agents Using This Template**:
- Documentation & Knowledge Agent
- Technical Writer Sub-Agent
- User Guide Specialist Sub-Agent
- API Documentation Writer

**Key Features**:
- 5-phase documentation workflow (Planning → Drafting → Enhancement → Review → Publication)
- Audience analysis framework
- Example validation requirements
- Style guide customization section
- Active voice and clarity standards

### Testing Agent Template

**Location**: `gitignore/Agent Library/templates/testing-agent-template.md`
**Purpose**: Template for agents that create and maintain test suites
**Use When**: Creating agents for unit testing, integration testing, E2E testing, performance testing
**Version**: 1.0
**Created**: 2025-10-05

**Pre-configured For**:
- Read access to source code (for understanding)
- Write access to test directories
- Test execution permissions
- Coverage analysis tools
- Test framework integration
- Mock and fixture generation

**Example Agents Using This Template**:
- Unit Test Generator
- Integration Test Specialist
- E2E Test Designer
- Performance Test Engineer

**Key Features**:
- 5-phase testing workflow (Analysis → Design → Implementation → Execution → Maintenance)
- Coverage targets (≥80% unit, ≥70% integration)
- AAA pattern (Arrange-Act-Assert) enforcement
- Flaky test prevention strategies
- Test optimization guidance

## Sub-Agent Templates

### Sub-Agent Base Template

**Location**: `gitignore/Agent Library/templates/sub-agent-templates/sub-agent-base-template.md`
**Purpose**: Foundation template for all sub-agents
**Use When**: Creating any new sub-agent

**Pre-configured For**:
- Parent agent reference
- Activation condition specification
- Specialized scope (narrower than primary agents)
- Coordination protocol with parent
- Performance metrics specific to sub-agents

**Key Differences from Base Template**:
- Includes parent agent reference
- Activation conditions section
- Simplified scope (inherits from parent)
- Coordination protocol with parent agent
- Focused on specific specialized tasks

## Template Selection Guide

### Decision Tree

**Question 1**: Is this a primary agent or sub-agent?
- **Primary Agent** → Continue to Question 2
- **Sub-Agent** → Use Sub-Agent Base Template

**Question 2**: What is the agent's primary function?
- **Meta-coordination/Orchestration** → Use Coordination Agent Template
- **Analysis/Discovery** → Use Analysis Agent Template
- **Code Implementation** → Use Implementation Agent Template
- **Documentation Creation** → Use Documentation Agent Template
- **Other/Hybrid** → Use Base Agent Template

**Question 3**: Does the agent need sub-agents?
- **Yes** → Add Sub-Agents section using Sub-Agent Base Template
- **No** → Remove Sub-Agents section

## Template Customization Checklist

When creating a new agent from a template:

- [ ] Update front matter (dateCreated, agentType, tier, status)
- [ ] Replace [Agent Name] with actual agent name throughout
- [ ] Define 4-5 Core Responsibilities specific to agent's role
- [ ] Specify Permitted Directories (exact paths)
- [ ] Specify Permitted File Types (with read/write permissions)
- [ ] List Forbidden Operations explicitly
- [ ] Define clear Scope Boundaries (can/cannot access)
- [ ] Specify handoff requirements (must handoff to which agents)
- [ ] Select Primary Model with justification
- [ ] Select Fallback Model with activation conditions
- [ ] Define Output Specifications (format, location, validation)
- [ ] Create Operational Workflow (phase-by-phase)
- [ ] Define Success Metrics (measurable outcomes)
- [ ] Add Sub-Agents section if applicable
- [ ] Validate no scope overlaps with existing agents
- [ ] Validate model selection fits concurrent execution plan

## Template Best Practices

### Naming Conventions

- **Primary Agents**: `[Domain]-Agent.md` (example: `Architecture-Discovery-Agent.md`)
- **Sub-Agents**: `[Parent]-Agent-[Specialization].md` (example: `Architecture-Discovery-Agent-File-Cataloguer.md`)

### Scope Definition

- Be explicit about permitted vs forbidden operations
- Define scope at directory, file type, and operation level
- Specify clear handoff conditions to other agents
- Avoid scope overlaps with existing agents

### Model Selection

- Choose models based on task requirements (code, analysis, writing)
- Consider RAM requirements for concurrent execution
- Justify model selection with specific reasoning
- Provide fallback model for resilience

### Workflow Design

- Break workflow into 4-5 clear phases
- Each phase should have 4-5 steps
- Include validation/decision points
- Specify handoff points to other agents

## Template Maintenance

### Version Control

- All templates versioned with template_version field
- Changes documented in Agent History/changelog.md
- Breaking changes require new major version
- Backward compatibility maintained when possible

### Template Updates

- Review templates quarterly for improvements
- Incorporate learnings from active agents
- Update based on framework evolution
- Add new templates as patterns emerge

---

**Catalog Status**: Active
**Created**: 2025-10-05
**Last Updated**: 2025-10-05
**Version**: 1.1
**Total Templates**: 5 (1 base + 4 domain specialists: Analysis, Implementation, Documentation, Testing)
