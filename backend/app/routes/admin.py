from fastapi import APIRouter, Depends
from ..dependencies import require_admin

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)

@router.get("/home")
def admin_home(_: dict = Depends(require_admin)):
    return {
        "modules": [
            "Maintenance",
            "Reports",
            "Transactions"
        ]
    }
