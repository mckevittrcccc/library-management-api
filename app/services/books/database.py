"""Relational-database Book service implementation."""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from app.exceptions import (
    BookIsbnAlreadyExistsError,
    BookNotFoundError,
    MemberNotFoundError,
)
from app.models.book import Book
from app.repositories.books import BookRepository
from app.repositories.members import MemberRepository
from app.schemas.books import BookInput
from app.services.integrity import violated_constraint
from .base import BookService


class DatabaseBookService(BookService):
    """Implement Book use cases with database persistence.

    The service applies application rules and defines transaction boundaries.
    """

    def __init__(self, session_factory: sessionmaker[Session]):
        # Share the factory; each operation creates its own Session.
        self._session_factory = session_factory

    def list_books(self) -> list[Book]:
        with self._session_factory() as session:
            return BookRepository(session).list_all()

    def get_book(self, book_id: int) -> Book:
        with self._session_factory() as session:
            book = BookRepository(session).get_by_id(book_id)
            if book is None:
                raise BookNotFoundError
            return book

    def create_book(self, data: BookInput) -> Book:
        try:
            # Verify the Member, check the ISBN, and insert atomically.
            with self._session_factory.begin() as session:
                if MemberRepository(session).get_by_id(data.member_id) is None:
                    raise MemberNotFoundError
                repository = BookRepository(session)
                self._ensure_unique_isbn(repository, data.isbn)
                book = repository.create(data)
                session.refresh(book)
                return book
        except IntegrityError as error:
            raise self._translate_conflict(error) from None

    def replace_book(self, book_id: int, data: BookInput) -> Book:
        try:
            # Lookup, validation, update, and commit are one atomic use case.
            with self._session_factory.begin() as session:
                repository = BookRepository(session)
                book = repository.get_by_id(book_id)
                if book is None:
                    raise BookNotFoundError
                if MemberRepository(session).get_by_id(data.member_id) is None:
                    raise MemberNotFoundError
                self._ensure_unique_isbn(repository, data.isbn, exclude_id=book_id)
                updated_book = repository.replace(book, data)
                session.refresh(updated_book)
                return updated_book
        except IntegrityError as error:
            raise self._translate_conflict(error) from None

    def delete_book(self, book_id: int) -> None:
        with self._session_factory.begin() as session:
            repository = BookRepository(session)
            book = repository.get_by_id(book_id)
            if book is None:
                raise BookNotFoundError
            repository.delete(book)

    @staticmethod
    def _ensure_unique_isbn(
        repository: BookRepository, isbn: str, *, exclude_id: int | None = None
    ) -> None:
        """Reject an ISBN already used by a different Book."""
        same_isbn = repository.get_by_isbn(isbn)
        if same_isbn is not None and same_isbn.id != exclude_id:
            raise BookIsbnAlreadyExistsError

    @staticmethod
    def _translate_conflict(error: IntegrityError) -> Exception:
        """Map a constraint race to the same outcome as the pre-checks."""
        constraint = violated_constraint(error)
        if constraint == "uq_books_isbn":
            return BookIsbnAlreadyExistsError()
        if constraint == "books_member_id_fkey":
            # The Member was deleted after the existence check.
            return MemberNotFoundError()
        return error
