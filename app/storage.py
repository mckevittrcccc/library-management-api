"""Temporary in-memory storage shared by the API routers."""

from app.schemas.books import BookResponse
from app.schemas.members import MemberResponse

# These lists reset whenever the application restarts. A database and
# repository layer will replace them in a later assignment.
members: list[MemberResponse] = [
    MemberResponse(
        id=1,
        name="Jordan Lee",
        email="jordan.lee@example.com",
        membership_id="MBR-1001",
        phone="555-201-3048",
    )
]

books: list[BookResponse] = [
    BookResponse(
        id=1,
        title="The Pragmatic Programmer",
        author="David Thomas",
        isbn="978-0135957059",
        published_year=2019,
        member_id=1,
    )
]
