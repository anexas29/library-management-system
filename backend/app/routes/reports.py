from datetime import date
from typing import Annotated, Optional
from pathlib import Path
import sys

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

try:
    from app.database import get_db
    from app.dependencies import require_user_or_admin
    from app.models import Transaction, User
except ImportError:
    if __package__ in (None, ""):
        sys.path.append(str(Path(__file__).resolve().parents[2]))
        from app.database import get_db
        from app.dependencies import require_user_or_admin
        from app.models import Transaction, User
    else:
        from ..database import get_db
        from ..dependencies import require_user_or_admin
        from ..models import Transaction, User

router = APIRouter(prefix="/reports", tags=["Reports"])
FINE_PER_DAY = 10


def _issue_status(return_date: Optional[date]) -> str:
    return "Returned" if return_date is not None else "Issued"


def _fine_status(calculated_fine: Optional[int], fine_paid: Optional[int]) -> str:
    due_fine = calculated_fine or 0
    paid_fine = fine_paid or 0
    return "Fine Pending" if due_fine > paid_fine else "Clear"


@router.get("/issued-books")
def issued_books_report(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_user_or_admin)],
):
    txns = db.query(Transaction).all()
    return [
        {
            "transaction_id": t.id,
            "user_id": t.user_id,
            "book_id": t.book_id,
            "issue_date": t.issue_date,
            "due_date": t.due_date,
            "status": _issue_status(t.return_date),
        }
        for t in txns
    ]


@router.get("/returned-books")
def returned_books_report(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_user_or_admin)],
):
    txns = db.query(Transaction).filter(Transaction.return_date.is_not(None)).all()
    return [
        {
            "transaction_id": t.id,
            "user_id": t.user_id,
            "book_id": t.book_id,
            "issue_date": t.issue_date,
            "return_date": t.return_date,
            "fine_paid": t.fine_paid,
            "status": "Returned",
        }
        for t in txns
    ]


@router.get("/fine-report")
def fine_report(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_user_or_admin)],
):
    txns = db.query(Transaction).all()
    return [
        {
            "transaction_id": t.id,
            "user_id": t.user_id,
            "book_id": t.book_id,
            "due_date": t.due_date,
            "return_date": t.return_date,
            "fine": t.calculated_fine or 0,
            "fine_paid": t.fine_paid or 0,
            "status": _fine_status(t.calculated_fine, t.fine_paid),
        }
        for t in txns
    ]


@router.get("/user-transactions/{user_id}")
def user_transactions_report(
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_user_or_admin)],
):
    txns = db.query(Transaction).filter(Transaction.user_id == user_id).all()
    return [
        {
            "transaction_id": t.id,
            "book_id": t.book_id,
            "issue_date": t.issue_date,
            "due_date": t.due_date,
            "return_date": t.return_date,
            "status": _issue_status(t.return_date),
        }
        for t in txns
    ]


@router.get("/overdue-returns")
def overdue_returns_report(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_user_or_admin)],
):
    today = date.today()
    txns = (
        db.query(Transaction)
        .filter(Transaction.return_date.is_(None), Transaction.due_date < today)
        .all()
    )
    return [
        {
            "transaction_id": t.id,
            "user_id": t.user_id,
            "book_id": t.book_id,
            "due_date": t.due_date,
            "days_late": (today - t.due_date).days,
            "fine": (today - t.due_date).days * FINE_PER_DAY,
        }
        for t in txns
    ]

