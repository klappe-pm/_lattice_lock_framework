import logging
import os
from datetime import datetime
from typing import Any

import aiofiles
import yaml
from pydantic import BaseModel, Field

from lattice_lock.utils.jinja import create_template
from lattice_lock.utils.safe_path import resolve_under_root
from lattice_lock_agents.prompt_architect.subagents.tool_profiles import ToolAssignment
from lattice_lock_agents.prompt_architect.tracker_client import TrackerClient
from lattice_lock_agents.prompt_architect.validators import (
    ConventionChecker,
    ConventionResult,
    PromptValidator,
    QualityScore,
    QualityScorer,
    ValidationResult,
)
from lattice_lock_orchestrator.api_clients import get_api_client

logger = logging.getLogger(__name__)


class GeneratedPrompt(BaseModel):
    prompt_id: str
    file_path: str
    content: str
    sections: dict[str, Any]
    metadata: dict[str, Any] = Field(default_factory=dict)
    validation_result: dict[str, Any] | None = None
    convention_result: dict[str, Any] | None = None
    quality_score: dict[str, Any] | None = None


class PromptGenerator:
    # Default configuration for validation
    DEFAULT_QUALITY_THRESHOLD = 6.0
    DEFAULT_MAX_RETRIES = 3

    def __init__(
        self,
        config_path: str = "agent_definitions/prompt_architect_agent/subagents/prompt_generator.yaml",
    ):
        self.config = self._load_config(config_path)
        self.template_path = os.path.join(
            os.path.dirname(__file__), "templates", "prompt_template.md"
        )
        self.prompts_dir = "project_prompts"
        self.state_file = os.path.join(self.prompts_dir, "project_prompts_state.json")

        # Initialize TrackerClient for state management
        self.tracker_client = TrackerClient()

        # Initialize LLM client
        model_config = self.config.get("agent", {}).get("model_selection", {})
        self.provider = model_config.get("default_provider", "local")
        self.model = model_config.get("default_model", "codellama:34b")
        self.client = get_api_client(self.provider)

        # Initialize validators
        validation_config = self.config.get("validation", {})
        self.quality_threshold = validation_config.get(
            "quality_threshold", self.DEFAULT_QUALITY_THRESHOLD
        )
        self.max_retries = validation_config.get("max_retries", self.DEFAULT_MAX_RETRIES)
        self.validate_before_write = validation_config.get("validate_before_write", True)

        self.prompt_validator = PromptValidator(strict_mode=False)
        self.convention_checker = ConventionChecker(prompts_root=self.prompts_dir)
        self.quality_scorer = QualityScorer(
            threshold=self.quality_threshold,
            use_llm=validation_config.get("use_llm_scoring", False),
            llm_client=self.client if validation_config.get("use_llm_scoring", False) else None,
            model=self.model,
        )

    def _load_config(self, path: str) -> dict[str, Any]:
        try:
            path = str(resolve_under_root(os.getcwd(), path))
        except ValueError:
            # Try absolute if getting from home/root? No, keeping strict to current dir for now for config
            # Or fall back if it exists?
            # Existing logic had explicit check.
            pass
        
        if not os.path.exists(path):
            # Fallback for testing or if path is relative to project root
            # resolve_under_root handles the joining, so if we are here it failed or doesn't exist
            # Let's try to resolve again if it wasn't resolved successfully above?
            # Actually, let's keep it simple: assume path is relative to cwd if not absolute
             pass

        if not os.path.exists(path):
             logger.warning(f"Config file not found at {path}, using defaults")
             return {}

        with open(path) as f:
            return yaml.safe_load(f)

    async def _load_template(self) -> str:
        if os.path.exists(self.template_path):
            async with aiofiles.open(self.template_path) as f:
                return await f.read()
        return ""

    async def generate(
        self, assignment: ToolAssignment, context_data: dict[str, Any]
    ) -> GeneratedPrompt:
        """
        Generate a detailed prompt based on the tool assignment and context.
        """
        template_content = await self._load_template()
        if not template_content:
            raise ValueError("Prompt template not found")

        # Extract basic info
        task_id = assignment.task_id
        tool_name = assignment.tool

        # Parse task_id to get phase, epic, task numbers
        # Assuming task_id format like "1.1.1" or "5.3.2"
        parts = task_id.split(".")
        phase_number = parts[0] if len(parts) > 0 else "0"
        epic_id = f"{parts[0]}.{parts[1]}" if len(parts) > 1 else "0.0"

        # Get names from context or assignment (placeholders for now if not available)
        epic_name = context_data.get("epic_name", "Unknown Epic")
        phase_name = context_data.get("phase_name", "Unknown Phase")
        task_title = context_data.get("task_title", "Unknown Task")

        # Generate sections
        context_text = await self._generate_context(assignment, context_data)
        goal_text = await self._generate_goal(assignment, context_data)
        steps_text = await self._generate_steps(assignment, context_data)
        do_not_touch_text = await self._generate_constraints(assignment, context_data)
        success_criteria_text = await self._generate_success_criteria(assignment, context_data)
        notes_text = await self._generate_notes(assignment, context_data)

        # Prepare template variables
        variables = {
            "prompt_id": task_id,
            "title": task_title,
            "tool_name": tool_name,
            "epic_id": epic_id,
            "epic_name": epic_name,
            "phase_number": phase_number,
            "phase_name": phase_name,
            "context": context_text,
            "goal": goal_text,
            "steps": steps_text,
            "do_not_touch": do_not_touch_text,
            "success_criteria": success_criteria_text,
            "notes": notes_text,
        }

        # Render template
        template = create_template(template_content)
        rendered_content = template.render(**variables)

        # Determine file path
        # Format: {phase}.{epic}.{task}_{tool}.md
        # Example: 5.3.2_codex_prompt_generator_impl.md
        # We need a clean task name for the filename
        clean_title = task_title.lower().replace(" ", "_").replace("-", "_")
        filename = f"{task_id}_{tool_name.lower()}_{clean_title}.md"

        # Determine phase directory
        _phase_dir_name = (
            f"phase{phase_number}_automation"  # Reserved for dynamic phase directory naming
        )
        # For now, we try to find the directory or create a generic one
        # In a real implementation, we'd map phase number to directory name
        # We'll use a simple mapping or search
        phase_dir = self._find_phase_directory(phase_number)
        file_path = os.path.join(self.prompts_dir, phase_dir, filename)

        # Create GeneratedPrompt object
        prompt = GeneratedPrompt(
            prompt_id=task_id,
            file_path=file_path,
            content=rendered_content,
            sections=variables,
            metadata={
                "generated_at": datetime.now().isoformat(),
                "model": self.model,
                "assignment": assignment.model_dump(),
            },
        )

        # Validate before writing if enabled
        if self.validate_before_write:
            validation_passed, prompt = await self._validate_and_retry(
                prompt, assignment, context_data
            )
            if not validation_passed:
                logger.warning(
                    f"Prompt {task_id} generated with validation warnings. "
                    "Review validation_result and quality_score in metadata."
                )

        # Write to file and update state (which also regenerates tracker markdown)
        await self._write_prompt_file(prompt)
        self._update_state(prompt, context_data)

        return prompt

    async def _validate_and_retry(
        self, prompt: GeneratedPrompt, assignment: ToolAssignment, context_data: dict[str, Any]
    ) -> tuple[bool, GeneratedPrompt]:
        """
        Validate prompt and retry generation if validation fails.

        Args:
            prompt: The generated prompt to validate
            assignment: The tool assignment
            context_data: Context data for regeneration

        Returns:
            Tuple of (validation_passed, possibly_updated_prompt)
        """
        for attempt in range(self.max_retries):
            # Run all validations
            validation_result = self.prompt_validator.validate_content(
                prompt.content, prompt.prompt_id
            )
            convention_result = self.convention_checker.check_filename(
                os.path.basename(prompt.file_path)
            )
            quality_score = await self.quality_scorer.score_content(
                prompt.content, prompt.prompt_id
            )

            # Store results in prompt metadata
            prompt.validation_result = validation_result.model_dump()
            prompt.convention_result = convention_result.model_dump()
            prompt.quality_score = quality_score.model_dump()

            # Log validation results
            self._log_validation_results(
                prompt.prompt_id, validation_result, convention_result, quality_score
            )

            # Check if validation passed
            all_valid = (
                validation_result.is_valid
                and convention_result.is_valid
                and quality_score.passes_threshold
            )

            if all_valid:
                logger.info(f"Prompt {prompt.prompt_id} passed all validations")
                return True, prompt

            # If not the last attempt, try to regenerate with feedback
            if attempt < self.max_retries - 1:
                logger.info(
                    f"Prompt {prompt.prompt_id} failed validation (attempt {attempt + 1}), "
                    "regenerating with feedback..."
                )
                prompt = await self._regenerate_with_feedback(
                    prompt, assignment, context_data, validation_result, quality_score
                )
            else:
                logger.warning(
                    f"Prompt {prompt.prompt_id} failed validation after {self.max_retries} attempts"
                )

        return False, prompt

    async def _regenerate_with_feedback(
        self,
        prompt: GeneratedPrompt,
        assignment: ToolAssignment,
        context_data: dict[str, Any],
        validation_result: ValidationResult,
        quality_score: QualityScore,
    ) -> GeneratedPrompt:
        """
        Regenerate prompt sections based on validation feedback.

        Args:
            prompt: The original prompt
            assignment: The tool assignment
            context_data: Original context data
            validation_result: Validation results with errors
            quality_score: Quality scoring results

        Returns:
            Regenerated prompt
        """
        # Collect feedback for regeneration
        feedback = []
        if validation_result.errors:
            feedback.extend(validation_result.errors)
        if validation_result.warnings:
            feedback.extend(validation_result.warnings)
        if quality_score.feedback:
            feedback.extend(quality_score.feedback)
        if quality_score.suggestions:
            feedback.extend(quality_score.suggestions)

        # Add feedback to context for regeneration
        enhanced_context = dict(context_data)
        enhanced_context["regeneration_feedback"] = feedback
        enhanced_context["previous_content"] = prompt.content

        # Regenerate sections that need improvement
        variables = dict(prompt.sections)

        # If steps had issues, regenerate them
        if quality_score.actionability_score < 6:
            variables["steps"] = await self._generate_steps_with_feedback(
                assignment, enhanced_context, feedback
            )

        # If context was unclear, enhance it
        if quality_score.clarity_score < 6:
            variables["context"] = await self._enhance_context(assignment, enhanced_context)

        # Re-render template
        template_content = await self._load_template()
        template = create_template(template_content)
        rendered_content = template.render(**variables)

        # Create new prompt
        return GeneratedPrompt(
            prompt_id=prompt.prompt_id,
            file_path=prompt.file_path,
            content=rendered_content,
            sections=variables,
            metadata={
                **prompt.metadata,
                "regenerated_at": datetime.now().isoformat(),
                "regeneration_feedback": feedback,
            },
        )

    async def _generate_steps_with_feedback(
        self, assignment: ToolAssignment, context_data: dict[str, Any], feedback: list[str]
    ) -> str:
        """Generate steps with validation feedback incorporated."""
        feedback_text = "\n".join(f"- {f}" for f in feedback)
        llm_prompt = f"""
Generate 4-8 specific, actionable steps for the following task.

Task: {context_data.get('task_title')}
Description: {context_data.get('task_description', '')}
Tool: {assignment.tool}
Files: {', '.join(assignment.files_owned)}

Previous issues to address:
{feedback_text}

Requirements:
- Each step should start with an action verb (Create, Implement, Add, Update, etc.)
- Each step should be specific and measurable
- Include file paths or function names where relevant
- Aim for 4-8 steps total

Format as a numbered list.
"""
        try:
            response = await self.client.chat_completion(
                model=self.model,
                messages=[{"role": "user", "content": llm_prompt}],
                temperature=0.5,  # Lower temperature for more focused output
            )
            return response.content or await self._generate_steps(assignment, context_data)
        except Exception as e:
            logger.error(f"Failed to regenerate steps: {e}")
            return await self._generate_steps(assignment, context_data)

    async def _enhance_context(
        self, assignment: ToolAssignment, context_data: dict[str, Any]
    ) -> str:
        """Enhance the context section for clarity."""
        original_context = context_data.get("context", "")
        llm_prompt = f"""
Enhance the following context section for a development prompt.

Original context:
{original_context}

Task: {context_data.get('task_title')}
Tool: {assignment.tool}
Files: {', '.join(assignment.files_owned)}

Requirements:
- Reference specific files or directories using backticks
- Explain the current state and what needs to change
- Be concise but complete (2-4 sentences)

Return only the enhanced context text.
"""
        try:
            response = await self.client.chat_completion(
                model=self.model,
                messages=[{"role": "user", "content": llm_prompt}],
                temperature=0.5,
            )
            return response.content or original_context
        except Exception as e:
            logger.error(f"Failed to enhance context: {e}")
            return original_context

    def _log_validation_results(
        self,
        prompt_id: str,
        validation_result: ValidationResult,
        convention_result: ConventionResult,
        quality_score: QualityScore,
    ) -> None:
        """Log validation results for visibility."""
        logger.info(f"Validation results for {prompt_id}:")
        logger.info(f"  Structure valid: {validation_result.is_valid}")
        logger.info(f"  Convention valid: {convention_result.is_valid}")
        logger.info(
            f"  Quality score: {quality_score.overall_score:.1f}/10 "
            f"(threshold: {self.quality_threshold})"
        )

        if validation_result.errors:
            for error in validation_result.errors:
                logger.warning(f"  Validation error: {error}")

        if convention_result.errors:
            for error in convention_result.errors:
                logger.warning(f"  Convention error: {error}")

        if quality_score.feedback:
            for fb in quality_score.feedback:
                logger.info(f"  Quality feedback: {fb}")

    async def _generate_context(
        self, assignment: ToolAssignment, context_data: dict[str, Any]
    ) -> str:
        # In a real implementation, this would call the LLM with specific context
        # For now, we return the provided context or a placeholder
        return context_data.get("context", "Context not provided.")

    async def _generate_goal(self, assignment: ToolAssignment, context_data: dict[str, Any]) -> str:
        return context_data.get("goal", "Goal not provided.")

    async def _generate_steps(
        self, assignment: ToolAssignment, context_data: dict[str, Any]
    ) -> str:
        # Use LLM to generate steps
        prompt = f"""
        Generate 4-8 specific, actionable steps for the following task:
        Task: {context_data.get('task_title')}
        Description: {context_data.get('task_description', '')}
        Tool: {assignment.tool}
        Files: {', '.join(assignment.files_owned)}

        Format as a numbered list.
        """

        try:
            response = await self.client.chat_completion(
                model=self.model, messages=[{"role": "user", "content": prompt}], temperature=0.7
            )
            return (
                response.content
                or "1. Analyze requirements\n2. Implement changes\n3. Verify implementation"
            )
        except Exception as e:
            logger.error(f"Failed to generate steps: {e}")
            return "1. Analyze requirements\n2. Implement changes\n3. Verify implementation"

    async def _generate_constraints(
        self, assignment: ToolAssignment, context_data: dict[str, Any]
    ) -> str:
        # Default constraints + specific ones
        constraints = [
            "- Existing prompt files in `project_prompts/`",
            "- `src/lattice_lock_cli/` (owned by Claude Code CLI)",
        ]
        return "\n".join(constraints)

    async def _generate_success_criteria(
        self, assignment: ToolAssignment, context_data: dict[str, Any]
    ) -> str:
        return "- Code compiles and runs\n- Tests pass"

    async def _generate_notes(
        self, assignment: ToolAssignment, context_data: dict[str, Any]
    ) -> str:
        return "- Follow the guardrails in prompt_generator.yaml"

    def _find_phase_directory(self, phase_number: str) -> str:
        # Simple heuristic to find existing phase directory
        if not os.path.exists(self.prompts_dir):
            return "phase" + phase_number

        for d in os.listdir(self.prompts_dir):
            if d.startswith(f"phase{phase_number}") and os.path.isdir(
                os.path.join(self.prompts_dir, d)
            ):
                return d
        return f"phase{phase_number}_generic"

    async def _write_prompt_file(self, prompt: GeneratedPrompt):
        os.makedirs(os.path.dirname(prompt.file_path), exist_ok=True)
        async with aiofiles.open(prompt.file_path, "w") as f:
            await f.write(prompt.content)
        logger.info(f"Generated prompt written to {prompt.file_path}")

    def _update_state(self, prompt: GeneratedPrompt, context_data: dict[str, Any]):
        """
        Update the tracker state with the newly generated prompt.

        Uses TrackerClient to add the prompt to the tracking system,
        which automatically regenerates the markdown tracker.

        Args:
            prompt: The generated prompt object.
            context_data: Context data containing title and other metadata.
        """
        # Extract tool from the assignment metadata
        assignment = prompt.metadata.get("assignment", {})
        tool = assignment.get("tool", "unknown")

        # Compute relative file path within project_prompts/
        # file_path is like "project_prompts/phase5_prompt_automation/5.4.1_claude_app_tracker.md"
        # We need just "phase5_prompt_automation/5.4.1_claude_app_tracker.md"
        file_path = prompt.file_path
        if file_path.startswith(self.prompts_dir):
            file_path = file_path[len(self.prompts_dir) :].lstrip("/\\")

        try:
            # Check if prompt already exists in tracker
            existing = self.tracker_client.get_prompt(prompt.prompt_id)
            if existing:
                logger.info(f"Prompt {prompt.prompt_id} already exists in tracker, skipping add")
                return

            # Add prompt to tracker
            result = self.tracker_client.add_prompt(
                prompt_id=prompt.prompt_id,
                title=context_data.get("task_title", prompt.sections.get("title", "Untitled")),
                tool=tool,
                file_path=file_path,
            )
            logger.info(f"Added prompt {prompt.prompt_id} to tracker: {result}")
        except ValueError as e:
            # Prompt may already exist, log and continue
            logger.warning(f"Could not add prompt to tracker: {e}")
        except Exception as e:
            logger.error(f"Failed to update tracker state: {e}")
            raise
