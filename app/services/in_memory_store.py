"""Shared in-memory state for the alternative service implementations."""

from dataclasses import dataclass, field
from threading import RLock

from app.models.book import Book
from app.models.member import Member


@dataclass
class InMemoryStore:
    """Hold Members and Books for one application-scoped in-memory service pair."""

    members: list[Member] = field(default_factory=list)
    books: list[Book] = field(default_factory=list)
    # One process-local lock protects compound operations such as ID
    # generation, relationship checks, and list mutation.
    lock: RLock = field(default_factory=RLock, repr=False)

    @classmethod
    def with_demo_data(cls) -> "InMemoryStore":
        """Create a store seeded so the relationship endpoints have data to show."""
        return cls(
            members=[
                Member(
                    id=1,
                    name="Jordan Lee",
                    email="jordan.lee@example.com",
                    membership_id="MBR-1001",
                    phone="555-201-3048",
                )
            ],
            books=[
                Book(
                    id=1,
                    title="The Pragmatic Programmer",
                    author="David Thomas",
                    isbn="978-0135957059",
                    published_year=2019,
                    member_id=1,
                )
            ],
        )
