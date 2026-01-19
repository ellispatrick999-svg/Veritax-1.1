import time
import uuid
from typing import List, Optional, Set

import jwt
from fastapi import Depends, HTTPException, Request, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader

from settings import (
    TOKEN_EXPIRATION_SECONDS,
    REQUIRE_AUTHENTICATION,
    ENVIRONMENT,
)
from exceptions import ValidationError, ComplianceError


# =====================
# Security Constants
# =====================

JWT_SECRET = "CHANGE_ME_IN_PROD"  # must come from env in prod
JWT_ALGORITHM = "HS256"

security = HTTPBearer()
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


# =====================
# Data Models
# =====================

class AuthenticatedUser:
    def __init__(
        self,
        user_id: str,
        roles: Set[str],
        scopes: Set[str],
        session_expires_at: float,
        is_partner: bool = False,
    ):
        self.user_id = user_id
        self.roles = roles
        self.scopes = scopes
        self.session_expires_at = session_expires_at
        self.is_partner = is_partner


# =====================
# Token Utilities
# =====================

def create_access_token(
    user_id: str,
    roles: Set[str],
    scopes: Set[str],
) -> str:
    payload = {
        "sub": user_id,
        "roles": list(roles),
        "scopes": list(scopes),
        "exp": int(time.time()) + TOKEN_EXPIRATION_SECONDS,
        "iat": int(time.time()),
        "jti": str(uuid.uuid4()),
        "type": "access",
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def create_refresh_token(user_id: str) -> str:
    payload = {
        "sub": user_id,
        "exp": int(time.time()) + (TOKEN_EXPIRATION_SECONDS * 24),
        "type": "refresh",
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


# =====================
# Session Enforcement
# =====================

def enforce_session_expiration(user: AuthenticatedUser):
    if time.time() > user.session_expires_at:
        raise HTTPException(status_code=401, detail="Session expired")


# =====================
# RBAC (Role-Based Access)
# =====================

def require_roles(allowed_roles: Set[str]):
    def checker(user: AuthenticatedUser = Depends(get_current_user)):
        if not user.roles.intersection(allowed_roles):
            raise HTTPException(status_code=403, detail="Insufficient role")
        return user
    return checker


# =====================
# Scope-Based Permissions
# =====================

def require_scopes(required_scopes: Set[str]):
    def checker(user: AuthenticatedUser = Depends(get_current_user)):
        if not required_scopes.issubset(user.scopes):
            raise HTTPException(status_code=403, detail="Missing required scope")
        return user
    return checker


# =====================
# Partner API Key Auth
# =====================

PARTNER_API_KEYS = {
    # api_key: partner_id
    "partner-key-123": "partner_abc",
}

def authenticate_api_key(api_key: Optional[str]) -> Optional[AuthenticatedUser]:
    if not api_key:
        return None

    if api_key not in PARTNER_API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API key")

    return AuthenticatedUser(
        user_id=PARTNER_API_KEYS[api_key],
        roles={"partner"},
        scopes={"read:tax"},
        session_expires_at=time.time() + TOKEN_EXPIRATION_SECONDS,
        is_partner=True,
    )


# =====================
# Current User Resolver
# =====================

def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Security(security),
    api_key: Optional[str] = Security(api_key_header),
) -> AuthenticatedUser:
    if not REQUIRE_AUTHENTICATION:
        return AuthenticatedUser(
            user_id="anonymous",
            roles={"anonymous"},
            scopes=set(),
            session_expires_at=float("inf"),
        )

    # Partner API key support
    partner_user = authenticate_api_key(api_key)
    if partner_user:
        audit_auth_event(request, partner_user, "partner_api_key_auth")
        return partner_user

    token = credentials.credentials
    payload = decode_token(token)

    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid token type")

    user = AuthenticatedUser(
        user_id=payload["sub"],
        roles=set(payload.get("roles", [])),
        scopes=set(payload.get("scopes", [])),
        session_expires_at=payload["exp"],
    )

    enforce_session_expiration(user)
    audit_auth_event(request, user, "jwt_auth")

    return user


# =====================
# Token Refresh Logic
# =====================

def refresh_access_token(refresh_token: str) -> str:
    payload = decode_token(refresh_token)

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    return create_access_token(
        user_id=payload["sub"],
        roles={"user"},
        scopes={"read:tax", "write:profile"},
    )


# =====================
# Audit Hooks
# =====================

def audit_auth_event(request: Request, user: AuthenticatedUser, event: str):
    """
    Hook for SOC-2 / compliance logging.
    Replace with real audit sink.
    """
    audit_record = {
        "event": event,
        "user_id": user.user_id,
        "roles": list(user.roles),
        "path": request.url.path,
        "ip": request.client.host if request.client else None,
        "timestamp": int(time.time()),
        "environment": ENVIRONMENT.value,
    }

    # In prod: send to audit log store
    print("[AUDIT]", audit_record)
