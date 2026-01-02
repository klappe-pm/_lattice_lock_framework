import asyncio
import logging
import os
import sys

# Ensure src is in python path if running from root without install
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from lattice_lock import ModelOrchestrator
from lattice_lock.logging_config import setup_logging


class ChatSession:
    """
    Manages a multi-turn conversation session with the Lattice Lock Orchestrator.
    """

    def __init__(self, system_prompt: str | None = None):
        self.orchestrator = ModelOrchestrator()
        self.history: list[dict[str, str]] = []
        if system_prompt:
            self.history.append({"role": "system", "content": system_prompt})

    async def chat(self, user_input: str, model_id: str | None = None) -> str:
        """
        Sends a message to the orchestrator, maintaining context.
        """
        # 1. Update history with user message
        self.history.append({"role": "user", "content": user_input})

        print(f"\n👤 User: {user_input}")

        # 2. Route request passing the full history
        # Note: We pass the last user input as 'prompt' for analysis,
        # but the 'messages' kwarg contains the full context for execution.
        response = await self.orchestrator.route_request(
            prompt=user_input,
            messages=self.history,  # Pass history to maintain context
            model_id=model_id,
        )

        # 3. Update history with assistant response
        self.history.append({"role": "assistant", "content": response.content})

        print(f"🤖 Assistant ({response.model}): {response.content}")
        return response.content

    async def close(self):
        await self.orchestrator.shutdown()


async def main():
    setup_logging(level=logging.WARNING, simple_format=True)

    # Initialize session
    print("🚀 Starting Multi-turn Chat Session...")
    session = ChatSession(system_prompt="You are a helpful and concise assistant.")

    try:
        # Turn 1: Establish context
        await session.chat("Hi, my name is Kevin.")

        # Turn 2: Verify context retention
        await session.chat("What is my name?")

        # Turn 3: Follow-up
        await session.chat("What is 2 + 2?")

    finally:
        await session.close()


if __name__ == "__main__":
    asyncio.run(main())
