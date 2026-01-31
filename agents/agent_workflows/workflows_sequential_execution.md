---
dateCreated: 2025-10-05
documentType: Workflow Template
category: Sequential Execution
version: 1.0
---

# Sequential Execution Workflow Template

Template for orchestrating sequential agent execution with clear handoffs and dependencies.

## Workflow Overview

**Use When**:
- Work streams have dependencies
- Limited RAM (16GB tier)
- Critical path requires sequential steps
- Complex handoffs between agents

**Benefits**:
- Clear dependency management
- Simplified resource management
- Reduced complexity
- Predictable execution flow

## Workflow Phases

### Phase 1: Sequential Planning (20-40 minutes)

**Objective**: Design sequential execution flow with optimized ordering

**Steps**:

1. **Dependency Mapping**
   - Identify all agents and tasks
   - Map dependencies between agents
   - Create dependency graph
   - Determine critical path

2. **Execution Ordering**
   - Order agents based on dependencies
   - Identify opportunities for mini-parallel sections
   - Optimize for minimal total time
   - Plan handoff points

3. **Resource Planning**
   - Calculate RAM requirements per agent
   - Plan model assignments
   - Identify cloud vs local usage
   - Validate sequential feasibility

4. **Handoff Protocol Design**
   - Define handoff criteria per transition
   - Specify deliverable formats
   - Create validation checklists
   - Plan knowledge transfer

**Validation Gate**:
- [ ] Dependency graph complete and valid
- [ ] Execution order optimized
- [ ] Resource plan validated
- [ ] Handoff protocols documented

**Outputs**:
- Dependency graph
- Execution sequence document
- Resource allocation plan
- Handoff protocol specification

---

### Phase 2: First Agent Activation (Minutes to Hours)

**Objective**: Launch and complete first agent in sequence

**Steps**:

1. **Agent Initialization**
   - Load agent definition
   - Validate scope contract
   - Verify model availability
   - Initialize monitoring

2. **Execution**
   - Execute agent workflow
   - Monitor progress and resources
   - Validate quality gates
   - Track deliverable completion

3. **Deliverable Validation**
   - Verify all outputs created
   - Run validation tests
   - Check quality standards
   - Document completion status

4. **Handoff Preparation**
   - Create handoff documentation
   - Package deliverables
   - Document decisions made
   - Prepare context transfer

**Validation Gate**:
- [ ] Agent execution complete
- [ ] All deliverables validated
- [ ] Quality gates passed
- [ ] Handoff documentation ready

**Outputs**:
- Agent deliverables
- Completion report
- Handoff documentation
- Lessons learned notes

---

### Phase 3: Sequential Agent Execution (Iterative)

**Objective**: Execute remaining agents in sequence with proper handoffs

**Steps** (Repeat for each agent):

1. **Handoff Acceptance**
   - Receive previous agent deliverables
   - Validate handoff completeness
   - Review context documentation
   - Confirm ready to proceed

2. **Agent Execution**
   - Execute agent workflow phases
   - Build on previous agent outputs
   - Monitor progress continuously
   - Validate intermediate checkpoints

3. **Integration with Previous Work**
   - Integrate with prior deliverables
   - Validate consistency
   - Resolve any conflicts
   - Maintain unified context

4. **Next Handoff Preparation**
   - Create updated handoff documentation
   - Package all relevant artifacts
   - Document cumulative progress
   - Prepare for next agent

**Validation Gate** (Per Agent):
- [ ] Handoff received and validated
- [ ] Agent execution complete
- [ ] Integration successful
- [ ] Next handoff prepared

**Outputs** (Per Agent):
- Agent-specific deliverables
- Updated handoff documentation
- Integration validation report
- Cumulative progress report

---

### Phase 4: Final Integration (1-2 hours)

**Objective**: Integrate all sequential outputs into final deliverables

**Steps**:

1. **Artifact Assembly**
   - Collect all agent outputs
   - Organize by deliverable type
   - Verify completeness
   - Check for missing pieces

2. **Cross-Agent Validation**
   - Validate consistency across agents
   - Check for contradictions
   - Verify dependency satisfaction
   - Test integrated functionality

3. **Final Quality Review**
   - Review against success metrics
   - Validate scope compliance
   - Check documentation completeness
   - Verify standards adherence

4. **Documentation Finalization**
   - Create final integration report
   - Document sequential flow
   - Capture lessons learned
   - Update workflow template

**Validation Gate**:
- [ ] All artifacts assembled
- [ ] Cross-agent validation passed
- [ ] Quality review complete
- [ ] Final documentation ready

**Outputs**:
- Integrated final deliverables
- Integration validation report
- Sequential execution report
- Lessons learned document

---

## Resource Management Guidelines

### RAM Optimization

**16GB Tier Strategy**:
- One agent at a time
- Cloud models for large agents (>16GB)
- Local models for smaller agents (<8GB)
- Sequential-only execution

**Resource Allocation**:
- Monitor RAM before each agent activation
- Ensure previous agent fully released resources
- Use cloud fallback if RAM insufficient
- Track resource usage patterns

### Model Selection Strategy

**Per-Agent Basis**:
- Evaluate agent requirements
- Check local model availability
- Consider cloud cost vs time
- Balance quality and resources

**Optimization**:
- Use smallest capable model
- Prefer local models when possible
- Cloud models for critical agents
- Document model rationale

---

## Handoff Protocol

### Standard Handoff Format

```yaml
handoff_id: [Unique identifier]
from_agent: [Previous agent name]
to_agent: [Next agent name]
date: YYYY-MM-DD
status: [ready | pending | blocked]

deliverables:
  - artifact: [File path or deliverable description]
    format: [File format or type]
    validation: [Validation status]
    location: [Exact path]

context:
  decisions_made:
    - decision: [Description]
      rationale: [Why this decision]

  open_issues:
    - issue: [Description]
      severity: [critical | high | medium | low]
      recommendation: [Suggested approach]

  lessons_learned:
    - lesson: [What was learned]
      application: [How to apply]

validation:
  checklist:
    - [ ] All deliverables present
    - [ ] Quality gates passed
    - [ ] Documentation complete
    - [ ] Context fully transferred

  sign_off:
    from_agent_validation: [passed | failed]
    to_agent_acceptance: [accepted | rejected | pending]
```

### Handoff Validation Checklist

**Deliverables**:
- [ ] All expected artifacts present
- [ ] Files in correct locations
- [ ] Proper file formats
- [ ] No corrupted files
- [ ] Validation tests passed

**Documentation**:
- [ ] Handoff document complete
- [ ] Decisions documented
- [ ] Open issues listed
- [ ] Context explained

**Quality**:
- [ ] Quality gates passed
- [ ] Standards compliant
- [ ] No critical issues
- [ ] Ready for next agent

---

## Execution Timeline Estimation

### Sequential Time Calculation

**Formula**:
```
Total Time = Sum(Agent Execution Times) + Sum(Handoff Times) + Buffer
```

**Example Calculation**:
- Agent 1: 8 hours
- Handoff 1→2: 30 minutes
- Agent 2: 12 hours
- Handoff 2→3: 30 minutes
- Agent 3: 6 hours
- Buffer (15%): 3.98 hours
- **Total**: ~31 hours (4 business days)

### Optimization Opportunities

**Mini-Parallel Sections**:
- Identify independent sub-tasks within agents
- Execute sub-agents in parallel when possible
- Reduce sequential bottlenecks
- Example: Documentation sub-agents can parallel within sequential main flow

**Overlapping Handoffs**:
- Prepare next agent during current agent execution
- Pre-validate handoff criteria
- Start context transfer early
- Reduce handoff transition time

---

## Success Metrics

### Execution Efficiency
- **Target**: Minimal idle time between agents
- **Measurement**: Handoff transition time
- **Threshold**: <5% total time in transitions

### Handoff Quality
- **Target**: Zero failed handoffs
- **Measurement**: Handoff acceptance rate
- **Threshold**: 100% acceptance on first attempt

### Resource Utilization
- **Target**: Optimal model usage
- **Measurement**: Local vs cloud model ratio
- **Threshold**: >70% local model usage (16GB tier)

### Quality Maintenance
- **Target**: No quality degradation
- **Measurement**: Quality gate pass rates
- **Threshold**: 100% pass rate

---

## Common Pitfalls and Mitigations

### Pitfall 1: Long Handoff Delays
**Symptoms**: Extended idle time between agents, slow progress
**Mitigation**: Prepare handoffs early, validate incrementally, parallelize preparation

### Pitfall 2: Incomplete Handoffs
**Symptoms**: Missing deliverables, context loss, rework required
**Mitigation**: Strict handoff checklist, validation protocol, acceptance criteria

### Pitfall 3: Dependency Deadlocks
**Symptoms**: Circular dependencies, blocked execution
**Mitigation**: Thorough dependency mapping, validate DAG, break cycles early

### Pitfall 4: Resource Mismanagement
**Symptoms**: RAM exhaustion, model unavailability, execution failures
**Mitigation**: Pre-validate resources, cloud fallback ready, monitor continuously

---

## Example: Phase 1 Sequential Execution

**Scenario**: 3 agents on 16GB RAM system

**Sequence**:

1. **Architecture Discovery Agent**
   - Duration: 45 minutes
   - RAM: 2.1GB (Gemini 2.5 Flash overhead)
   - Deliverables: Dependency map, architecture report
   - Handoff to: Model Orchestrator Tool Agent

2. **Model Orchestrator Tool Agent**
   - Duration: 2 days
   - RAM: 20GB peak (use CodeLlama 34B on cloud)
   - Deliverables: Consolidated code, tests
   - Handoff to: Documentation Agent

3. **Documentation Agent**
   - Duration: 1.5 days
   - RAM: 10.376GB (local models)
   - Deliverables: User guides, API docs
   - Final integration

**Total Time**: 4 days
**Handoff Count**: 2
**Cloud Usage**: 1 agent (Model Orchestrator)

---

**Template Version**: 1.0
**Created**: 2025-10-05
**Last Updated**: 2025-10-05
**Template Type**: Sequential Execution
