# Lattice Lock Agent Taxonomy

## Overview

This document provides a comprehensive reference for all agents and subagents defined in the Lattice Lock framework. It covers the naming conventions, hierarchical relationships, and functional domains of each agent.

### Summary Statistics

| Metric | Count |
|--------|-------|
| **Parent Agents** | 15 |
| **Total Subagents** | 102 |
| **Agents with Subagents** | 14 |
| **Standalone Orchestrators** | 1 |

### Agent-Subagent Distribution

| Parent Agent | Subagent Count | Domain |
|--------------|----------------|--------|
| ux_agent | 15 | User Experience & Design |
| content_agent | 13 | Content Creation & Distribution |
| product_agent | 11 | Product Strategy & Discovery |
| product_management_agent | 10 | Product Lifecycle Management |
| business_review_agent | 8 | Business Intelligence & Analysis |
| engineering_agent | 8 | Software Development & DevOps |
| google_apps_script_agent | 8 | Google Workspace Automation |
| research_agent | 7 | User & Market Research |
| context_agent | 6 | Knowledge & Memory Management |
| project_agent | 4 | Project Planning & Execution |
| prompt_architect_agent | 4 | Prompt Engineering & Optimization |
| cloud_agent | 3 | Multi-Cloud Infrastructure |
| education_agent | 3 | Training & Curriculum Development |
| public_relations_agent | 2 | PR & External Communications |
| model_orchestration_agent | 0 | Model Routing (no subagents) |

---

## Naming Conventions

### Pattern Overview

Agents in Lattice Lock follow a **professional role-based naming convention** rather than anthropomorphized or personality-based names. This approach emphasizes clarity and domain alignment.

### Parent Agent Naming

- **Format**: `{domain}_agent`
- **Examples**: `engineering_agent`, `content_agent`, `research_agent`
- **Role Assignment**: Each parent agent is assigned a senior leadership role (e.g., "Engineering Lead", "Editorial Director", "Research Lead")

### Subagent Naming

- **Format**: `{function/role}_specialist` or `{job_title}`
- **Examples**: `api_designer`, `data_analyst`, `wireframe_creator`
- **File Naming**: `{parent_agent}_{subagent_name}_definition.yaml`

### Role Titles

Agents are given professional role titles that reflect their function:

| Agent Type | Example Roles |
|------------|---------------|
| Parent Agents | Director, Lead, Architect, Chief Officer |
| Subagents | Analyst, Specialist, Designer, Developer, Manager |

### Key Characteristics

1. **Non-Anthropomorphic**: Agents are named after functions, not personalities
2. **Domain-Aligned**: Names clearly indicate the agent's area of expertise
3. **Hierarchical Clarity**: Parent-subagent relationships are explicit through file organization
4. **Professional Titles**: Roles mirror real-world job functions for intuitive understanding

---

## Agent Reference

### Business Review Agent

**Role**: Business Intelligence Lead
**Description**: Orchestrates comprehensive business analysis, OKR tracking, and market intelligence synthesis.
**Domain**: Business Intelligence & Analysis

| Subagent | Role | Description |
|----------|------|-------------|
| competitive_intelligence_analyst | Intelligence Analyst | Analyzes competitive landscape and market positioning |
| data_quality_manager | Data Quality Lead | Ensures data integrity and quality standards |
| financial_analyst | Financial Analyst | Conducts financial analysis and reporting |
| okr_tracker | OKR Specialist | Monitors and tracks OKR progress and alignment |
| performance_analyst | Performance Analyst | Analyzes operational and business performance metrics |
| process_improvement_specialist | Process Engineer | Identifies and implements process improvements |
| reporting_automation_specialist | Automation Engineer | Automates business reporting workflows |
| risk_assessment_analyst | Risk Analyst | Evaluates and reports on business risks |

---

### Cloud Agent

**Role**: Cloud Architect
**Description**: Manages cloud infrastructure across AWS, Azure, and Google Cloud.
**Domain**: Multi-Cloud Infrastructure

| Subagent | Role | Description |
|----------|------|-------------|
| aws_agent | AWS Specialist | Manages Amazon Web Services resources and configurations |
| azure_agent | Azure Specialist | Manages Microsoft Azure resources and configurations |
| google_cloud_agent | GCP Specialist | Manages Google Cloud Platform resources and configurations |

---

### Content Agent

**Role**: Editorial Director
**Description**: Manages full-lifecycle content strategy, creation, and distribution.
**Domain**: Content Creation & Distribution

| Subagent | Role | Description |
|----------|------|-------------|
| analyst | Content Analyst | Analyzes content performance and engagement metrics |
| content_strategist | Content Strategist | Develops content strategy and editorial calendars |
| copywriter | Copywriter | Creates persuasive marketing and advertising copy |
| editor | Editor | Reviews and refines content for quality and consistency |
| editorial_manager | Editorial Manager | Coordinates editorial workflows and content pipelines |
| email_marketing_specialist | Email Marketer | Designs and optimizes email marketing campaigns |
| localization_expert | Localization Lead | Adapts content for international markets and languages |
| operations_specialist | Content Ops Specialist | Manages content operations and publishing workflows |
| seo_specialist | SEO Specialist | Optimizes content for search engine visibility |
| social_media_strategist | Social Media Lead | Develops social media strategy and campaigns |
| style_guide_reviewer | Style Guide Specialist | Ensures brand voice and style guide compliance |
| technical_writer | Technical Writer | Creates technical documentation and guides |
| writer | Content Writer | Generates long-form content including blogs and whitepapers |

---

### Context Agent

**Role**: Knowledge Architect
**Description**: Manages the framework's knowledge state, history synthesis, and validation.
**Domain**: Knowledge & Memory Management

| Subagent | Role | Description |
|----------|------|-------------|
| chat_summary | Summarization Specialist | Synthesizes conversation histories into summaries |
| information_gatherer | Information Specialist | Collects and organizes relevant contextual information |
| knowledge_synthesizer | Knowledge Engineer | Synthesizes information into structured knowledge |
| llm_memory_specialist | Memory Engineer | Manages LLM memory and context persistence |
| memory_storage | Storage Specialist | Handles long-term memory storage and retrieval |
| validator | Validation Specialist | Validates context accuracy and consistency |

---

### Education Agent

**Role**: Education Director
**Description**: Develops comprehensive educational strategies, training courses, and learning materials.
**Domain**: Training & Curriculum Development

| Subagent | Role | Description |
|----------|------|-------------|
| curriculum_developer | Curriculum Designer | Designs learning paths and course structures |
| instructional_designer | Instructional Designer | Creates interactive training modules and content |
| training_facilitator | Training Facilitator | Delivers and facilitates training sessions |

---

### Engineering Agent

**Role**: Engineering Lead
**Description**: Orchestrates full-stack engineering, from system architecture to quality assurance.
**Domain**: Software Development & DevOps

| Subagent | Role | Description |
|----------|------|-------------|
| api_designer | API Architect | Designs RESTful and GraphQL API specifications |
| backend_developer | Backend Engineer | Develops server-side logic and services |
| database_administrator | DBA | Manages database design, optimization, and maintenance |
| devops_engineer | DevOps Engineer | Manages CI/CD pipelines and infrastructure automation |
| frontend_developer | Frontend Engineer | Develops user interfaces and client-side logic |
| security_engineer | Security Engineer | Implements security measures and conducts audits |
| system_architect | System Architect | Designs system architecture and technical specifications |
| testing_qa_specialist | QA Engineer | Develops and executes testing strategies |

---

### Google Apps Script Agent

**Role**: Apps Script Architect
**Description**: Specialized in developing and deploying Google Apps Script solutions and integrations.
**Domain**: Google Workspace Automation

| Subagent | Role | Description |
|----------|------|-------------|
| script_architect | Script Architect | Designs script architecture and integration patterns |
| script_cost_analyzer | Cost Analyst | Analyzes script execution costs and quotas |
| script_deployer | Deployment Engineer | Manages script deployment and versioning |
| script_developer | Script Developer | Develops Google Apps Script code and functions |
| script_devtools_manager | DevTools Manager | Manages development tools and environments |
| script_ide_handler | IDE Specialist | Handles IDE integrations and configurations |
| script_integrator | Integration Engineer | Integrates scripts with external services |
| script_tester | Script Tester | Tests and validates script functionality |

---

### Model Orchestration Agent

**Role**: Orchestrator
**Description**: Manages high-level model selection, routing, and cognitive load balancing across the agent network.
**Domain**: Model Routing

*This agent has no subagents. It routes tasks to other parent agents based on complexity and requirements.*

---

### Product Agent

**Role**: Product Director
**Description**: Orchestrates product strategy, discovery, and requirements management.
**Domain**: Product Strategy & Discovery

| Subagent | Role | Description |
|----------|------|-------------|
| business_analyst | Business Analyst | Analyzes business requirements and impact |
| business_case_owner | Business Case Lead | Develops and owns business case documentation |
| dashboard_designer | Dashboard Designer | Designs analytics dashboards and visualizations |
| dashboard_requirements_writer | Requirements Writer | Documents dashboard functional requirements |
| frameworks_designer | Frameworks Designer | Designs product frameworks and methodologies |
| internal_documentation_researcher | Documentation Researcher | Researches and synthesizes internal documentation |
| metrics_analyst | Metrics Analyst | Analyzes product metrics and KPIs |
| metrics_researcher | Metrics Researcher | Researches industry metrics and benchmarks |
| operations | Product Operations | Manages product operations workflows |
| opportunity_solutions_tree_designer | OST Designer | Designs opportunity solution trees |
| strategist | Product Strategist | Develops product strategy and vision |

---

### Product Management Agent

**Role**: Chief Product Officer
**Description**: Orchestrates the entire product lifecycle from strategy and discovery to launch and growth.
**Domain**: Product Lifecycle Management

| Subagent | Role | Description |
|----------|------|-------------|
| brand_strategist | Brand Strategist | Develops brand positioning and messaging |
| competitive_analyst | Competitive Analyst | Analyzes competitive landscape and positioning |
| growth_manager | Growth Manager | Optimizes growth loops and user acquisition |
| gtm_lead | GTM Lead | Leads go-to-market planning and execution |
| key_result_analyst | KR Analyst | Analyzes and tracks key results |
| objective_strategist | Objective Strategist | Defines and aligns strategic objectives |
| opportunity_analyst | Opportunity Analyst | Evaluates market opportunities and solutions |
| product_marketing_manager | Product Marketing Manager | Manages product marketing and positioning |
| product_strategist | Product Strategist | Develops long-term product strategy |
| roadmapper | Roadmap Lead | Creates and maintains product roadmaps |

---

### Project Agent

**Role**: Senior Project Manager
**Description**: Orchestrates project planning, execution, and status reporting.
**Domain**: Project Planning & Execution

| Subagent | Role | Description |
|----------|------|-------------|
| project_analyst | Project Analyst | Analyzes project capacity and resources |
| project_planner | Project Planner | Creates project timelines and schedules |
| project_status_writer | Status Reporter | Generates project status reports |
| task_manager | Task Manager | Manages task assignments and tracking |

---

### Prompt Architect Agent

**Role**: Prompt Engineer
**Description**: Specializes in engineering and optimizing high-performance LLM prompts and agent behaviors.
**Domain**: Prompt Engineering & Optimization

| Subagent | Role | Description |
|----------|------|-------------|
| prompt_generator | Prompt Generator | Generates and iterates on prompt designs |
| roadmap_parser | Roadmap Parser | Parses roadmap documents for prompt context |
| spec_analyzer | Spec Analyzer | Analyzes specifications for prompt requirements |
| tool_matcher | Tool Matcher | Matches tasks to optimal tools and workflows |

---

### Public Relations Agent

**Role**: PR Director
**Description**: Manages external communication, press releases, and brand narrative.
**Domain**: PR & External Communications

| Subagent | Role | Description |
|----------|------|-------------|
| advertising_specialist | Advertising Specialist | Develops advertising campaigns and creative |
| press_release_writer | PR Writer | Writes press releases and media communications |

---

### Research Agent

**Role**: Research Lead
**Description**: Orchestrates user research, market analysis, and competitive intelligence.
**Domain**: User & Market Research

| Subagent | Role | Description |
|----------|------|-------------|
| competitive_intelligence_analyst | CI Analyst | Conducts competitive intelligence gathering |
| data_analyst | Research Data Analyst | Analyzes research datasets for insights |
| market_research_analyst | Market Researcher | Analyzes market trends and opportunities |
| qualitative_research_expert | Qualitative Researcher | Conducts qualitative research and synthesis |
| report_writer | Research Writer | Writes research reports and findings |
| survey_research_specialist | Survey Specialist | Designs and analyzes research surveys |
| user_research_specialist | User Researcher | Conducts user research and interviews |

---

### UX Agent

**Role**: Design Lead
**Description**: Orchestrates user experience design, usability testing, and visual interface development.
**Domain**: User Experience & Design

| Subagent | Role | Description |
|----------|------|-------------|
| accessibility_specialist | Accessibility Lead | Ensures WCAG compliance and accessibility |
| customer_journey_mapper | Journey Mapper | Maps customer journeys and touchpoints |
| diagram_designer | Diagram Designer | Creates UX diagrams and visual documentation |
| flow_architect | Flow Architect | Designs user flows and navigation structures |
| information_architect | IA Specialist | Designs information architecture and taxonomy |
| interaction_designer | Interaction Designer | Designs micro-interactions and behaviors |
| jtbd_researcher | JTBD Researcher | Conducts Jobs-to-be-Done research |
| metrics_analyst | UX Metrics Analyst | Analyzes UX metrics and conversion data |
| prototype_builder | Prototyper | Builds interactive prototypes |
| service_blueprinter | Service Designer | Creates service blueprints and designs |
| usability_tester | Usability Tester | Conducts usability testing sessions |
| user_persona_developer | Persona Developer | Develops user personas and segments |
| ux_strategist | UX Strategist | Develops UX strategy and vision |
| visual_designer | Visual Designer | Creates visual designs and UI components |
| wireframe_creator | Wireframe Designer | Designs low-fidelity wireframes |

---

## File Structure

```
agents/agent_definitions/
├── AGENT_TAXONOMY.md                    # This file
├── agent_instructions_format.md         # Instruction format documentation
├── agents_glossary/                     # Glossary and terminology
├── business_review_agent/
│   ├── business_review_agent_definition.yaml
│   └── subagents/
│       ├── business_review_agent_*_definition.yaml
├── cloud_agent/
│   ├── cloud_agent_definition.yaml
│   └── subagents/
├── content_agent/
│   ├── content_agent_definition.yaml
│   └── subagents/
├── context_agent/
│   ├── context_agent_definition.yaml
│   └── subagents/
├── education_agent/
│   ├── education_agent_definition.yaml
│   └── subagents/
├── engineering_agent/
│   ├── engineering_agent_definition.yaml
│   └── subagents/
├── google_apps_script_agent/
│   ├── google_apps_script_agent_definition.yaml
│   └── subagents/
├── model_orchestration_agent/
│   └── model_orchestration_agent_definition.yaml
├── product_agent/
│   ├── product_agent_definition.yaml
│   └── subagents/
├── product_management_agent/
│   ├── product_management_agent_definition.yaml
│   └── subagents/
├── project_agent/
│   ├── project_agent_definition.yaml
│   └── subagents/
├── prompt_architect_agent/
│   ├── prompt_architect_agent_definition.yaml
│   └── subagents/
├── public_relations_agent/
│   ├── public_relations_agent_definition.yaml
│   └── subagents/
├── research_agent/
│   ├── research_agent_definition.yaml
│   └── subagents/
└── ux_agent/
    ├── ux_agent_definition.yaml
    └── subagents/
```
