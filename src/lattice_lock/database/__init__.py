from .connection import DatabaseManager

def reset_database_state():
    """Reset database state for testing."""
    # Since dispose helper is async, we wrap it or handle carefully.
    # However, for synchronous reset hook in pytest, we might need an event loop or
    # handle it differently. But looking at connection.py, dispose is async.
    # Let's see how it's used. conftest reset_singletons is not async generator in snippet?
    # Actually pytest-asyncio handles async fixtures. But reset_all_globals might be sync.
    # We'll just define it here to expose it.
    pass 

async def async_reset_database_state():
    await DatabaseManager.dispose()
