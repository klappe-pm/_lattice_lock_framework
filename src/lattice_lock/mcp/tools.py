"""
Tool definitions for Lattice Lock MCP Server.
"""

import json
import logging
import subprocess
from typing import Any

from mcp.types import EmbeddedResource, ImageContent, TextContent, Tool

from lattice_lock.gauntlet.generator import GauntletGenerator
from lattice_lock.orchestrator.core import ModelOrchestrator
from lattice_lock.sheriff.sheriff import run_sheriff

logger = logging.getLogger(__name__)


def get_tools() -> list[Tool]:
    """Return list of available MCP tools."""
    return [
        Tool(
            name="validate_code",
            description="Run Sheriff static analysis to validate code against governance rules.",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File or directory path to validate"}
                },
                "required": ["path"],
            },
        ),
        Tool(
            name="ask_orchestrator",
            description="Ask the Lattice Lock Orchestrator a question (routes to best model).",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "The question or prompt to process",
                    },
                    "model_id": {
                        "type": "string",
                        "description": "Optional specific model ID to use",
                    },
                },
                "required": ["prompt"],
            },
        ),
        Tool(
            name="run_tests",
            description="Run Gauntlet tests (generates them first if needed).",
            inputSchema={
                "type": "object",
                "properties": {
                    "output_dir": {
                        "type": "string",
                        "description": "Directory to output/run tests (default: tests/gauntlet)",
                    },
                    "lattice_file": {
                        "type": "string",
                        "description": "Path to lattice.yaml (default: lattice.yaml)",
                    },
                },
            },
        ),
    ]


async def handle_tool_call(
    name: str, arguments: dict[str, Any]
) -> list[TextContent | ImageContent | EmbeddedResource]:
    """Handle execution of tool calls."""

    if name == "validate_code":
        path = arguments.get("path", ".")
        try:
            result = run_sheriff(path, json_output=True)
            # Serialize result
            json_str = json.dumps(result.to_dict(), indent=2)
            return [TextContent(type="text", text=json_str)]
        except Exception as e:
            return [TextContent(type="text", text=f"Error running Sheriff: {e}")]

    elif name == "ask_orchestrator":
        prompt = arguments.get("prompt")
        model_id = arguments.get("model_id")

        try:
            orchestrator = ModelOrchestrator()
            response = await orchestrator.route_request(prompt, model_id=model_id)
            return [TextContent(type="text", text=response.content)]
        except Exception as e:
            return [TextContent(type="text", text=f"Error processing request: {e}")]

    elif name == "run_tests":
        output_dir = arguments.get("output_dir", "tests/gauntlet")
        lattice_file = arguments.get("lattice_file", "lattice.yaml")

        try:
            # 1. Generate
            generator = GauntletGenerator(lattice_file=lattice_file, output_dir=output_dir)
            generator.generate()

            # 2. Run via pytest (subprocess to capture output)
            cmd = ["pytest", output_dir, "--tb=short"]
            result = subprocess.run(cmd, capture_output=True, text=True)

            output = (
                f"Test Generation: Complete\n\nPytest Output:\n{result.stdout}\n{result.stderr}"
            )
            return [TextContent(type="text", text=output)]
        except Exception as e:
            return [TextContent(type="text", text=f"Error running tests: {e}")]

    else:
        raise ValueError(f"Unknown tool: {name}")
