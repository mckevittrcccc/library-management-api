"""Abstract Book service contract."""

from abc import ABC, abstractmethod

from app.models.book import Book
from app.schemas.books import BookInput


class BookService(ABC):
    """Define Book use-case operations shared by all implementations."""

    @abstractmethod
    def list_books(self) -> list[Book]:
        """Return every Book."""

    @abstractmethod
    def get_book(self, book_id: int) -> Book:
        """Return one Book or raise BookNotFoundError."""

    @abstractmethod
    def create_book(self, data: BookInput) -> Book:
        """Create a Book for an existing Member, rejecting a duplicate ISBN."""

    @abstractmethod
    def replace_book(self, book_id: int, data: BookInput) -> Book:
        """Replace a Book, verifying its Member and rejecting a duplicate ISBN."""

    @abstractmethod
    def delete_book(self, book_id: int) -> None:
        """Delete a Book."""
