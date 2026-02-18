from typing import Annotated
from pathlib import Path
import sys

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

try:
    from app.auth import decode_access_token
    from app.database import get_db
    from app.models import User
except ImportError:
    if __package__ in (None, ""):
        sys.path.append(str(Path(__file__).resolve().parents[1]))
        from app.auth import decode_access_token
        from app.database import get_db
        from app.models import User
    else:
        from .auth import decode_access_token
        from .database import get_db
        from .models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user_id_raw = payload.get("sub")
    if user_id_raw is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    try:
        user_id = int(user_id_raw)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token subject",
        ) from None

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user


def require_admin(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    role = (current_user.role or "").strip().lower()
    if role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


def require_user_or_admin(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    if current_user.role not in {"admin", "user"}:
        raise HTTPException(status_code=403, detail="Access denied")
    return current_user
