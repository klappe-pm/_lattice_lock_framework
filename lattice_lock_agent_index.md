# Lattice Lock Framework - Complete Agent Index

> **LLM INSTRUCTION**: Read this entire file to understand the complete agent taxonomy, hierarchy, and relationships.

---

## Summary Statistics

| Metric | Count |
|--------|-------|
| Parent Agents | 15 |
| Total Subagents | 102 |
| Total Agent Files | 117 |
| Agents with Subagents | 14 |
| Standalone Orchestrators | 1 |

---

## Complete Agent Hierarchy

### 1. business_review_agent
**Role:** Business Intelligence Lead
**Version:** 2.1.0
**Inherits From:** base_agent_v2.1.yaml
**Primary Goal:** Deliver actionable business intelligence and ensure organizational alignment.
**Subagents:** 8

| Subagent Name | Role | Inherits From |
|---------------|------|---------------|
| competitive_intelligence_analyst | Intelligence Analyst | intelligence_subagent_v2.1.yaml |
| data_quality_manager | Data Steward | analytics_subagent_v2.1.yaml |
| financial_analyst | Financial Analyst | analytics_subagent_v2.1.yaml |
| okr_tracker | OKR Tracker | analytics_subagent_v2.1.yaml |
| performance_analyst | Performance Analyst | analytics_subagent_v2.1.yaml |
| process_improvement_specialist | Process Specialist | operational_subagent_v2.1.yaml |
| reporting_automation_specialist | Reporting Automation Lead | automation_subagent_v2.1.yaml |
| risk_assessment_analyst | Risk Analyst | analytics_subagent_v2.1.yaml |

---

### 2. cloud_agent
**Role:** Cloud Architect
**Version:** 2.1.0
**Inherits From:** base_agent_v2.1.yaml
**Primary Goal:** Provision, manage, and optimize cloud resources across multi-cloud environments.
**Subagents:** 3

| Subagent Name | Role | Inherits From |
|---------------|------|---------------|
| aws_agent | AWS Cloud Specialist | infrastructure_subagent_v2.1.yaml |
| azure_agent | Azure Cloud Specialist | infrastructure_subagent_v2.1.yaml |
| google_cloud_agent | GCP Cloud Specialist | infrastructure_subagent_v2.1.yaml |

---

### 3. content_agent
**Role:** Editorial Director
**Version:** 2.1.0
**Inherits From:** base_agent_v2.1.yaml
**Primary Goal:** Produce and distribute high-quality, SEO-optimized content across multiple channels.
**Subagents:** 13

| Subagent Name | Role | Inherits From |
|---------------|------|---------------|
| analyst | Content Analyst | analytics_subagent_v2.1.yaml |
| content_strategist | Content Strategist | creative_subagent_v2.1.yaml |
| copywriter | Copywriter | creative_subagent_v2.1.yaml |
| editor | Editor | creative_subagent_v2.1.yaml |
| editorial_manager | Editorial Manager | operational_subagent_v2.1.yaml |
| email_marketing_specialist | Email Specialist | operational_subagent_v2.1.yaml |
| localization_expert | Localization Lead | creative_subagent_v2.1.yaml |
| operations_specialist | Content Ops | operational_subagent_v2.1.yaml |
| seo_specialist | SEO Engineer | technical_subagent_v2.1.yaml |
| social_media_strategist | Social Lead | planning_subagent_v2.1.yaml |
| style_guide_reviewer | Style Guide Reviewer | creative_subagent_v2.1.yaml |
| technical_writer | Technical Writer | creative_subagent_v2.1.yaml |
| writer | Content Writer | creative_subagent_v2.1.yaml |

---

### 4. context_agent
**Role:** Knowledge Architect
**Version:** 2.1.0
**Inherits From:** base_agent_v2.1.yaml
**Primary Goal:** Maintain high-fidelity context and validation across the agent ecosystem.
**Max Delegation Depth:** 3
**Subagents:** 6

| Subagent Name | Role | Inherits From |
|---------------|------|---------------|
| chat_summary | Session Summarizer | memory_subagent_v2.1.yaml |
| information_gatherer | Data Gatherer | operational_subagent_v2.1.yaml |
| knowledge_synthesizer | Knowledge Architect | memory_subagent_v2.1.yaml |
| llm_memory_specialist | Retrieval Engineer | memory_subagent_v2.1.yaml |
| memory_storage | Storage Administrator | memory_subagent_v2.1.yaml |
| validator | Validation Engineer | technical_subagent_v2.1.yaml |

---

### 5. education_agent
**Role:** Education Director
**Version:** 1.0.0
**Inherits From:** base_agent_v2.1.yaml
**Primary Goal:** Empower users and developers through structured learning paths, tutorials, and certification programs.
**Subagents:** 3

| Subagent Name | Role | Inherits From |
|---------------|------|---------------|
| curriculum_developer | Curriculum Developer | creative_subagent_v2.1.yaml |
| instructional_designer | Instructional Designer | creative_subagent_v2.1.yaml |
| training_facilitator | Training Facilitator | creative_subagent_v2.1.yaml |

---

### 6. engineering_agent
**Role:** Engineering Lead
**Version:** 2.1.0
**Inherits From:** base_agent_v2.1.yaml
**Primary Goal:** Design, implement, and maintain high-performance software systems.
**Subagents:** 8

| Subagent Name | Role | Inherits From |
|---------------|------|---------------|
| api_designer | API Architect | technical_subagent_v2.1.yaml |
| backend_developer | Backend Engineer | technical_subagent_v2.1.yaml |
| database_administrator | Database Engineer | technical_subagent_v2.1.yaml |
| devops_engineer | DevOps Engineer | technical_subagent_v2.1.yaml |
| frontend_developer | Frontend Engineer | technical_subagent_v2.1.yaml |
| security_engineer | Security Engineer | technical_subagent_v2.1.yaml |
| system_architect | System Architect | technical_subagent_v2.1.yaml |
| testing_qa_specialist | QA Engineer | technical_subagent_v2.1.yaml |

---

### 7. google_apps_script_agent
**Role:** Apps Script Architect
**Version:** 2.1.0
**Inherits From:** base_agent_v2.1.yaml
**Primary Goal:** Build and automate workflows across Google Workspace using Apps Script.
**Subagents:** 8

| Subagent Name | Role | Inherits From |
|---------------|------|---------------|
| script_architect | Apps Script Architect | technical_subagent_v2.1.yaml |
| script_cost_analyzer | Cost Planner | planning_subagent_v2.1.yaml |
| script_deployer | Deployment Manager | infrastructure_subagent_v2.1.yaml |
| script_developer | Apps Script Developer | technical_subagent_v2.1.yaml |
| script_devtools_manager | Tooling Lead | technical_subagent_v2.1.yaml |
| script_ide_handler | Environment Specialist | technical_subagent_v2.1.yaml |
| script_integrator | Integration Specialist | automation_subagent_v2.1.yaml |
| script_tester | Apps Script QA | technical_subagent_v2.1.yaml |

---

### 8. model_orchestration_agent
**Role:** Orchestrator
**Version:** 2.1.0
**Inherits From:** base_agent_v2.1.yaml
**Primary Goal:** Optimize model utilization to balance cost, speed, and accuracy for every task.
**Max Delegation Depth:** 1
**Subagents:** 0 (Standalone orchestrator - routes to other parent agents)

---

### 9. product_agent
**Role:** Product Director
**Version:** 2.1.0
**Inherits From:** base_agent_v2.1.yaml
**Primary Goal:** Define and drive the product roadmap through strategic discovery and roadmap prioritization.
**Subagents:** 11

| Subagent Name | Role | Inherits From |
|---------------|------|---------------|
| business_analyst | Business Analyst | analytics_subagent_v2.1.yaml |
| business_case_owner | Business Case Lead | planning_subagent_v2.1.yaml |
| dashboard_designer | Visualization Designer | creative_subagent_v2.1.yaml |
| dashboard_requirements_writer | Requirements Engineer | planning_subagent_v2.1.yaml |
| frameworks_designer | Framework Architect | planning_subagent_v2.1.yaml |
| internal_documentation_researcher | Internal Knowledge Scout | intelligence_subagent_v2.1.yaml |
| metrics_analyst | Product Analyst | analytics_subagent_v2.1.yaml |
| metrics_researcher | Product Intelligence Researcher | intelligence_subagent_v2.1.yaml |
| operations | Product Ops Automation | automation_subagent_v2.1.yaml |
| opportunity_solutions_tree_designer | Discovery Specialist | planning_subagent_v2.1.yaml |
| strategist | Product Strategist | planning_subagent_v2.1.yaml |

---

### 10. product_management_agent
**Role:** Chief Product Officer
**Version:** 1.0.0
**Inherits From:** base_agent_v2.1.yaml
**Primary Goal:** Drive product success through rigorous strategy, data-driven discovery, and executed roadmaps.
**Subagents:** 10

| Subagent Name | Role | Inherits From |
|---------------|------|---------------|
| brand_strategist | Brand Strategist | creative_subagent_v2.1.yaml |
| competitive_analyst | Competitive Analyst | creative_subagent_v2.1.yaml |
| growth_manager | Growth Manager | creative_subagent_v2.1.yaml |
| gtm_lead | GTM Lead | creative_subagent_v2.1.yaml |
| key_result_analyst | Key Result Analyst | creative_subagent_v2.1.yaml |
| objective_strategist | Objective Strategist | creative_subagent_v2.1.yaml |
| opportunity_analyst | Discovery Lead | creative_subagent_v2.1.yaml |
| product_marketing_manager | Product Marketing Manager | creative_subagent_v2.1.yaml |
| product_strategist | Product Strategist | creative_subagent_v2.1.yaml |
| roadmapper | Roadmap Owner | creative_subagent_v2.1.yaml |

---

### 11. project_agent
**Role:** Senior Project Manager
**Version:** 2.1.0
**Inherits From:** base_agent_v2.1.yaml
**Primary Goal:** Manage project timelines, resources, and stakeholder communications.
**Subagents:** 4

| Subagent Name | Role | Inherits From |
|---------------|------|---------------|
| project_analyst | Project Analyst | analytics_subagent_v2.1.yaml |
| project_planner | Project Planner | planning_subagent_v2.1.yaml |
| project_status_writer | Status Specialist | operational_subagent_v2.1.yaml |
| task_manager | Task Coordinator | operational_subagent_v2.1.yaml |

---

### 12. prompt_architect_agent
**Role:** Prompt Engineer
**Version:** 2.1.0
**Inherits From:** base_agent_v2.1.yaml
**Primary Goal:** Architect and refine prompts that ensure accurate, safe, and efficient agent execution.
**Subagents:** 4

| Subagent Name | Role | Inherits From |
|---------------|------|---------------|
| prompt_generator | Prompt Creator | creative_subagent_v2.1.yaml |
| roadmap_parser | Roadmap Parser | planning_subagent_v2.1.yaml |
| spec_analyzer | Spec Analyst | planning_subagent_v2.1.yaml |
| tool_matcher | Tooling Logic Lead | automation_subagent_v2.1.yaml |

---

### 13. public_relations_agent
**Role:** PR Director
**Version:** 2.1.0
**Inherits From:** base_agent_v2.1.yaml
**Primary Goal:** Craft and maintain a positive and consistent public image for the project.
**Max Delegation Depth:** 1
**Subagents:** 2

| Subagent Name | Role | Inherits From |
|---------------|------|---------------|
| advertising_specialist | Advertising Specialist | creative_subagent_v2.1.yaml |
| press_release_writer | PR Writer | creative_subagent_v2.1.yaml |

---

### 14. research_agent
**Role:** Research Lead
**Version:** 2.1.0
**Inherits From:** base_agent_v2.1.yaml
**Primary Goal:** Provide deep, evidence-based insights to inform product and business strategy.
**Subagents:** 7

| Subagent Name | Role | Inherits From |
|---------------|------|---------------|
| competitive_intelligence_analyst | Research Specialist | intelligence_subagent_v2.1.yaml |
| data_analyst | Research Data Analyst | analytics_subagent_v2.1.yaml |
| market_research_analyst | Market Analyst | intelligence_subagent_v2.1.yaml |
| qualitative_research_expert | Qualitative Researcher | intelligence_subagent_v2.1.yaml |
| report_writer | Research Reporter | creative_subagent_v2.1.yaml |
| survey_research_specialist | Survey Specialist | intelligence_subagent_v2.1.yaml |
| user_research_specialist | User Researcher | intelligence_subagent_v2.1.yaml |

---

### 15. ux_agent
**Role:** Design Lead
**Version:** 2.1.0
**Inherits From:** base_agent_v2.1.yaml
**Primary Goal:** Ensure a seamless, accessible, and high-conversion user experience across all frameworks.
**Subagents:** 15

| Subagent Name | Role | Inherits From |
|---------------|------|---------------|
| accessibility_specialist | Accessibility Engineer | technical_subagent_v2.1.yaml |
| customer_journey_mapper | Experience Architect | creative_subagent_v2.1.yaml |
| diagram_designer | Diagram Designer | creative_subagent_v2.1.yaml |
| flow_architect | Flow Architect | creative_subagent_v2.1.yaml |
| information_architect | Information Architect | creative_subagent_v2.1.yaml |
| interaction_designer | Interaction Designer | creative_subagent_v2.1.yaml |
| jtbd_researcher | JTBD Researcher | creative_subagent_v2.1.yaml |
| metrics_analyst | UX Data Analyst | analytics_subagent_v2.1.yaml |
| prototype_builder | Interaction Prototyper | creative_subagent_v2.1.yaml |
| service_blueprinter | Service Blueprinter | creative_subagent_v2.1.yaml |
| usability_tester | Usability Engineer | technical_subagent_v2.1.yaml |
| user_persona_developer | Persona Researcher | intelligence_subagent_v2.1.yaml |
| ux_strategist | UX Strategist | creative_subagent_v2.1.yaml |
| visual_designer | Visual Designer | creative_subagent_v2.1.yaml |
| wireframe_creator | UI Architect | creative_subagent_v2.1.yaml |

---

## Subagent Template Inheritance Hierarchy

```
base_agent_v2.1.yaml
├── analytics_subagent_v2.1.yaml (10 subagents)
│   ├── business_review_agent: financial_analyst, okr_tracker, performance_analyst,
│   │                          data_quality_manager, risk_assessment_analyst
│   ├── product_agent: business_analyst, metrics_analyst
│   ├── project_agent: project_analyst
│   ├── research_agent: data_analyst
│   └── ux_agent: metrics_analyst
│
├── automation_subagent_v2.1.yaml (4 subagents)
│   ├── business_review_agent: reporting_automation_specialist
│   ├── google_apps_script_agent: script_integrator
│   ├── product_agent: operations
│   └── prompt_architect_agent: tool_matcher
│
├── creative_subagent_v2.1.yaml (36 subagents)
│   ├── content_agent: content_strategist, copywriter, editor, localization_expert,
│   │                  style_guide_reviewer, technical_writer, writer
│   ├── education_agent: curriculum_developer, instructional_designer, training_facilitator
│   ├── product_agent: dashboard_designer
│   ├── product_management_agent: ALL 10 subagents
│   ├── prompt_architect_agent: prompt_generator
│   ├── public_relations_agent: advertising_specialist, press_release_writer
│   ├── research_agent: report_writer
│   └── ux_agent: customer_journey_mapper, diagram_designer, flow_architect,
│                 information_architect, interaction_designer, jtbd_researcher,
│                 prototype_builder, service_blueprinter, ux_strategist,
│                 visual_designer, wireframe_creator
│
├── infrastructure_subagent_v2.1.yaml (4 subagents)
│   ├── cloud_agent: aws_agent, azure_agent, google_cloud_agent
│   └── google_apps_script_agent: script_deployer
│
├── intelligence_subagent_v2.1.yaml (9 subagents)
│   ├── business_review_agent: competitive_intelligence_analyst
│   ├── product_agent: internal_documentation_researcher, metrics_researcher
│   ├── research_agent: competitive_intelligence_analyst, market_research_analyst,
│   │                   qualitative_research_expert, survey_research_specialist,
│   │                   user_research_specialist
│   └── ux_agent: user_persona_developer
│
├── memory_subagent_v2.1.yaml (4 subagents)
│   └── context_agent: chat_summary, knowledge_synthesizer, llm_memory_specialist, memory_storage
│
├── operational_subagent_v2.1.yaml (7 subagents)
│   ├── business_review_agent: process_improvement_specialist
│   ├── content_agent: editorial_manager, email_marketing_specialist, operations_specialist
│   ├── context_agent: information_gatherer
│   └── project_agent: project_status_writer, task_manager
│
├── planning_subagent_v2.1.yaml (11 subagents)
│   ├── content_agent: social_media_strategist
│   ├── google_apps_script_agent: script_cost_analyzer
│   ├── product_agent: business_case_owner, dashboard_requirements_writer,
│   │                  frameworks_designer, opportunity_solutions_tree_designer, strategist
│   ├── project_agent: project_planner
│   └── prompt_architect_agent: roadmap_parser, spec_analyzer
│
└── technical_subagent_v2.1.yaml (17 subagents)
    ├── content_agent: seo_specialist
    ├── context_agent: validator
    ├── engineering_agent: ALL 8 subagents
    ├── google_apps_script_agent: script_architect, script_developer, script_devtools_manager,
    │                             script_ide_handler, script_tester
    └── ux_agent: accessibility_specialist, usability_tester
```

---

## Base Agent Template Configuration

All agents inherit from `base_agent_v2.1.yaml` which defines:

### Configuration Defaults
- **Language:** en-US
- **Timezone:** UTC
- **Log Level:** INFO
- **Max Steps:** 50
- **Timeout:** 300 seconds

### Delegation Settings
- **Default Max Depth:** 2
- **Delegation Triggers:** Task requires specialization

### Model Selection Strategies
| Strategy | Primary Model | Fallback | Criteria |
|----------|---------------|----------|----------|
| Code Generation | codellama:34b | claude-3.5-sonnet | accuracy > speed |
| Reasoning | deepseek-r1:70b | claude-3.5-sonnet | depth > speed |
| Quick Response | llama3.1:8b | gpt-4o-mini | speed > accuracy |

### Cost Limits
- **Warning Threshold:** $0.10
- **Hard Limit:** $1.00
- **Approval Required Above:** $0.50

### Guardrails
- Never commit secrets to git
- Never delete files without confirmation
- Never execute arbitrary code outside sandbox
- Max cost per session: $5.00

### Escalation Triggers
- If confidence < 0.7
- If cost > $1.00
- If user intent is unclear

---

## Reference

- **Framework Source:** https://github.com/klappe-pm/lattice-lock-framework
- **Agent Definitions:** /agents/agent_definitions/
- **Agent Templates:** /agents/agent_templates/
- **Total Files Indexed:** 117
