"""
Standard MCP Prompt Templates for Lattice Lock.
"""

from mcp.types import Prompt, PromptArgument

GOVERNANCE_CHECK_PROMPT = Prompt(
    name="governance-check",
    description="Analyze code for governance violations using Lattice Lock rules.",
    arguments=[
        PromptArgument(name="code", description="The code snippet to analyze", required=True),
        PromptArgument(name="context", description="Additional project context", required=False),
    ],
)

CODE_REVIEW_PROMPT = Prompt(
    name="code-review",
    description="Perform a comprehensive code review focusing on security, performance, and architecture.",
    arguments=[
        PromptArgument(
            name="file_content", description="Content of the file to review", required=True
        ),
        PromptArgument(
            name="file_path", description="Path of the file (for context)", required=True
        ),
    ],
)

TEST_GENERATION_PROMPT = Prompt(
    name="generate-tests",
    description="Generate pytest cases for the provided code.",
    arguments=[
        PromptArgument(name="code", description="The code to generate tests for", required=True),
    ],
)

MCP_PROMPTS = [GOVERNANCE_CHECK_PROMPT, CODE_REVIEW_PROMPT, TEST_GENERATION_PROMPT]
