from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field

class Role(str, Enum):
    """User roles for role-based access control."""
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"

    @property
    def permissions(self) -> set[str]:
        """Get permissions associated with this role."""
        base_permissions = {"read:health", "read:projects", "read:errors"}

        if self == Role.ADMIN:
            return base_permissions | {
                "write:projects",
                "write:rollback",
                "write:config",
                "manage:users",
                "manage:api_keys",
            }
        elif self == Role.OPERATOR:
            return base_permissions | {"write:rollback"}
        else:  # VIEWER
            return base_permissions

class TokenData(BaseModel):
    sub: str
    role: Role
    exp: datetime
    iat: datetime
    jti: str
    token_type: str = "access"

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int

class APIKeyInfo(BaseModel):
    key_id: str
    created_at: datetime
    last_used: Optional[datetime] = None
    name: str = ""

class UserBase(BaseModel):
    username: str
    role: Role = Role.VIEWER
    disabled: bool = False

class User(UserBase):
    hashed_password: str
    api_keys: List[str] = Field(default_factory=list)

class LoginRequest(BaseModel):
    username: str
    password: str
