"""SQLAlchemy model for the books table."""

from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Book(Base):
    """Map Book objects to rows in the books table."""

    __tablename__ = "books"
    __table_args__ = (UniqueConstraint("isbn", name="uq_books_isbn"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    author: Mapped[str] = mapped_column(String(120), nullable=False)
    isbn: Mapped[str] = mapped_column(String(20), nullable=False)
    published_year: Mapped[int] = mapped_column(Integer, nullable=False)
    # The foreign key stops the database from storing a Book that points to a
    # Member that does not exist, even if application checks are bypassed.
    member_id: Mapped[int] = mapped_column(
        ForeignKey("members.id"),
        nullable=False,
        index=True,
    )

    member: Mapped[Member] = relationship(back_populates="books")
