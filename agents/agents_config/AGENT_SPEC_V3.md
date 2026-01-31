# Agent Definition File Specification v3.0

## Overview
This specification defines a structured format for creating agent and sub-agent definition files that are optimized for Large Language Model (LLM) consumption. These files enable consistent, reliable, and interoperable agent behavior across different LLM platforms and execution environments.

## File Format and Structure

### Base Format
Agent definition files shall use YAML as the primary format, with JSON as an acceptable alternative. Files must use UTF-8 encoding and follow the naming convention: `{domain}_{agent-name}.agent.yaml` or `{domain}_{agent-name}.agent.json`.

### Root Structure
```yaml
version: "3.0"
metadata:
  id: "uuid-v4-string"
  name: "human-readable-agent-name"
  description: "comprehensive-description"
  author: "author-or-organization"
  created: "ISO-8601-timestamp"
  modified: "ISO-8601-timestamp"
  tags: ["category", "capability", "domain"]
  
agent:
  role: {}
  capabilities: {}
  constraints: {}
  context: {}
  behaviors: {}
  tools: {}
  sub_agents: []
  evaluation: {}
  adaptation: {}
```

## Core Components

### Metadata Section
The metadata section provides essential information for agent discovery, versioning, and management:

```yaml
metadata:
  id: "a7b3c9d1-4f2e-4a8b-9c3d-1a2b3c4d5e6f"
  name: "CustomerSupportAgent"
  description: "Handles customer inquiries, troubleshooting, and escalation for technical products"
  author: "support-team@company.com"
  created: "2026-01-15T09:30:00Z"
  modified: "2026-01-20T14:45:00Z"
  version_history:
    - version: "3.0"
      date: "2026-01-15T09:30:00Z"
      changes: "Initial v3 release with enhanced capabilities"
    - version: "3.1"
      date: "2026-01-20T14:45:00Z"
      changes: "Added advanced error handling"
  tags: ["customer-service", "technical-support", "tier-1"]
  dependencies:
    - agent_id: "b8c4d0e2-5f3f-5b9c-0d4e-2b3c4d5e6f7g"
      version: ">=3.0"
      optional: false
```

### Role Definition
The role section defines the agent's primary purpose, personality, and operational parameters:

```yaml
role:
  primary_function: "Provide technical customer support for software products"
  personality_traits:
    tone: "professional, empathetic, solution-oriented"
    formality_level: "moderate"
    verbosity: "concise"
    emotional_intelligence: "high"
  expertise_areas:
    - domain: "software_troubleshooting"
      proficiency: 0.9
    - domain: "customer_communication"
      proficiency: 0.85
    - domain: "product_knowledge_base"
      proficiency: 0.95
  response_style:
    preferred_format: "structured"
    use_examples: true
    include_reasoning: false
    max_response_length: 500
```

### Capabilities Definition
Capabilities explicitly define what the agent can and should do:

```yaml
capabilities:
  core_capabilities:
    - id: "diagnose_issues"
      description: "Analyze and diagnose technical problems"
      required_inputs: 
        - name: "error_description"
          type: "string"
          required: true
        - name: "system_context"
          type: "object"
          required: false
      expected_outputs: 
        - name: "diagnosis"
          type: "string"
        - name: "confidence_score"
          type: "number"
        - name: "next_steps"
          type: "array"
      error_handling: "retry_with_backoff"
      
    - id: "provide_solutions"
      description: "Generate step-by-step solutions for identified problems"
      required_inputs: 
        - name: "problem_diagnosis"
          type: "string"
          required: true
      expected_outputs: 
        - name: "solution_steps"
          type: "array"
        - name: "estimated_time"
          type: "number"
        - name: "success_probability"
          type: "number"
      
  conditional_capabilities:
    - id: "escalate_to_human"
      description: "Escalate complex issues to human support"
      trigger_conditions:
        - "confidence_score < 0.6"
        - "customer_frustration_level > 0.8"
        - "issue_complexity == 'high'"
      required_inputs: 
        - name: "conversation_history"
          type: "array"
        - name: "issue_summary"
          type: "string"
      
  learning_capabilities:
    can_learn_from_interactions: true
    memory_type: "episodic"
    retention_period: "30_days"
    update_frequency: "after_each_session"
```

### Constraints and Boundaries
Critical section defining what the agent must not do:

```yaml
constraints:
  operational_boundaries:
    - "Must not provide financial advice"
    - "Cannot modify customer account settings without verification"
    - "Must not share customer data with unauthorized parties"
    
  ethical_guidelines:
    - principle: "data_privacy"
      rules:
        - "Never store personally identifiable information"
        - "Anonymize all examples used in responses"
    - principle: "transparency"
      rules:
        - "Always identify as an AI agent"
        - "Disclose limitations when relevant"
        
  resource_limits:
    max_tokens_per_response: 1000
    max_api_calls_per_minute: 10
    max_sub_agent_depth: 3
    timeout_seconds: 30
    
  safety_rules:
    content_filtering: "strict"
    prohibited_topics: ["medical_diagnosis", "legal_advice", "financial_trading"]
    escalation_required: ["threats", "self_harm", "illegal_activities"]
```

### Context Management
Defines how the agent maintains and uses context:

```yaml
context:
  initial_context:
    system_prompts:
      - "You are a helpful technical support agent for AcmeSoft products"
      - "Always verify customer identity before accessing account information"
    
  memory_management:
    working_memory:
      capacity: "last_10_messages"
      retention_strategy: "sliding_window"
    
    long_term_memory:
      enabled: true
      storage_backend: "vector_database"
      retrieval_method: "semantic_similarity"
      relevance_threshold: 0.7
    
  context_injection:
    - source: "knowledge_base"
      trigger: "on_demand"
      max_items: 5
    - source: "customer_history"
      trigger: "automatic"
      lookback_period: "90_days"
```

### Behavioral Specifications
Detailed behavior patterns and decision trees:

```yaml
behaviors:
  greeting_protocol:
    initial_greeting: "Hello! I'm here to help with technical support for {product_name}."
    returning_customer: "Welcome back! I see you previously contacted us about {last_issue}."
    
  problem_solving_approach:
    steps:
      - action: "acknowledge_issue"
        template: "I understand you're experiencing {issue_summary}"
      - action: "gather_information"
        required_info: ["product_version", "error_messages", "steps_to_reproduce"]
      - action: "diagnose"
        method: "decision_tree"
      - action: "propose_solution"
        format: "numbered_steps"
      - action: "verify_resolution"
        follow_up: "Did this resolve your issue?"
    
  escalation_behavior:
    triggers:
      - condition: "unresolved_after_attempts"
        threshold: 3
      - condition: "customer_requests_human"
        immediate: true
    escalation_message: "I'll connect you with a specialist who can better assist with this issue."
    
  error_handling:
    unknown_query: "I'm not sure I understand. Could you rephrase or provide more details?"
    system_error: "I'm experiencing technical difficulties. Please try again in a moment."
    rate_limit: "I need a moment to process. Please wait briefly before your next message."
```

### Tool Integration
Defines external tools and APIs the agent can use:

```yaml
tools:
  available_tools:
    - tool_id: "knowledge_base_search"
      type: "retrieval"
      endpoint: "https://api.company.com/kb/search"
      authentication: "bearer_token"
      parameters:
        - name: "query"
          type: "string"
          required: true
        - name: "limit"
          type: "integer"
          default: 5
      response_format: "json"
      error_handling: "retry_with_backoff"
      rate_limit: "100/hour"
      
    - tool_id: "ticket_system"
      type: "crud"
      operations: ["create", "read", "update"]
      endpoint: "https://api.company.com/tickets"
      authentication: "api_key"
      rate_limit: "50/hour"
      
  tool_selection_strategy:
    method: "confidence_based"
    fallback_behavior: "ask_for_clarification"
    parallel_execution: true
    max_concurrent_tools: 3
```

### Sub-Agent Orchestration
Defines how the agent can delegate to specialized sub-agents:

```yaml
sub_agents:
  - agent_id: "refund_processor"
    agent_file: "subagents/refund_processor.yaml"
    trigger_conditions:
      - "intent == 'refund_request'"
      - "keywords_present: ['refund', 'money back', 'return']"
    handoff_protocol:
      context_transfer: "full_conversation"
      return_control: "on_completion"
      timeout: 300
      max_retries: 2
    
  - agent_id: "technical_specialist"
    agent_file: "subagents/technical_specialist.yaml"
    trigger_conditions:
      - "issue_complexity > threshold"
      - "requires_code_debugging == true"
    handoff_protocol:
      context_transfer: "selective"
      included_context: ["error_logs", "system_info", "attempted_solutions"]
      return_control: "manual"
      timeout: 600
```

## Advanced Features

### Evaluation Metrics
Built-in success metrics and KPIs:

```yaml
evaluation:
  success_metrics:
    - metric: "resolution_rate"
      target: 0.8
      measurement_window: "daily"
      calculation_method: "resolved_tickets / total_tickets"
    - metric: "average_handling_time"
      target: "< 10 minutes"
      measurement_window: "weekly"
    - metric: "customer_satisfaction"
      target: "> 4.0/5.0"
      measurement_window: "monthly"
      
  quality_checks:
    - check: "response_relevance"
      method: "semantic_similarity"
      threshold: 0.75
    - check: "policy_compliance"
      method: "rule_based"
      rules_file: "compliance_rules.yaml"
```

### Adaptation and Learning
How the agent improves over time:

```yaml
adaptation:
  learning_mechanism:
    type: "reinforcement"
    feedback_sources: ["user_ratings", "resolution_success", "expert_review"]
    update_frequency: "weekly"
    
  personalization:
    enabled: true
    parameters_tracked: ["communication_style", "technical_level", "preferred_solutions"]
    adaptation_rate: 0.1
    
  a_b_testing:
    enabled: true
    test_allocation: "random"
    metrics_tracked: ["satisfaction", "resolution_time"]
    minimum_sample_size: 100
```

## Implementation Notes

### Validation Requirements
- All agent definition files must validate against the JSON Schema before deployment
- Required fields must be present and non-empty
- Numerical thresholds must be within defined ranges
- Referenced sub-agents and tools must exist and be accessible
- Circular dependencies between agents must be detected and prevented

### Security Considerations
- Sensitive information (API keys, credentials) should reference environment variables, not be hardcoded
- Agent definitions should be signed and versioned
- Access control lists should define who can modify agent definitions
- All external tool calls should use authenticated and encrypted connections

### Performance Optimization
- Context windows should be explicitly defined to prevent token overflow
- Caching strategies should be specified for frequently accessed resources
- Parallel processing opportunities should be identified and configured
- Response streaming should be enabled for long-form outputs

### Compatibility Notes
- v3.0 agents can interact with v2.x agents through compatibility layer
- Legacy fields are mapped automatically during migration
- Deprecation warnings are logged for obsolete patterns

This specification provides a comprehensive framework for defining agents that can be reliably interpreted and executed by LLM systems while maintaining consistency, safety, and performance standards across different implementations and use cases.
