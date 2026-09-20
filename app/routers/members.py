"""HTTP endpoints for the Member resource."""

from fastapi import APIRouter, HTTPException, Response, status

from app.schemas.books import BookResponse
from app.schemas.members import MemberInput, MemberResponse
from app.storage import books, members

# Every route in this file begins with /members and appears under the
# Members heading in FastAPI's generated API documentation.
router = APIRouter(prefix="/members", tags=["Members"])


def find_member(member_id: int) -> MemberResponse:
    """Find one member or return an HTTP 404 error to the client."""
    for member in members:
        if member.id == member_id:
            return member

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Member not found",
    )


def _check_unique(data: MemberInput, *, exclude_id: int | None = None) -> None:
    """Reject a Member email or membership_id already used by a different Member."""
    for member in members:
        if exclude_id is not None and member.id == exclude_id:
            continue
        if member.email == data.email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A member with this email already exists",
            )
        if member.membership_id == data.membership_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A member with this membership_id already exists",
            )


# GET /members reads the entire Member collection.
@router.get(
    "",
    response_model=list[MemberResponse],
    summary="List all members",
    description="Return every member currently stored by the application.",
)
def list_members() -> list[MemberResponse]:
    """Return every member currently stored in memory."""
    return members


@router.get(
    "/{member_id}",
    response_model=MemberResponse,
    summary="Get one member",
    description="Return the member identified by the path parameter.",
    responses={404: {"description": "Member not found"}},
)
def get_member(member_id: int) -> MemberResponse:
    """Return the member with the requested ID."""
    return find_member(member_id)


# POST creates a new resource, so a successful request returns HTTP 201.
@router.post(
    "",
    response_model=MemberResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a member",
    description="Create a member from a validated name, email, membership ID, and phone number.",
    responses={409: {"description": "Email or membership_id already in use"}},
)
def create_member(data: MemberInput) -> MemberResponse:
    """Create a member from a validated JSON request body."""
    _check_unique(data)
    next_member_id = max((member.id for member in members), default=0) + 1
    member = MemberResponse(
        id=next_member_id,
        **data.model_dump(),
    )
    members.append(member)
    return member


# PUT replaces the editable values of the Member identified by the URL.
@router.put(
    "/{member_id}",
    response_model=MemberResponse,
    summary="Replace a member",
    description="Replace all editable fields of an existing member.",
    responses={
        404: {"description": "Member not found"},
        409: {"description": "Email or membership_id already in use"},
    },
)
def replace_member(
    member_id: int,
    data: MemberInput,
) -> MemberResponse:
    """Replace the editable fields of an existing member."""
    member = find_member(member_id)
    _check_unique(data, exclude_id=member_id)
    updated_member = MemberResponse(
        id=member_id,
        **data.model_dump(),
    )
    members[members.index(member)] = updated_member
    return updated_member


# A successful DELETE has no response body, so it returns HTTP 204.
@router.delete(
    "/{member_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a member",
    description="Delete a member only when no books are currently checked out to them.",
    responses={
        404: {"description": "Member not found"},
        409: {"description": "Member still has associated books"},
    },
)
def delete_member(member_id: int) -> Response:
    """Remove a member from the in-memory collection."""
    member = find_member(member_id)

    # Do not leave Books pointing to a Member that no longer exists.
    if any(book.member_id == member_id for book in books):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Delete or reassign the member's books before deleting the member",
        )

    members.remove(member)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# This nested URL reads the Books that belong to one Member.
@router.get(
    "/{member_id}/books",
    response_model=list[BookResponse],
    summary="List a member's books",
    description="Return every book currently associated with the requested member.",
    responses={404: {"description": "Member not found"}},
)
def list_member_books(member_id: int) -> list[BookResponse]:
    """Return every book associated with the requested member."""
    find_member(member_id)
    return [book for book in books if book.member_id == member_id]
