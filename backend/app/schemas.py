from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    role: str
    access_token: str
    token_type: str = "bearer"


class BookCreateRequest(BaseModel):
    media_type: Literal["book", "movie"] = "book"
    title: str
    author: str
    serial_no: str
    category: str = "general"


class BookUpdateRequest(BaseModel):
    book_id: int
    media_type: Literal["book", "movie"] = "book"
    title: str
    author: str
    serial_no: str
    category: str = "general"
    available: bool = True


class MembershipCreateRequest(BaseModel):
    member_name: str
    duration_months: Literal[6, 12, 24] = 6


class MembershipUpdateRequest(BaseModel):
    membership_number: str
    action: Literal["extend", "cancel"] = "extend"
    extension_months: Literal[6, 12, 24] = 6


class UserManageRequest(BaseModel):
    mode: Literal["new", "existing"] = "new"
    name: str
    username: str
    password: str | None = None
    role: Literal["admin", "user"] = "user"
    membership_number: str | None = None


class BookAvailabilityQuery(BaseModel):
    title: str | None = None
    media_type: Literal["book", "movie"] | None = None


class IssueBookRequest(BaseModel):
    user_id: int
    book_id: int
    issue_date: date
    return_date: date | None = None
    remarks: str | None = None


class ReturnBookRequest(BaseModel):
    transaction_id: int
    serial_no: str
    return_date: date


class PayFineRequest(BaseModel):
    transaction_id: int
    fine_paid: bool = Field(default=False)
    remarks: str | None = None
