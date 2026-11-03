from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.jwt import decode_access_token
from app.db.session import get_db
from app.services.user_manager import get_user_by_id


bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token = credentials.credentials
        payload = decode_access_token(token)
        user_id = int(payload.get("sub"))

    except Exception:
        raise credentials_exception

    user = get_user_by_id(db, user_id)

    if user is None or not user.is_active:
        raise credentials_exception

    return user