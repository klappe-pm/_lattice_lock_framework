---
dateCreated: 2025-10-05
documentType: Workflow Template
category: Hybrid Execution
version: 1.0
---

# Hybrid Workflow Template

Template combining sequential and parallel execution for optimal resource utilization and time efficiency.

## Workflow Overview

**Use When**:
- Mixed dependencies (some parallel, some sequential)
- Medium RAM availability (32GB tier)
- Time optimization critical
- Complex multi-phase projects

**Benefits**:
- Balance of speed and resource efficiency
- Flexibility to adapt to constraints
- 30-50% time savings vs full sequential
- Manageable resource usage

## Execution Strategy

### Phase-Based Parallelization

**Strategy**: Execute phases sequentially, parallelize within phases where possible

**Example Structure**:
```
Phase 1: Discovery (Sequential) - Baseline required
  └─> Single agent execution

Phase 2: Implementation (Parallel) - Independent tracks
  ├─> Track A: Code (parallel sub-agents)
  ├─> Track B: Tests (parallel sub-agents)
  └─> Track C: Docs (parallel sub-agents)

Phase 3: Integration (Sequential) - Dependent on Phase 2
  └─> Single integration agent
```

### Agent-Level Parallelization

**Strategy**: Execute agents sequentially, parallelize sub-agents within each agent

**Example Structure**:
```
Agent 1: Architecture Discovery (Sequential)
  ├─> Sub-Agent A: File Cataloguer (parallel)
  ├─> Sub-Agent B: Dependency Mapper (parallel)
  └─> Sub-Agent C: Structure Analyzer (parallel)

Agent 2: Model Orchestrator Tool (Sequential, follows Agent 1)
  ├─> Sub-Agent A: Code Analyst (parallel)
  ├─> Sub-Agent B: API Specialist (parallel)
  └─> Sub-Agent C: Testing Specialist (parallel)
```

## Workflow Phases

### Phase 1: Hybrid Planning (30-60 minutes)

**Objective**: Design optimal hybrid execution strategy

**Steps**:

1. **Dependency Analysis**
   - Map all agent dependencies
   - Identify parallelizable sections
   - Determine sequential requirements
   - Create hybrid execution graph

2. **Resource-Aware Optimization**
   - Calculate RAM requirements per phase
   - Identify parallel opportunities within RAM limits
   - Plan sequential fallbacks
   - Optimize for time within constraints

3. **Phase Definition**
   - Group agents into phases
   - Define phase boundaries
   - Specify parallel sections
   - Document sequential requirements

4. **Execution Strategy Documentation**
   - Create detailed execution plan
   - Document resource allocation
   - Define transition protocols
   - Plan monitoring approach

**Validation Gate**:
- [ ] Hybrid execution graph complete
- [ ] Resource allocation validated
- [ ] Phase transitions defined
- [ ] Strategy documented

**Outputs**:
- Hybrid execution graph
- Phase definition document
- Resource allocation plan
- Execution strategy specification

---

### Phase 2: Sequential Phase Execution (Iterative)

**Objective**: Execute each phase with internal parallelization

**Steps** (Per Phase):

1. **Phase Initialization**
   - Validate previous phase completion
   - Verify resource availability
   - Load phase-specific agents
   - Initialize phase monitoring

2. **Internal Parallel Execution**
   - Launch all parallel agents/sub-agents within phase
   - Monitor resource usage
   - Track individual progress
   - Manage dynamic allocation

3. **Phase Completion Validation**
   - Verify all phase deliverables
   - Validate quality gates
   - Check cross-agent consistency
   - Document phase completion

4. **Inter-Phase Handoff**
   - Create phase transition documentation
   - Package phase outputs
   - Prepare for next phase
   - Release phase resources

**Validation Gate** (Per Phase):
- [ ] All phase agents completed
- [ ] Internal consistency validated
- [ ] Quality gates passed
- [ ] Handoff documentation ready

**Outputs** (Per Phase):
- Phase deliverables
- Phase completion report
- Inter-phase handoff documentation
- Resource utilization metrics

---

### Phase 3: Dynamic Resource Management (Continuous)

**Objective**: Optimize resource usage throughout hybrid execution

**Steps**:

1. **Continuous Monitoring**
   - Track RAM usage per agent
   - Monitor phase progress
   - Detect resource pressure
   - Alert on threshold breaches

2. **Dynamic Optimization**
   - Adjust parallelism based on RAM
   - Swap models (local ↔ cloud)
   - Reduce concurrency if needed
   - Maintain system stability

3. **Adaptive Scheduling**
   - Reorder agents within phase if beneficial
   - Adjust phase boundaries if needed
   - Optimize for current state
   - Minimize idle time

4. **Performance Tracking**
   - Measure actual vs planned time
   - Track resource efficiency
   - Document optimization decisions
   - Calculate time savings

**Validation Gate** (Continuous):
- [ ] Resources within safe limits
- [ ] No critical bottlenecks
- [ ] Optimization decisions logged
- [ ] Performance targets on track

**Outputs**:
- Real-time monitoring dashboard
- Resource optimization log
- Performance metrics
- Adaptive decisions documentation

---

### Phase 4: Final Integration (1-2 hours)

**Objective**: Integrate all phase outputs and validate complete system

**Steps**:

1. **Cross-Phase Integration**
   - Collect all phase deliverables
   - Validate phase boundaries
   - Resolve cross-phase issues
   - Create unified outputs

2. **End-to-End Validation**
   - Test complete workflows
   - Validate all dependencies satisfied
   - Check quality standards
   - Verify success metrics

3. **Performance Analysis**
   - Calculate total execution time
   - Measure time savings vs sequential
   - Analyze resource efficiency
   - Document hybrid effectiveness

4. **Retrospective**
   - Review hybrid execution
   - Identify optimization opportunities
   - Document lessons learned
   - Update hybrid template

**Validation Gate**:
- [ ] All phases integrated
- [ ] End-to-end validation passed
- [ ] Performance targets met
- [ ] Documentation complete

**Outputs**:
- Integrated final deliverables
- Performance analysis report
- Hybrid execution retrospective
- Template improvements log

---

## RAM Tier Strategies

### 32GB Tier (Optimal for Hybrid)

**Recommended Approach**:
- 2-3 concurrent agents within phases
- Mix of local (7B-32B) and cloud models
- Phase-level parallelization
- Agent-level selective parallelization

**Example Configuration**:
```yaml
Phase 1: Discovery (Sequential baseline)
  agent: Architecture Discovery (single)
  ram: 2.1GB
  parallel_sub_agents: 3
  total_ram: ~14GB

Phase 2: Implementation (Parallel tracks)
  Track A: Code Implementation
    ram: ~12GB (2 sub-agents parallel)
  Track B: Documentation
    ram: ~10GB (2 sub-agents parallel)
  total_concurrent_ram: ~22GB

Phase 3: Integration (Sequential finalization)
  agent: Integration (single)
  ram: ~5GB
```

### 16GB Tier (Limited Hybrid)

**Recommended Approach**:
- Sequential phases
- Parallel sub-agents only (2-3 concurrent)
- Cloud models for heavy agents
- Conservative parallelization

**Example Configuration**:
```yaml
Phase 1: Discovery (Sequential)
  agent: Architecture Discovery (single)
  parallel_sub_agents: 2 (lighter models)
  total_ram: ~8GB

Phase 2: Implementation (Sequential agents)
  Agent A: Code (cloud model)
    parallel_sub_agents: 0
  Agent B: Tests (local model)
    parallel_sub_agents: 2
    total_ram: ~12GB
```

### 64GB+ Tier (Maximum Hybrid)

**Recommended Approach**:
- Full parallel phases when possible
- Mix of hybrid and full parallel
- Maximum local model usage
- Aggressive parallelization

**Example Configuration**:
```yaml
Phase 1: Discovery (Parallel)
  agents: 2 concurrent discovery agents
  parallel_sub_agents: 3 per agent
  total_ram: ~28GB

Phase 2: Implementation (Full parallel)
  Track A, B, C: All concurrent
  total_ram: ~60GB

Phase 3: Integration (Parallel validation)
  agents: 2 validation agents
  total_ram: ~20GB
```

---

## Adaptive Strategies

### Strategy 1: Phase-Level Adaptive

**When**: RAM varies significantly across phases

**Approach**:
- Assess RAM availability before each phase
- Adjust parallelism per phase
- Optimize phase boundaries
- Maximum flexibility

**Example**:
```
Phase 1: 40% RAM → Full parallel (3 agents)
Phase 2: 80% RAM → Partial parallel (2 agents)
Phase 3: 95% RAM → Sequential only (1 agent)
```

### Strategy 2: Agent-Level Adaptive

**When**: Individual agents have variable sub-agent RAM needs

**Approach**:
- Assess RAM before each agent
- Adjust sub-agent parallelism
- Sequential fallback if needed
- Per-agent optimization

**Example**:
```
Agent A: 30% RAM → Parallel sub-agents (4 concurrent)
Agent B: 70% RAM → Limited parallel (2 concurrent)
Agent C: 90% RAM → Sequential sub-agents (1 at a time)
```

### Strategy 3: Dynamic Adaptive

**When**: RAM usage unpredictable or fluctuating

**Approach**:
- Continuous monitoring
- Real-time parallelism adjustment
- Dynamic model swapping
- Aggressive optimization

**Example**:
```
Monitor every 5 minutes:
- If RAM < 70%: Increase parallelism
- If RAM 70-85%: Maintain current
- If RAM > 85%: Reduce parallelism
- If RAM > 95%: Emergency sequential
```

---

## Success Metrics

### Time Efficiency
- **Target**: 30-50% time savings vs full sequential
- **Measurement**: Total elapsed time comparison
- **Calculation**: (Sequential Time - Hybrid Time) / Sequential Time

### Resource Efficiency
- **Target**: 60-80% average RAM usage
- **Measurement**: Average RAM across all phases
- **Threshold**: <50% = underutilized, >85% = overstressed

### Hybrid Effectiveness
- **Target**: >80% parallelization opportunities realized
- **Measurement**: Actual parallel time / Potential parallel time
- **Threshold**: <70% = suboptimal hybrid execution

### Quality Maintenance
- **Target**: No quality degradation
- **Measurement**: Quality gate pass rates
- **Threshold**: 100% pass rate

---

## Common Hybrid Patterns

### Pattern 1: Sequential-Parallel-Sequential (SPS)

**Structure**:
```
Phase 1: Sequential setup
  → Single baseline agent

Phase 2: Parallel execution
  → Multiple independent agents

Phase 3: Sequential integration
  → Single integration agent
```

**Use When**: Clear baseline required, independent work possible, integration critical

### Pattern 2: Parallel-Sequential-Parallel (PSP)

**Structure**:
```
Phase 1: Parallel discovery
  → Multiple discovery agents

Phase 2: Sequential consolidation
  → Single consolidation agent

Phase 3: Parallel implementation
  → Multiple implementation agents
```

**Use When**: Parallel discovery possible, central coordination needed, parallel implementation

### Pattern 3: Nested Hybrid (Phase + Agent Hybrid)

**Structure**:
```
Phase 1: Sequential
  Agent A (parallel sub-agents)

Phase 2: Parallel
  Agent B (parallel sub-agents)
  Agent C (sequential sub-agents)

Phase 3: Sequential
  Agent D (parallel sub-agents)
```

**Use When**: Maximum optimization needed, resources allow, complex execution flow

---

**Template Version**: 1.0
**Created**: 2025-10-05
**Last Updated**: 2025-10-05
**Template Type**: Hybrid Execution
