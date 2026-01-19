from fastapi import HTTPException

def require_role(user, allowed_roles: set[str]):
    if user.role not in allowed_roles:
        raise HTTPException(status_code=403, detail="Insufficient permissions")


def require_scope(user, scope: str):
    if scope not in user.scopes:
        raise HTTPException(status_code=403, detail="Missing required scope")
