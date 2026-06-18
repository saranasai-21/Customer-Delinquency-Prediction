# backend/api/routers/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """OAuth2 password login flow returning custom tokens for RBAC groups."""
    username = form_data.username
    password = form_data.password
    
    # Mock authentication checks
    if username == "admin" and password == "admin123":
        return {
            "access_token": "admin-token-secret",
            "token_type": "bearer",
            "role": "admin"
        }
    elif username == "analyst" and password == "analyst123":
        return {
            "access_token": "analyst-token-secret",
            "token_type": "bearer",
            "role": "analyst"
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
