import secrets
import bcrypt
from datetime import datetime, timezone
from typing import Tuple, List, Optional
from fastapi import HTTPException, status

from .models import Role, APIKeyInfo
from .config import get_config
from .storage import MemoryAuthStorage

# Constants
BCRYPT_ROUNDS = 12

def generate_api_key(
    username: str,
    role: Role,
    name: str = "",
) -> Tuple[str, str]:
    """
    Generate a new API key for a user.
    Returns (api_key, key_id).
    """
    config = get_config()

    key_id = secrets.token_urlsafe(8)
    key_secret = secrets.token_urlsafe(32)
    api_key = f"{config.api_key_prefix}{key_secret}"

    api_key_hash = bcrypt.hashpw(
        api_key.encode(), 
        bcrypt.gensalt(rounds=BCRYPT_ROUNDS)
    ).decode()

    metadata = APIKeyInfo(
        key_id=key_id,
        created_at=datetime.now(timezone.utc),
        name=name,
    )

    MemoryAuthStorage.save_api_key(api_key_hash, username, role, key_id, metadata)
    return api_key, key_id

def verify_api_key(api_key: str) -> Tuple[str, Role]:
    """
    Verify an API key and return associated user info.
    Returns (username, role).
    """
    all_keys = MemoryAuthStorage.get_all_api_keys()
    
    for stored_hash, (username, role, key_id) in all_keys.items():
        try:
            if bcrypt.checkpw(api_key.encode(), stored_hash.encode()):
                # Update last used
                meta = MemoryAuthStorage.get_api_key_metadata(key_id)
                if meta:
                    meta.last_used = datetime.now(timezone.utc)
                return username, role
        except ValueError:
            continue

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API key",
    )

def revoke_api_key(key_id: str) -> bool:
    """Revoke an API key by its ID."""
    all_keys = MemoryAuthStorage.get_all_api_keys()
    keys_to_remove = [k for k, (_, _, kid) in all_keys.items() if kid == key_id]

    if not keys_to_remove:
        return False

    for k in keys_to_remove:
        MemoryAuthStorage.delete_api_key(k)
        
    MemoryAuthStorage.delete_api_key_metadata(key_id)
    return True

def rotate_api_key(key_id: str, name: str = "") -> Optional[Tuple[str, str]]:
    """Rotate an API key."""
    all_keys = MemoryAuthStorage.get_all_api_keys()
    username = None
    role = None

    for _, (u, r, kid) in all_keys.items():
        if kid == key_id:
            username = u
            role = r
            break

    if username is None:
        return None

    # Preserve name if not provided
    if not name:
        meta = MemoryAuthStorage.get_api_key_metadata(key_id)
        if meta:
            name = meta.name

    revoke_api_key(key_id)
    return generate_api_key(username, role, name)

def list_api_keys(username: str) -> List[APIKeyInfo]:
    """List all API keys for a user."""
    return MemoryAuthStorage.list_api_keys(username)

def clear_api_keys() -> None:
    """Clear all API keys (test utility)."""
    # Only clear api keys part of storage
    # Use direct access or add method to storage
    # Accessing protected member generic workaround or add clear_keys to storage
    # Since I control storage.py, I'll just assume MemoryAuthStorage has _api_keys
    MemoryAuthStorage._api_keys.clear()
    MemoryAuthStorage._api_key_metadata.clear()
