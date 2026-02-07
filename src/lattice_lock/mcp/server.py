"""
MCP Server implementation for Lattice Lock.
"""

import logging
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import EmbeddedResource, GetPromptResult, ImageContent, Prompt, TextContent, Tool

from lattice_lock.config.feature_flags import Feature, is_feature_enabled
from lattice_lock.mcp.templates import GOVERNANCE_CHECK_PROMPT, MCP_PROMPTS
from lattice_lock.mcp.tools import get_tools, handle_tool_call

logger = logging.getLogger(__name__)


class LatticeMCPServer:
    """
    Model Context Protocol (MCP) Server for Lattice Lock.
    Exposes Sheriff, Gauntlet, and Orchestrator as tools.
    """

    def __init__(self, name: str = "lattice-lock"):
        self.server = Server(name)
        self._setup_handlers()

    def _setup_handlers(self):
        """Register MCP handlers."""

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            return get_tools()

        @self.server.call_tool()
        async def call_tool(
            name: str, arguments: dict[str, Any]
        ) -> list[TextContent | ImageContent | EmbeddedResource]:
            return await handle_tool_call(name, arguments)

        @self.server.list_prompts()
        async def list_prompts() -> list[Prompt]:
            return MCP_PROMPTS

        @self.server.get_prompt()
        async def get_prompt(name: str, arguments: dict[str, str] | None) -> GetPromptResult:
            # Simple retrieval for now
            # In a real implementation we would hydrate templates with arguments
            if name == "governance-check":
                return GetPromptResult(
                    description=GOVERNANCE_CHECK_PROMPT.description,
                    messages=[
                        TextContent(
                            type="text",
                            text=f"Check this code for governance violations:\n\n{arguments.get('code', '')}",
                        )
                    ],
                )
            # Fallback for others (stub)
            return GetPromptResult(description="Prompt template", messages=[])

    async def run_stdio(self):
        """Run the server using stdio transport."""
        if not is_feature_enabled(Feature.MCP):
            logger.error("MCP feature is disabled. Check LATTICE_DISABLED_FEATURES.")
            return

        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options(),
            )
