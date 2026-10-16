"""Relational-database Member service implementation."""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from app.exceptions import (
    MemberEmailAlreadyExistsError,
    MemberHasBooksError,
    MemberNotFoundError,
    MembershipIdAlreadyExistsError,
)
from app.models.book import Book
from app.models.member import Member
from app.repositories.books import BookRepository
from app.repositories.members import MemberRepository
from app.schemas.members import MemberInput
from app.services.integrity import violated_constraint
from .base import MemberService


class DatabaseMemberService(MemberService):
    """Implement Member use cases with database persistence.

    The service applies application rules and defines transaction boundaries.
    """

    def __init__(self, session_factory: sessionmaker[Session]):
        # Share the factory; each operation creates its own Session.
        self._session_factory = session_factory

    def list_members(self) -> list[Member]:
        with self._session_factory() as session:
            return MemberRepository(session).list_all()

    def get_member(self, member_id: int) -> Member:
        with self._session_factory() as session:
            member = MemberRepository(session).get_by_id(member_id)
            if member is None:
                raise MemberNotFoundError
            return member

    def create_member(self, data: MemberInput) -> Member:
        try:
            # begin() commits on success and rolls back if an exception escapes.
            with self._session_factory.begin() as session:
                repository = MemberRepository(session)
                self._ensure_unique(repository, data)
                member = repository.create(data)
                session.refresh(member)
                return member
        except IntegrityError as error:
            raise self._translate_conflict(error) from None

    def replace_member(self, member_id: int, data: MemberInput) -> Member:
        try:
            # Read, validate, update, and commit are one atomic use case.
            with self._session_factory.begin() as session:
                repository = MemberRepository(session)
                member = repository.get_by_id(member_id)
                if member is None:
                    raise MemberNotFoundError
                self._ensure_unique(repository, data, exclude_id=member_id)
                updated_member = repository.replace(member, data)
                session.refresh(updated_member)
                return updated_member
        except IntegrityError as error:
            raise self._translate_conflict(error) from None

    def delete_member(self, member_id: int) -> None:
        try:
            # The Book check and the delete belong to one transaction.
            with self._session_factory.begin() as session:
                repository = MemberRepository(session)
                member = repository.get_by_id(member_id)
                if member is None:
                    raise MemberNotFoundError
                if BookRepository(session).exists_for_member(member_id):
                    raise MemberHasBooksError
                repository.delete(member)
        except IntegrityError as error:
            # A Book was added after the check; the foreign key blocked the delete.
            if violated_constraint(error) == "books_member_id_fkey":
                raise MemberHasBooksError from None
            raise

    def list_member_books(self, member_id: int) -> list[Book]:
        with self._session_factory() as session:
            if MemberRepository(session).get_by_id(member_id) is None:
                raise MemberNotFoundError
            return BookRepository(session).list_by_member(member_id)

    @staticmethod
    def _ensure_unique(
        repository: MemberRepository,
        data: MemberInput,
        *,
        exclude_id: int | None = None,
    ) -> None:
        """Reject an email or membership ID already used by a different Member."""
        same_email = repository.get_by_email(data.email)
        if same_email is not None and same_email.id != exclude_id:
            raise MemberEmailAlreadyExistsError
        same_membership = repository.get_by_membership_id(data.membership_id)
        if same_membership is not None and same_membership.id != exclude_id:
            raise MembershipIdAlreadyExistsError

    @staticmethod
    def _translate_conflict(error: IntegrityError) -> Exception:
        """Map a unique-constraint race to the same outcome as the pre-check."""
        constraint = violated_constraint(error)
        if constraint == "uq_members_email":
            return MemberEmailAlreadyExistsError()
        if constraint == "uq_members_membership_id":
            return MembershipIdAlreadyExistsError()
        return error
