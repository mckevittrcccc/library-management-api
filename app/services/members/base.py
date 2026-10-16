"""Abstract Member service contract."""

from abc import ABC, abstractmethod

from app.models.book import Book
from app.models.member import Member
from app.schemas.members import MemberInput


class MemberService(ABC):
    """Define Member use-case operations shared by all implementations."""

    @abstractmethod
    def list_members(self) -> list[Member]:
        """Return every Member."""

    @abstractmethod
    def get_member(self, member_id: int) -> Member:
        """Return one Member or raise MemberNotFoundError."""

    @abstractmethod
    def create_member(self, data: MemberInput) -> Member:
        """Create and return a Member, rejecting duplicate email or membership ID."""

    @abstractmethod
    def replace_member(self, member_id: int, data: MemberInput) -> Member:
        """Replace and return one Member, rejecting duplicate email or membership ID."""

    @abstractmethod
    def delete_member(self, member_id: int) -> None:
        """Delete a Member unless Books still reference them."""

    @abstractmethod
    def list_member_books(self, member_id: int) -> list[Book]:
        """Return the Books associated with one Member."""
