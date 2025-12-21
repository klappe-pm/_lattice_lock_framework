# Agent Definitions Inventory

**Last Updated**: December 20, 2025  
**Total Parent Agents**: 13  
**Total Subagents**: 56  
**Format**: Agent Definitions v2.1

---

## Parent Agents

| Agent Type | Type | Name | [[Name]] | Description |
|---|---|---|---|---|
| business_review_agent | agent | business_review_agent | [[business_review_agent]] | Analyzes business metrics, OKRs, and market intelligence. Primary interface for performance tracking, competitive analysis, and strategic reporting. |
| cloud_agent | agent | cloud_agent | [[cloud_agent]] | Manages cloud infrastructure across AWS, Azure, and Google Cloud. Provisions, manages, and optimizes cloud resources while ensuring security compliance. |
| content_agent | agent | content_agent | [[content_agent]] | Develops and manages content strategy, creation, and distribution. Creates high-quality, engaging content aligned with brand voice and SEO optimization. |
| context_agent | agent | context_agent | [[context_agent]] | Manages project context, memory, and knowledge retrieval. Ensures agents have access to relevant and up-to-date context through summarization and synthesis. |
| engineering_agent | agent | engineering_agent | [[engineering_agent]] | Orchestrates engineering tasks including coding, testing, and deployment. Manages the software development lifecycle and ensures high-quality code delivery. |
| google_apps_script_agent | agent | google_apps_script_agent | [[google_apps_script_agent]] | Develops, deploys, and manages Google Apps Script projects. Automates Google Workspace workflows with secure, optimized script execution. |
| model_orchestration_agent | agent | model_orchestration_agent | [[model_orchestration_agent]] | Intelligent router and manager for AI model selection, cost optimization, and performance tracking across 63 models and 8 providers. Chief Model Architect. |
| product_agent | agent | product_agent | [[product_agent]] | Orchestrates product management activities including strategy, requirements, and metrics. Defines and drives product strategy with roadmap and PRD generation. |
| project_agent | agent | project_agent | [[project_agent]] | Manages project timelines, tasks, and resources. Ensures project delivery on time and within scope through planning and risk management. |
| prompt_architect_agent | agent | prompt_architect_agent | [[prompt_architect_agent]] | Generates detailed LLM prompts for project phases based on specifications and roadmaps. Bridges gap between project planning and actionable agent prompts. |
| public_relations_agent | agent | public_relations_agent | [[public_relations_agent]] | Manages public communications and media relations. Maintains positive public image through press releases and media statement management. |
| research_agent | agent | research_agent | [[research_agent]] | Conducts market, user, and competitive research. Provides data-driven insights through research execution and analysis to support decision making. |
| ux_agent | agent | ux_agent | [[ux_agent]] | Designs user interfaces and experiences. Creates intuitive and accessible user experiences through wireframes, prototypes, and usability testing. |

---

## Business Review Agent Subagents

| Agent Type | Type | Name | [[Name]] | Description |
|---|---|---|---|---|
| business_review_agent | subagent | okr_tracker | [[okr_tracker]] | Tracks Objectives and Key Results. Monitors progress towards company goals and flags at-risk OKRs. |
| business_review_agent | subagent | competitive_intelligence_analyst | [[competitive_intelligence_analyst]] | Analyzes competitive landscape and market positioning. Provides intelligence on competitor activities and market trends. |
| business_review_agent | subagent | data_quality_manager | [[data_quality_manager]] | Ensures data integrity and quality across business metrics. Validates and cleans data for accurate reporting. |
| business_review_agent | subagent | financial_analyst | [[financial_analyst]] | Analyzes financial performance and metrics. Provides insights on revenue, costs, and profitability. |
| business_review_agent | subagent | performance_analyst | [[performance_analyst]] | Analyzes business performance metrics and KPIs. Tracks progress against targets and identifies optimization opportunities. |
| business_review_agent | subagent | process_improvement_specialist | [[process_improvement_specialist]] | Identifies and implements process improvements. Optimizes workflows and operational efficiency. |
| business_review_agent | subagent | reporting_automation_specialist | [[reporting_automation_specialist]] | Automates report generation and distribution. Creates and maintains automated reporting pipelines. |
| business_review_agent | subagent | risk_assessment_analyst | [[risk_assessment_analyst]] | Assesses and monitors business risks. Identifies risks and recommends mitigation strategies. |

---

## Cloud Agent Subagents

| Agent Type | Type | Name | [[Name]] | Description |
|---|---|---|---|---|
| cloud_agent | subagent | aws_agent | [[aws_agent]] | Manages AWS infrastructure and services. Handles EC2, S3, RDS, and other AWS resource provisioning and optimization. |
| cloud_agent | subagent | azure_agent | [[azure_agent]] | Manages Azure infrastructure and services. Handles VM, Storage, Database, and other Azure resource management. |
| cloud_agent | subagent | google_cloud_agent | [[google_cloud_agent]] | Manages Google Cloud infrastructure and services. Handles GCE, Cloud Storage, BigQuery, and other GCP resource management. |

---

## Content Agent Subagents

| Agent Type | Type | Name | [[Name]] | Description |
|---|---|---|---|---|
| content_agent | subagent | analyst | [[analyst]] | Analyzes content performance and audience engagement. Provides insights for content optimization and strategy refinement. |
| content_agent | subagent | editorial_manager | [[editorial_manager]] | Manages editorial calendar and content workflow. Coordinates content creation, review, and publication processes. |
| content_agent | subagent | email_marketing_specialist | [[email_marketing_specialist]] | Creates and manages email marketing campaigns. Develops email content strategies and executes campaign execution. |
| content_agent | subagent | localization_expert | [[localization_expert]] | Adapts content for different languages and markets. Ensures cultural relevance and proper localization. |
| content_agent | subagent | operations_specialist | [[operations_specialist]] | Manages content operations and distribution. Handles publishing, distribution, and technical content management. |
| content_agent | subagent | seo_specialist | [[seo_specialist]] | Optimizes content for search engines. Implements SEO best practices and manages keyword strategy. |
| content_agent | subagent | social_media_strategist | [[social_media_strategist]] | Develops and executes social media strategy. Creates content and manages social media presence across platforms. |
| content_agent | subagent | writer | [[writer]] | Creates high-quality written content. Produces engaging articles, copy, and other written materials. |

---

## Context Agent Subagents

| Agent Type | Type | Name | [[Name]] | Description |
|---|---|---|---|---|
| context_agent | subagent | chat_summary | [[chat_summary]] | Summarizes conversation history and extracts key points. Condenses discussions into actionable summaries. |
| context_agent | subagent | information_gatherer | [[information_gatherer]] | Collects and organizes relevant information. Gathers data from various sources for context building. |
| context_agent | subagent | knowledge_synthesizer | [[knowledge_synthesizer]] | Synthesizes disparate information into coherent knowledge. Creates connected knowledge graphs and understanding. |
| context_agent | subagent | llm_memory_specialist | [[llm_memory_specialist]] | Manages LLM-specific memory and token optimization. Optimizes memory usage for context windows. |
| context_agent | subagent | memory_storage | [[memory_storage]] | Handles memory persistence and retrieval. Manages storage of memory across sessions. |
| context_agent | subagent | validator | [[validator]] | Validates information accuracy and consistency. Ensures context quality and reliability. |

---

## Engineering Agent Subagents

| Agent Type | Type | Name | [[Name]] | Description |
|---|---|---|---|---|
| engineering_agent | subagent | api_designer | [[api_designer]] | Designs API specifications and interfaces. Creates RESTful and service definitions. |
| engineering_agent | subagent | backend_developer | [[backend_developer]] | Implements server-side logic and databases. Builds robust and scalable backend systems. |
| engineering_agent | subagent | database_administrator | [[database_administrator]] | Manages database design and optimization. Handles schema design, indexing, and performance tuning. |
| engineering_agent | subagent | devops_engineer | [[devops_engineer]] | Manages infrastructure and deployment automation. Handles CI/CD, containerization, and infrastructure as code. |
| engineering_agent | subagent | frontend_developer | [[frontend_developer]] | Builds user-facing interfaces and experiences. Implements responsive UI components and client-side logic. |
| engineering_agent | subagent | security_engineer | [[security_engineer]] | Implements security measures and best practices. Handles authentication, authorization, and security hardening. |
| engineering_agent | subagent | system_architect | [[system_architect]] | Designs system architecture and technical strategy. Creates scalable, maintainable system designs. |
| engineering_agent | subagent | testing_qa_specialist | [[testing_qa_specialist]] | Designs and executes testing strategies. Ensures quality through automated and manual testing. |

---

## Google Apps Script Agent Subagents

| Agent Type | Type | Name | [[Name]] | Description |
|---|---|---|---|---|
| google_apps_script_agent | subagent | script_architect | [[script_architect]] | Designs Google Apps Script architecture and solutions. Plans script structure and integration approach. |
| google_apps_script_agent | subagent | script_cost_analyzer | [[script_cost_analyzer]] | Analyzes execution cost of Apps Scripts. Optimizes for cost efficiency within quota limits. |
| google_apps_script_agent | subagent | script_deployer | [[script_deployer]] | Deploys and releases Google Apps Scripts. Manages deployment versions and rollbacks. |
| google_apps_script_agent | subagent | script_developer | [[script_developer]] | Develops Google Apps Script implementations. Writes and optimizes Apps Script code. |
| google_apps_script_agent | subagent | script_devtools_manager | [[script_devtools_manager]] | Manages Google Apps Script development tools. Handles IDE setup and debugging tools. |
| google_apps_script_agent | subagent | script_ide_handler | [[script_ide_handler]] | Manages Apps Script IDE operations. Handles editor functionality and development environment. |
| google_apps_script_agent | subagent | script_integrator | [[script_integrator]] | Integrates Apps Scripts with Google Workspace services. Connects scripts to Sheets, Docs, Gmail, etc. |
| google_apps_script_agent | subagent | script_tester | [[script_tester]] | Tests Google Apps Scripts for functionality and performance. Ensures script reliability and optimization. |

---

## Product Agent Subagents

| Agent Type | Type | Name | [[Name]] | Description |
|---|---|---|---|---|
| product_agent | subagent | business_analyst | [[business_analyst]] | Analyzes business requirements and opportunities. Translates business needs into product specifications. |
| product_agent | subagent | business_case_owner | [[business_case_owner]] | Develops and maintains business cases for initiatives. Justifies product investments with data and analysis. |
| product_agent | subagent | dashboard_designer | [[dashboard_designer]] | Designs dashboards and data visualizations. Creates metrics dashboards for stakeholder reporting. |
| product_agent | subagent | dashboard_requirements_writer | [[dashboard_requirements_writer]] | Writes requirements for dashboard development. Specifies dashboard structure and metrics. |
| product_agent | subagent | frameworks_designer | [[frameworks_designer]] | Designs product frameworks and methodologies. Creates systems for product development processes. |
| product_agent | subagent | internal_documentation_researcher | [[internal_documentation_researcher]] | Research internal documentation and knowledge. Gathers existing documentation and institutional knowledge. |
| product_agent | subagent | metrics_analyst | [[metrics_analyst]] | Analyzes product metrics and performance indicators. Interprets data to guide product decisions. |
| product_agent | subagent | metrics_researcher | [[metrics_researcher]] | Researches and defines appropriate metrics. Identifies key metrics for tracking product success. |
| product_agent | subagent | operations | [[operations]] | Manages product operations and processes. Handles product launch, feedback collection, and lifecycle. |
| product_agent | subagent | opportunity_solutions_tree_designer | [[opportunity_solutions_tree_designer]] | Designs opportunity-solution trees for discovery. Maps customer problems to potential solutions. |
| product_agent | subagent | strategist | [[strategist]] | Develops product strategy and vision. Creates long-term product direction and roadmap. |

---

## Project Agent Subagents

| Agent Type | Type | Name | [[Name]] | Description |
|---|---|---|---|---|
| project_agent | subagent | project_analyst | [[project_analyst]] | Analyzes project health and metrics. Provides insights on project status and performance. |
| project_agent | subagent | project_planner | [[project_planner]] | Plans project timelines and deliverables. Creates detailed project plans and schedules. |
| project_agent | subagent | project_status_writer | [[project_status_writer]] | Writes project status reports and updates. Communicates project progress to stakeholders. |
| project_agent | subagent | task_manager | [[task_manager]] | Manages tasks and assignments. Coordinates task assignment and tracking. |

---

## Prompt Architect Agent Subagents

| Agent Type | Type | Name | [[Name]] | Description |
|---|---|---|---|---|
| prompt_architect_agent | subagent | spec_analyzer | [[spec_analyzer]] | Analyzes project specifications and requirements. Extracts structured requirements from documentation. |
| prompt_architect_agent | subagent | roadmap_parser | [[roadmap_parser]] | Parses roadmaps and phase plans into task hierarchies. Decomposes phases into discrete assignable tasks. |
| prompt_architect_agent | subagent | prompt_generator | [[prompt_generator]] | Generates detailed LLM prompts with context and goals. Creates comprehensive prompts for agent execution. |
| prompt_architect_agent | subagent | tool_matcher | [[tool_matcher]] | Matches tasks to appropriate tools based on capabilities. Prevents file ownership conflicts and optimizes tool allocation. |

---

## Public Relations Agent Subagents

| Agent Type | Type | Name | [[Name]] | Description |
|---|---|---|---|---|
| public_relations_agent | subagent | press_release_writer | [[press_release_writer]] | Writes press releases and media statements. Creates professional communications for media distribution. |

---

## Research Agent Subagents

| Agent Type | Type | Name | [[Name]] | Description |
|---|---|---|---|---|
| research_agent | subagent | competitive_intelligence_analyst | [[competitive_intelligence_analyst]] | Analyzes competitive landscape and benchmarking. Provides intelligence on competitor strategies and offerings. |
| research_agent | subagent | data_analyst | [[data_analyst]] | Analyzes research data and generates insights. Interprets quantitative research findings. |
| research_agent | subagent | market_research_analyst | [[market_research_analyst]] | Conducts market research and analysis. Studies market size, trends, and opportunities. |
| research_agent | subagent | qualitative_research_expert | [[qualitative_research_expert]] | Conducts qualitative research and analysis. Performs interviews, focus groups, and ethnographic research. |
| research_agent | subagent | report_writer | [[report_writer]] | Writes research reports and documentation. Synthesizes research findings into comprehensive reports. |
| research_agent | subagent | survey_research_specialist | [[survey_research_specialist]] | Designs and executes survey research. Creates surveys and analyzes quantitative research data. |
| research_agent | subagent | user_research_specialist | [[user_research_specialist]] | Conducts user research and usability studies. Performs user testing and feedback collection. |

---

## UX Agent Subagents

| Agent Type | Type | Name | [[Name]] | Description |
|---|---|---|---|---|
| ux_agent | subagent | accessibility_specialist | [[accessibility_specialist]] | Ensures accessibility compliance and best practices. Makes designs inclusive for all users. |
| ux_agent | subagent | interaction_designer | [[interaction_designer]] | Designs interaction patterns and user flows. Creates intuitive interaction models and microinteractions. |
| ux_agent | subagent | metrics_analyst | [[metrics_analyst]] | Analyzes UX metrics and user behavior data. Measures design effectiveness through metrics and analytics. |
| ux_agent | subagent | prototype_builder | [[prototype_builder]] | Builds interactive prototypes and proof of concepts. Creates working prototypes for validation. |
| ux_agent | subagent | usability_tester | [[usability_tester]] | Conducts usability testing and user research. Tests designs with real users and gathers feedback. |
| ux_agent | subagent | user_persona_developer | [[user_persona_developer]] | Develops user personas and mental models. Creates detailed representations of target users. |
| ux_agent | subagent | visual_designer | [[visual_designer]] | Designs visual elements and branding. Creates visual designs and design systems. |
| ux_agent | subagent | wireframe_creator | [[wireframe_creator]] | Creates wireframes and layout designs. Designs screen layouts and information architecture. |

---

## Agent Distribution Summary

| Category | Count |
|---|---|
| Parent Agents | 13 |
| Subagents | 56 |
| Total Agents | 69 |

### Distribution by Domain

| Domain | Parent Agents | Subagents |
|---|---|---|
| Business & Analytics | 2 | 15 |
| Engineering & Development | 2 | 16 |
| Content & Communications | 2 | 9 |
| Infrastructure & Operations | 1 | 3 |
| Product & Strategy | 2 | 11 |
| Research & Data | 1 | 7 |
| Design & UX | 1 | 8 |
| System Management | 1 | 4 |
| Automation & Tools | 1 | 8 |
| Google Workspace | 1 | 8 |

---

## Notes

- All agents follow the Agent Specification v2.1 format
- Memory persistence references the Universal Memory Directive
- File paths and access controls are defined per agent
- Model selection strategies support both local and cloud-based providers
- Cost limits and estimation parameters are configurable per agent
- See `AGENT_DEFINITIONS_CRITIQUE.md` for improvement recommendations
