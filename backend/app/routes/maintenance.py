from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..auth import hash_password
from ..database import get_db
from ..dependencies import require_admin
from ..models import Book, Membership, User
from ..schemas import (
    BookCreateRequest,
    BookUpdateRequest,
    MembershipCreateRequest,
    MembershipUpdateRequest,
    UserManageRequest,
)

router = APIRouter(prefix="/maintenance", tags=["Maintenance"])


def _membership_number() -> str:
    return f"M-{date.today().strftime('%Y%m%d')}"


@router.post("/add-book")
def add_book(
    payload: BookCreateRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    existing = db.query(Book).filter(Book.serial_no == payload.serial_no).first()
    if existing:
        raise HTTPException(status_code=400, detail="Duplicate serial number")

    book = Book(
        media_type=payload.media_type,
        title=payload.title.strip(),
        author=payload.author.strip(),
        serial_no=payload.serial_no.strip(),
        category=payload.category.strip(),
        available=True,
    )
    db.add(book)
    db.commit()
    db.refresh(book)
    return {"message": "Book added successfully", "book_id": book.id}


@router.put("/update-book")
def update_book(
    payload: BookUpdateRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    book = db.query(Book).filter(Book.id == payload.book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    duplicate = (
        db.query(Book)
        .filter(Book.serial_no == payload.serial_no, Book.id != payload.book_id)
        .first()
    )
    if duplicate:
        raise HTTPException(status_code=400, detail="Duplicate serial number")

    book.media_type = payload.media_type
    book.title = payload.title.strip()
    book.author = payload.author.strip()
    book.serial_no = payload.serial_no.strip()
    book.category = payload.category.strip()
    book.available = payload.available
    db.commit()
    return {"message": "Book updated successfully"}


@router.post("/add-membership")
def add_membership(
    payload: MembershipCreateRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    start_date = date.today()
    end_date = start_date + timedelta(days=payload.duration_months * 30)
    membership = Membership(
        membership_number=f"{_membership_number()}-{datetime.now().strftime('%H%M%S%f')}",
        name=payload.member_name.strip(),
        membership_type=f"{payload.duration_months}_months",
        start_date=start_date,
        end_date=end_date,
        active=True,
    )
    db.add(membership)
    db.commit()
    db.refresh(membership)
    return {
        "message": "Membership created successfully",
        "membership_number": membership.membership_number,
    }


@router.put("/update-membership")
def update_membership(
    payload: MembershipUpdateRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    membership = (
        db.query(Membership)
        .filter(Membership.membership_number == payload.membership_number)
        .first()
    )
    if not membership:
        raise HTTPException(status_code=404, detail="Membership not found")

    if payload.action == "cancel":
        membership.active = False
        db.commit()
        return {"message": "Membership cancelled"}

    if not membership.active:
        raise HTTPException(status_code=400, detail="Cancelled membership cannot be extended")

    membership.end_date = membership.end_date + timedelta(days=payload.extension_months * 30)
    membership.membership_type = f"{payload.extension_months}_months"
    db.commit()
    return {"message": "Membership extended successfully"}


@router.get("/memberships")
def list_memberships(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    memberships = db.query(Membership).all()
    return [
        {
            "name": m.name,
            "membership_number": m.membership_number,
            "type": m.membership_type,
            "start_date": m.start_date,
            "end_date": m.end_date,
            "active": m.active,
        }
        for m in memberships
    ]


@router.post("/user-management")
def user_management(
    payload: UserManageRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    membership_id = None
    if payload.membership_number:
        membership = (
            db.query(Membership)
            .filter(Membership.membership_number == payload.membership_number)
            .first()
        )
        if not membership:
            raise HTTPException(status_code=404, detail="Membership not found")
        membership_id = membership.id

    existing = db.query(User).filter(User.username == payload.username).first()

    if payload.mode == "new":
        if existing:
            raise HTTPException(status_code=400, detail="Username already exists")
        if not payload.password:
            raise HTTPException(status_code=400, detail="Password is mandatory for new user")

        user = User(
            name=payload.name.strip(),
            username=payload.username.strip(),
            password=hash_password(payload.password),
            role=payload.role,
            membership_id=membership_id,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return {"message": "User created successfully", "user_id": user.id}

    if not existing:
        raise HTTPException(status_code=404, detail="Existing user not found")

    existing.name = payload.name.strip()
    existing.role = payload.role
    existing.membership_id = membership_id
    if payload.password:
        existing.password = hash_password(payload.password)
    db.commit()
    return {"message": "User updated successfully", "user_id": existing.id}
