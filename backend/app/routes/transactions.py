from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import require_user_or_admin
from ..models import Book, Membership, Transaction, User
from ..schemas import IssueBookRequest, PayFineRequest, ReturnBookRequest

router = APIRouter(prefix="/transactions", tags=["Transactions"])
FINE_PER_DAY = 10


def _has_unpaid_fine(db: Session, user_id: int) -> bool:
    txn = (
        db.query(Transaction)
        .filter(
            Transaction.user_id == user_id,
            Transaction.calculated_fine > Transaction.fine_paid,
        )
        .first()
    )
    return txn is not None


def _has_active_membership(db: Session, user: User, on_date: date) -> bool:
    if not user.membership_id:
        return False
    membership = db.query(Membership).filter(Membership.id == user.membership_id).first()
    if not membership:
        return False
    return membership.active and membership.start_date <= on_date <= membership.end_date


@router.get("/book-available")
def book_available(
    title: str | None = Query(default=None),
    media_type: str | None = Query(default=None),
    db: Session = Depends(get_db),
    _: User = Depends(require_user_or_admin),
):
    if not title and not media_type:
        raise HTTPException(status_code=400, detail="Provide either title or media_type")

    query = db.query(Book).filter(Book.available == True)
    if title:
        query = query.filter(Book.title.ilike(f"%{title.strip()}%"))
    if media_type:
        query = query.filter(Book.media_type == media_type.strip().lower())

    books = query.all()
    return [
        {
            "id": b.id,
            "title": b.title,
            "author": b.author,
            "serial_no": b.serial_no,
            "media_type": b.media_type,
            "available": b.available,
        }
        for b in books
    ]


@router.post("/issue-book")
def issue_book(
    payload: IssueBookRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_user_or_admin),
):
    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    book = db.query(Book).filter(Book.id == payload.book_id, Book.available == True).first()
    if not book:
        raise HTTPException(status_code=400, detail="Book not available")

    if payload.issue_date < date.today():
        raise HTTPException(status_code=400, detail="Issue date cannot be lesser than today")

    if not _has_active_membership(db, user, payload.issue_date):
        raise HTTPException(status_code=400, detail="Active membership required")

    if _has_unpaid_fine(db, payload.user_id):
        raise HTTPException(status_code=400, detail="User has unpaid fine")

    max_return_date = payload.issue_date + timedelta(days=15)
    due_date = payload.return_date or max_return_date

    if due_date > max_return_date:
        raise HTTPException(status_code=400, detail="Return date cannot be greater than 15 days")
    if due_date < payload.issue_date:
        raise HTTPException(status_code=400, detail="Return date cannot be before issue date")

    txn = Transaction(
        book_id=book.id,
        user_id=payload.user_id,
        issue_date=payload.issue_date,
        due_date=due_date,
        remarks=payload.remarks,
    )
    book.available = False
    db.add(txn)
    db.commit()
    db.refresh(txn)
    return {
        "message": "Book issued successfully",
        "transaction_id": txn.id,
        "book_name": book.title,
        "author": book.author,
        "issue_date": txn.issue_date,
        "return_date": txn.due_date,
    }


@router.post("/return-book")
def return_book(
    payload: ReturnBookRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_user_or_admin),
):
    txn = (
        db.query(Transaction)
        .filter(Transaction.id == payload.transaction_id, Transaction.return_date == None)
        .first()
    )
    if not txn:
        raise HTTPException(status_code=404, detail="Active transaction not found")

    book = db.query(Book).filter(Book.id == txn.book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if book.serial_no != payload.serial_no:
        raise HTTPException(status_code=400, detail="Serial number mismatch")

    txn.pending_return_date = payload.return_date
    days_late = max((payload.return_date - txn.due_date).days, 0)
    fine = days_late * FINE_PER_DAY
    txn.calculated_fine = fine
    db.commit()
    return {
        "message": "Proceed to pay fine page",
        "transaction_id": txn.id,
        "book_name": book.title,
        "author": book.author,
        "issue_date": txn.issue_date,
        "return_date": txn.due_date,
        "selected_return_date": payload.return_date,
        "fine": fine,
    }


@router.post("/pay-fine")
def pay_fine(
    payload: PayFineRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_user_or_admin),
):
    txn = (
        db.query(Transaction)
        .filter(Transaction.id == payload.transaction_id, Transaction.return_date == None)
        .first()
    )
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")

    if txn.calculated_fine > 0 and not payload.fine_paid:
        raise HTTPException(status_code=400, detail="Paid fine checkbox is mandatory for pending fine")

    txn.fine_paid = txn.calculated_fine if payload.fine_paid else 0
    txn.return_date = txn.pending_return_date or date.today()
    txn.pending_return_date = None
    if payload.remarks:
        txn.remarks = payload.remarks

    book = db.query(Book).filter(Book.id == txn.book_id).first()
    if book:
        book.available = True

    db.commit()
    return {"message": "Book returned successfully"}


@router.get("/overdue-returns")
def overdue_returns(db: Session = Depends(get_db), _: User = Depends(require_user_or_admin)):
    today = date.today()
    txns = (
        db.query(Transaction)
        .filter(Transaction.return_date == None, Transaction.due_date < today)
        .all()
    )
    return [
        {
            "transaction_id": t.id,
            "book_id": t.book_id,
            "user_id": t.user_id,
            "due_date": t.due_date,
            "days_late": (today - t.due_date).days,
            "fine": (today - t.due_date).days * FINE_PER_DAY,
        }
        for t in txns
    ]


@router.get("/active-issues")
def active_issues(db: Session = Depends(get_db), _: User = Depends(require_user_or_admin)):
    txns = db.query(Transaction).filter(Transaction.return_date == None).all()
    return [
        {
            "transaction_id": t.id,
            "user_id": t.user_id,
            "book_id": t.book_id,
            "issue_date": t.issue_date,
            "due_date": t.due_date,
        }
        for t in txns
    ]
