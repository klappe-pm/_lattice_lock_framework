import logging
from .models import User, Role
from .passwords import get_password_hash, verify_password
from .config import get_config
from .storage import MemoryAuthStorage

logger = logging.getLogger("lattice_lock.admin.auth.users")

def create_user(username: str, password: str, role: Role = Role.VIEWER) -> User:
    """Create a new user."""
    config = get_config()
    if MemoryAuthStorage.get_user(username):
        raise ValueError(f"User {username} already exists")
        
    if len(password) < config.password_min_length:
        raise ValueError(f"Password must be at least {config.password_min_length} characters")
        
    hashed = get_password_hash(password)
    user = User(
        username=username, 
        hashed_password=hashed, 
        role=role
    )
    MemoryAuthStorage.save_user(user)
    logger.info("User created: %s with role %s", username, role.value)
    return user

def get_user(username: str) -> User | None:
    """Get a user by username."""
    return MemoryAuthStorage.get_user(username)

def delete_user(username: str) -> bool:
    """Delete a user."""
    success = MemoryAuthStorage.delete_user(username)
    if success:
        logger.info("User deleted: %s", username)
    return success

def clear_users() -> None:
    """Clear all users (test utility)."""
    MemoryAuthStorage._users.clear()

def authenticate_user(username: str, password: str) -> User | None:
    """Authenticate a user."""
    user = get_user(username)
    
    # Constant time dummy check to prevent timing attacks
    dummy_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.VTtYA/ICNVu5xO"
    hash_to_verify = user.hashed_password if user else dummy_hash
    
    password_valid = verify_password(password, hash_to_verify)
    
    if user is None or user.disabled or not password_valid:
        return None
        
    return user
