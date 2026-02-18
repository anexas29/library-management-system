from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from ..auth import create_access_token, verify_password
from ..database import get_db
from ..models import User
from ..schemas import LoginRequest, LoginResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=LoginResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": str(user.id), "role": user.role})
    return {"role": user.role, "access_token": token, "token_type": "bearer"}
