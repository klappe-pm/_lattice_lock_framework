---
dateCreated: 2025-10-05
documentType: Documentation
category: Workflow Templates
version: 1.0
---

# Workflow Templates Documentation

Comprehensive collection of execution workflow templates for multi-agent orchestration.

## Overview

This directory contains proven workflow templates for orchestrating agent execution across different execution strategies: parallel, sequential, and hybrid approaches.

**Templates Available**:
1. Parallel Execution Workflow
2. Sequential Execution Workflow
3. Hybrid Workflow

## Quick Selection Guide

### When to Use Each Template

**Parallel Execution** (`parallel-execution-workflow.md`):
- ✅ Independent work streams with no dependencies
- ✅ 32GB+ RAM available
- ✅ Time optimization is critical priority
- ✅ Multiple tracks can execute simultaneously
- **Expected Benefit**: 30-70% time savings vs sequential

**Sequential Execution** (`sequential-execution-workflow.md`):
- ✅ Work streams have dependencies
- ✅ 16GB RAM (limited resources)
- ✅ Simple, predictable execution flow preferred
- ✅ Complex handoffs between agents required
- **Expected Benefit**: Simplified complexity, clear dependencies

**Hybrid Workflow** (`hybrid-workflow.md`):
- ✅ Mixed dependencies (some parallel, some sequential)
- ✅ 32GB RAM (medium resources)
- ✅ Balance of speed and resource efficiency
- ✅ Complex multi-phase projects
- **Expected Benefit**: 30-50% time savings, flexible execution

## Template Comparison

| Feature | Parallel | Sequential | Hybrid |
|---------|----------|------------|--------|
| RAM Requirement | 32GB+ | 16GB+ | 32GB+ |
| Complexity | High | Low | Medium |
| Time Savings | 30-70% | Baseline | 30-50% |
| Dependencies | None | Any | Mixed |
| Resource Management | Complex | Simple | Moderate |
| Coordination Overhead | High | Low | Medium |

## RAM Tier Recommendations

### 16GB RAM Tier
**Recommended**: Sequential Execution
- Limited to 1-2 concurrent agents
- Cloud models for heavy workloads
- Simple coordination
- Example: 4-5 days for complete Phase 2

### 32GB RAM Tier
**Recommended**: Hybrid Workflow
- 2-3 concurrent agents possible
- Mix local and cloud models
- Flexible parallelization
- Example: 3-3.5 days for complete Phase 2 (30% savings)

### 64GB+ RAM Tier
**Recommended**: Parallel Execution
- Full parallel execution (3+ tracks)
- Primarily local models (70B capable)
- Maximum time optimization
- Example: 2.5-3 days for complete Phase 2 (50%+ savings)

## Workflow Template Structure

Each template follows a consistent structure:

### Standard Sections

1. **Workflow Overview**
   - Use cases and when to apply
   - Benefits and trade-offs
   - Expected outcomes

2. **Workflow Phases**
   - Detailed phase-by-phase execution
   - Steps within each phase
   - Validation gates
   - Expected outputs

3. **Resource Management**
   - RAM allocation strategies
   - Model selection guidance
   - Dynamic optimization approaches

4. **Coordination Protocols**
   - Status reporting formats
   - Handoff procedures
   - Conflict resolution processes

5. **Success Metrics**
   - Quantitative measurements
   - Quality thresholds
   - Performance targets

6. **Common Pitfalls**
   - Known issues and symptoms
   - Mitigation strategies
   - Prevention approaches

## Using the Templates

### Step 1: Select Template

Evaluate your project requirements:
- Available RAM
- Work stream dependencies
- Time constraints
- Resource availability
- Coordination complexity

Select the most appropriate template based on the Quick Selection Guide above.

### Step 2: Customize Template

Adapt template to your specific project:
- Define specific agents for your project
- Calculate exact RAM requirements
- Specify model assignments
- Document handoff points
- Set project-specific validation gates

### Step 3: Execute Workflow

Follow the template phases:
- Initialize according to Phase 1
- Execute phases sequentially (following template)
- Monitor progress continuously
- Validate at each gate
- Adjust strategy as needed

### Step 4: Document and Iterate

Capture learnings:
- Document execution results
- Note deviations from template
- Record optimization decisions
- Update template based on learnings
- Share improvements with team

## Integration with Agent System

### Agent Template Compatibility

All workflow templates are designed to work with:
- Analysis Agent Template
- Implementation Agent Template
- Documentation Agent Template
- Testing Agent Template
- Base Agent Template
- Sub-Agent Templates

### Validation Framework Integration

Workflow templates integrate with the Agent Validation Framework:
- Scope contract validation
- Model assignment verification
- Resource allocation checks
- Quality gate enforcement
- Performance monitoring

## Advanced Patterns

### Nested Hybrid Execution

Combine workflow templates at different levels:
- **Phase Level**: Hybrid workflow for phase orchestration
- **Agent Level**: Parallel execution within agents (sub-agents)
- **Result**: Maximum optimization with managed complexity

**Example**:
```
Phase 1: Sequential (from Hybrid template)
  └─> Agent A: Parallel sub-agents (from Parallel template)

Phase 2: Parallel (from Hybrid template)
  ├─> Agent B: Sequential sub-agents (from Sequential template)
  └─> Agent C: Parallel sub-agents (from Parallel template)

Phase 3: Sequential (from Hybrid template)
  └─> Agent D: Parallel sub-agents (from Parallel template)
```

### Dynamic Template Switching

Adapt workflow strategy mid-execution:
- Start with Parallel template
- Switch to Sequential if RAM pressure detected
- Resume Parallel when resources available
- Document strategy changes

**Use When**: Resource availability unpredictable or fluctuating

## Performance Monitoring

### Key Metrics to Track

**Time Efficiency**:
- Total execution time
- Time savings vs baseline
- Phase completion times
- Handoff transition times

**Resource Utilization**:
- Average RAM usage
- Peak RAM usage
- Model usage (local vs cloud)
- Resource efficiency ratio

**Quality Metrics**:
- Validation gate pass rates
- Rework requirements
- Error rates
- Test coverage achieved

**Coordination Metrics**:
- Handoff success rates
- Conflict resolution time
- Status reporting compliance
- Integration success rates

### Dashboard Integration

All templates integrate with the Performance Monitoring Dashboard:
- Real-time agent status tracking
- Resource utilization visualization
- Progress monitoring
- Alert management

Access dashboard: `gitignore/Agent Context/performance-dashboard.html`

## Best Practices

### Planning Phase
1. Conduct thorough dependency analysis
2. Calculate realistic resource requirements
3. Define clear validation gates
4. Document handoff protocols upfront

### Execution Phase
1. Monitor resources continuously
2. Validate at every gate
3. Document decisions immediately
4. Adjust strategy based on data

### Completion Phase
1. Conduct retrospective analysis
2. Document lessons learned
3. Update templates based on experience
4. Share improvements with team

### Emergency Protocols

**RAM Exhaustion**:
1. Pause lowest priority agents
2. Swap models to cloud
3. Reduce parallelism
4. Resume when resources available

**Quality Gate Failures**:
1. Pause affected agents
2. Root cause analysis
3. Fix issues before proceeding
4. Re-validate before continuing

**Schedule Pressure**:
1. Re-evaluate parallelization opportunities
2. Consider cloud model acceleration
3. Prioritize critical path
4. Document trade-offs made

## Template Maintenance

### Version Control

All templates are versioned:
- **Major version** (x.0): Breaking changes, incompatible updates
- **Minor version** (1.x): New features, backward compatible
- **Patch version** (1.1.x): Bug fixes, clarifications

Current versions:
- Parallel Execution: 1.0
- Sequential Execution: 1.0
- Hybrid Workflow: 1.0

### Update Process

1. **Identify Improvement**: Document template limitations or enhancement opportunities
2. **Design Update**: Create updated template version
3. **Validation**: Test with sample project
4. **Documentation**: Update README and changelog
5. **Release**: Increment version, notify team

### Feedback Loop

Contribute improvements:
- Document execution results
- Note template deviations
- Suggest enhancements
- Share optimization discoveries

Location for feedback: `gitignore/Agent History/workflow-feedback.md`

## Examples

### Example 1: Phase 2 Parallel Execution (64GB RAM)

**Project**: Multi-Agent System Phase 2
**Template**: Parallel Execution
**RAM**: 64GB available
**Duration**: 2.5-3 days

**Configuration**:
```yaml
Track A: Model Orchestrator Tool Agent
  ram: 11.976GB
  agents: 3 sub-agents parallel
  model: CodeLlama 34B

Track B: Framework Development Agent
  ram: 23.9GB
  agents: 2 sub-agents parallel
  model: Qwen 2.5 32B

Track C: Documentation Agent
  ram: 10.376GB
  agents: 3 sub-agents parallel
  model: Claude Sonnet 4.5

Execution: Track A + C concurrent (22GB), then Track B (24GB)
Result: 2.5 days (vs 6.5 days sequential = 62% time savings)
```

### Example 2: Phase 1 Sequential Discovery (16GB RAM)

**Project**: Multi-Agent System Phase 1
**Template**: Sequential Execution
**RAM**: 16GB available
**Duration**: 1.5 hours

**Configuration**:
```yaml
Agent 1: Model Orchestrator Integration
  ram: 2GB
  duration: 15 min
  model: O3 Mini (cloud)

Agent 2: Architecture Discovery
  ram: 14GB (peak with parallel sub-agents)
  duration: 45 min
  model: Gemini 2.5 Flash

Total: 1 hour (sequential) vs potential 45 min (parallel, but RAM constrained)
```

### Example 3: Phase 2 Hybrid Execution (32GB RAM)

**Project**: Multi-Agent System Phase 2
**Template**: Hybrid Workflow
**RAM**: 32GB available
**Duration**: 3-3.5 days

**Configuration**:
```yaml
Phase 1: Sequential Setup
  agent: Architecture Discovery (complete)

Phase 2: Partial Parallel Execution
  Track A + C: Concurrent (22GB)
    - Model Orchestrator Tool Agent
    - Documentation Agent
  Duration: 2.5 days

Phase 3: Sequential High-RAM Work
  Track B: Framework Development (24GB)
  Duration: 1 day

Total: 3.5 days (vs 6.5 sequential = 46% time savings)
```

## Troubleshooting

### Common Issues

**Issue**: RAM exhaustion during parallel execution
**Solution**: Switch to Hybrid template, reduce concurrency, use cloud models

**Issue**: Long handoff delays in sequential execution
**Solution**: Parallelize handoff preparation, validate incrementally

**Issue**: Quality degradation with parallel execution
**Solution**: Strengthen validation gates, reduce parallelism for critical work

**Issue**: Poor time savings with hybrid execution
**Solution**: Re-analyze dependencies, optimize phase boundaries, increase parallelism

## Resources

### Related Documentation
- Agent Template Catalog: `gitignore/Agent Library/catalog.md`
- Agent Validation Framework: `gitignore/Agent Library/validation-framework.py`
- Performance Dashboard: `gitignore/Agent Context/performance-dashboard.html`
- Phase Execution Plans: `gitignore/Plans/Project-Execution-Plan-Phase-*.md`

### Support
- Template feedback: `gitignore/Agent History/workflow-feedback.md`
- Issue tracking: `gitignore/Claude Context/CLAUDE.context.md`
- Questions: Document in Claude Context and reference in session

---

**Documentation Version**: 1.0
**Created**: 2025-10-05
**Last Updated**: 2025-10-05
**Maintained By**: Framework Development Agent
