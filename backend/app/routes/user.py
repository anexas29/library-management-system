from fastapi import APIRouter, Depends

from ..dependencies import require_user_or_admin
from ..models import User

router = APIRouter(
    prefix="/user",
    tags=["User"]
)

@router.get("/home")
def user_home(current_user: User = Depends(require_user_or_admin)):
    if current_user.role != "user":
        return {"modules": ["Maintenance", "Reports", "Transactions"]}
    return {
        "modules": [
            "Reports",
            "Transactions"
        ]
    }
