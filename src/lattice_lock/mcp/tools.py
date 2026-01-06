"""
Tool definitions for Lattice Lock MCP Server.
"""

import json
import logging
import subprocess
from pathlib import Path
from typing import Any

from lattice_lock.gauntlet.generator import GauntletGenerator
from lattice_lock.orchestrator.core import ModelOrchestrator
from lattice_lock.sheriff.sheriff import run_sheriff
from mcp.types import EmbeddedResource, ImageContent, TextContent, Tool

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


def _validate_safe_path(path_str: str) -> Path:
    """
    Validate that a path resolves to within the current working directory.
    Prevents path traversal attacks (e.g. ../../etc/passwd).
    """
    root = Path.cwd().resolve()
    target = (root / path_str).resolve()

    if not target.is_relative_to(root):
        raise ValueError(f"Path traversal detected: {path_str} must be relative to project root.")

    return target


async def handle_tool_call(
    name: str, arguments: dict[str, Any]
) -> list[TextContent | ImageContent | EmbeddedResource]:
    """Handle execution of tool calls."""

    if name == "validate_code":
        raw_path = arguments.get("path", ".")
        try:
            safe_path = _validate_safe_path(raw_path)
            result = run_sheriff(str(safe_path), json_output=True)
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
        raw_output_dir = arguments.get("output_dir", "tests/gauntlet")
        raw_lattice_file = arguments.get("lattice_file", "lattice.yaml")

        try:
            safe_output_dir = _validate_safe_path(raw_output_dir)
            safe_lattice_file = _validate_safe_path(raw_lattice_file)

            # 1. Generate
            generator = GauntletGenerator(
                lattice_file=str(safe_lattice_file), output_dir=str(safe_output_dir)
            )
            generator.generate()

            # 2. Run via pytest (subprocess to capture output)
            cmd = ["pytest", str(safe_output_dir), "--tb=short"]
            result = subprocess.run(cmd, capture_output=True, text=True)

            output = (
                f"Test Generation: Complete\n\nPytest Output:\n{result.stdout}\n{result.stderr}"
            )
            return [TextContent(type="text", text=output)]
        except Exception as e:
            return [TextContent(type="text", text=f"Error running tests: {e}")]

    else:
        raise ValueError(f"Unknown tool: {name}")
