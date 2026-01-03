import bcrypt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.

    Args:
        plain_password: The user input password.
        hashed_password: The stored hashed password (bcrypt prefix).
    """
    if not plain_password or not hashed_password:
        return False

    try:
        # bcrypt requires bytes
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.

    Returns:
        String representation of the hash.
    """
    # gensalt() generates a salt
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")
