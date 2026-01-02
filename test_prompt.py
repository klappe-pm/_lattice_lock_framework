import asyncio
import logging
import os
import sys

# Ensure src is in python path if running from root without install
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from lattice_lock import ModelOrchestrator
from lattice_lock.logging_config import setup_logging


async def main():
    # Setup logging to see what's happening
    setup_logging(level=logging.INFO, simple_format=True)
    setup_logging(level=logging.INFO, simple_format=True)

    print("🚀 Initializing Lattice Lock ModelOrchestrator...")
    try:
        orchestrator = ModelOrchestrator()
    except Exception as e:
        print(f"❌ Failed to initialize orchestrator: {e}")
        return

    # Check for API keys (simple check for common ones)
    if not os.environ.get("OPENAI_API_KEY") and not os.environ.get("ANTHROPIC_API_KEY"):
        print("⚠️  Warning: No OPENAI_API_KEY or ANTHROPIC_API_KEY found in environment.")
        print("   The test might fail if no providers are configured.")

    prompt = "Hello! Please briefly introduce yourself and tell me what year it is."
    print(f"\n📝 Sending prompt: '{prompt}'\n")

    try:
        response = await orchestrator.route_request(
            prompt=prompt,
            # You can force a model if you want, e.g., model_id="gpt-4o"
            # model_id="gpt-4o"
        )

        print("\n✅ Response Received:\n")
        print(f"Model: {response.model}")
        print("-" * 40)
        print(response.content)
        print("-" * 40)
        print(f"Usage: {response.usage}")

    except Exception as e:
        print(f"\n❌ Error during request: {e}")
    finally:
        await orchestrator.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
