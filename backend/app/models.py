from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Date,
    ForeignKey,
    Text
)
from sqlalchemy.orm import relationship
from .database import Base


# --------------------------------------------------
# USER MODEL
# --------------------------------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(20), default="user")  # admin / user
    membership_id = Column(Integer, ForeignKey("memberships.id"), nullable=True)

    transactions = relationship("Transaction", back_populates="user")
    membership = relationship("Membership", back_populates="users")


# --------------------------------------------------
# BOOK / MOVIE MODEL
# --------------------------------------------------
class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    author = Column(String(100), nullable=False)
    serial_no = Column(String(50), unique=True, nullable=False)
    media_type = Column(String(20), default="book")  # book / movie
    category = Column(String(50), default="general")
    available = Column(Boolean, default=True)

    transactions = relationship("Transaction", back_populates="book")


# --------------------------------------------------
# MEMBERSHIP MODEL
# --------------------------------------------------
class Membership(Base):
    __tablename__ = "memberships"

    id = Column(Integer, primary_key=True, index=True)
    membership_number = Column(String(30), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    membership_type = Column(String(20), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    active = Column(Boolean, default=True)
    users = relationship("User", back_populates="membership")


# --------------------------------------------------
# TRANSACTION MODEL
# --------------------------------------------------
class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)

    issue_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    pending_return_date = Column(Date, nullable=True)
    return_date = Column(Date, nullable=True)

    calculated_fine = Column(Integer, default=0)
    fine_paid = Column(Integer, default=0)

    remarks = Column(Text, nullable=True)

    user = relationship("User", back_populates="transactions")
    book = relationship("Book", back_populates="transactions")
