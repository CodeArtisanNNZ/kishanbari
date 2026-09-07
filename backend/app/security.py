from datetime import datetime, timedelta, timezone
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session
from .config import get_settings
from .database import get_db
from .models import User

password_hash = PasswordHash.recommended()
bearer = HTTPBearer(auto_error=False)

def hash_password(value: str) -> str: return password_hash.hash(value)
def verify_password(value: str, hashed: str) -> bool: return password_hash.verify(value, hashed)
def create_token(user: User) -> str:
    settings = get_settings()
    payload = {"sub": user.id, "admin": user.is_admin, "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_minutes)}
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")

def current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer), db: Session = Depends(get_db)) -> User:
    if not credentials: raise HTTPException(status.HTTP_401_UNAUTHORIZED, "লগইন প্রয়োজন")
    try:
        payload = jwt.decode(credentials.credentials, get_settings().jwt_secret, algorithms=["HS256"])
        user_id = payload["sub"]
    except (InvalidTokenError, KeyError):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "অকার্যকর বা মেয়াদোত্তীর্ণ টোকেন")
    user = db.scalar(select(User).where(User.id == user_id))
    if not user: raise HTTPException(status.HTTP_401_UNAUTHORIZED, "ব্যবহারকারী পাওয়া যায়নি")
    return user

def admin_user(user: User = Depends(current_user)) -> User:
    if not user.is_admin: raise HTTPException(status.HTTP_403_FORBIDDEN, "অ্যাডমিন অনুমতি প্রয়োজন")
    return user
