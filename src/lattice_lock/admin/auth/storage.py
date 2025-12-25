from typing import Dict, Set, Tuple, Optional, List
from .models import User, APIKeyInfo, Role

class MemoryAuthStorage:
    """In-memory storage for authentication data (users, tokens, keys)."""
    
    _users: Dict[str, User] = {}
    _revoked_tokens: Set[str] = set()
    _api_keys: Dict[str, Tuple[str, Role, str]] = {}  # hash -> (username, role, key_id)
    _api_key_metadata: Dict[str, APIKeyInfo] = {}  # key_id -> metadata
    
    @classmethod
    def get_user(cls, username: str) -> Optional[User]:
        return cls._users.get(username)
        
    @classmethod
    def save_user(cls, user: User):
        cls._users[user.username] = user
        
    @classmethod
    def delete_user(cls, username: str) -> bool:
        if username in cls._users:
            del cls._users[username]
            return True
        return False
    
    @classmethod
    def get_all_users(cls) -> List[User]:
        return list(cls._users.values())
        
    @classmethod
    def revoke_token(cls, jti: str):
        cls._revoked_tokens.add(jti)
        
    @classmethod
    def is_token_revoked(cls, jti: str) -> bool:
        return jti in cls._revoked_tokens
        
    @classmethod
    def save_api_key(cls, key_hash: str, username: str, role: Role, key_id: str, metadata: APIKeyInfo):
        cls._api_keys[key_hash] = (username, role, key_id)
        cls._api_key_metadata[key_id] = metadata
        
    @classmethod
    def get_all_api_keys(cls) -> Dict[str, Tuple[str, Role, str]]:
        return cls._api_keys

    @classmethod
    def get_api_key_metadata(cls, key_id: str) -> Optional[APIKeyInfo]:
        return cls._api_key_metadata.get(key_id)

    @classmethod
    def delete_api_key(cls, key_hash: str) -> None:
        if key_hash in cls._api_keys:
             del cls._api_keys[key_hash]

    @classmethod
    def delete_api_key_metadata(cls, key_id: str) -> None:
         if key_id in cls._api_key_metadata:
             del cls._api_key_metadata[key_id]
             
    @classmethod
    def clear(cls):
        """Reset all storage."""
        cls._users.clear()
        cls._revoked_tokens.clear()
        cls._api_keys.clear()
        cls._api_key_metadata.clear()
