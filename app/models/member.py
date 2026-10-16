"""SQLAlchemy model for the members table."""

from __future__ import annotations

from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Member(Base):
    """Map Member objects to rows in the members table."""

    __tablename__ = "members"
    # Named constraints let the service layer tell which rule a database
    # IntegrityError violated without exposing raw database messages.
    __table_args__ = (
        UniqueConstraint("email", name="uq_members_email"),
        UniqueConstraint("membership_id", name="uq_members_membership_id"),
    )

    # PostgreSQL generates the primary key.
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(320), nullable=False)
    membership_id: Mapped[str] = mapped_column(String(40), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)

    # One Member has many Books. The foreign key lives on Book, the "many" side.
    books: Mapped[list[Book]] = relationship(back_populates="member")
