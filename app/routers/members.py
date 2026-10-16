"""HTTP endpoints for the Member resource."""

from fastapi import APIRouter, Depends, Response, status

from app.dependencies import get_member_service
from app.exceptions import (
    MemberEmailAlreadyExistsError,
    MemberHasBooksError,
    MemberNotFoundError,
    MembershipIdAlreadyExistsError,
)
from app.models.book import Book
from app.models.member import Member
from app.routers.http_errors import (
    member_email_already_exists,
    member_has_books,
    member_not_found,
    membership_id_already_exists,
)
from app.schemas.books import BookResponse
from app.schemas.members import MemberInput, MemberResponse
from app.services.members import MemberService

# Every route in this file begins with /members and appears under the
# Members heading in FastAPI's generated API documentation.
router = APIRouter(prefix="/members", tags=["Members"])


# GET /members reads the entire Member collection.
@router.get(
    "",
    response_model=list[MemberResponse],
    summary="List all members",
    description="Return every member currently stored by the application.",
)
def list_members(
    service: MemberService = Depends(get_member_service),
) -> list[Member]:
    """Delegate Member retrieval to the service layer."""
    return service.list_members()


@router.get(
    "/{member_id}",
    response_model=MemberResponse,
    summary="Get one member",
    description="Return the member identified by the path parameter.",
    responses={404: {"description": "Member not found"}},
)
def get_member(
    member_id: int,
    service: MemberService = Depends(get_member_service),
) -> Member:
    """Return one Member or translate the missing-resource error."""
    try:
        return service.get_member(member_id)
    except MemberNotFoundError:
        raise member_not_found() from None


# POST creates a new resource, so a successful request returns HTTP 201.
@router.post(
    "",
    response_model=MemberResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a member",
    description="Create a member from a validated name, email, membership ID, and phone number.",
    responses={409: {"description": "Email or membership_id already in use"}},
)
def create_member(
    data: MemberInput,
    service: MemberService = Depends(get_member_service),
) -> Member:
    """Pass validated input to the service and translate conflicts."""
    try:
        return service.create_member(data)
    except MemberEmailAlreadyExistsError:
        raise member_email_already_exists() from None
    except MembershipIdAlreadyExistsError:
        raise membership_id_already_exists() from None


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
    service: MemberService = Depends(get_member_service),
) -> Member:
    """Replace one Member through the service layer."""
    try:
        return service.replace_member(member_id, data)
    except MemberNotFoundError:
        raise member_not_found() from None
    except MemberEmailAlreadyExistsError:
        raise member_email_already_exists() from None
    except MembershipIdAlreadyExistsError:
        raise membership_id_already_exists() from None


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
def delete_member(
    member_id: int,
    service: MemberService = Depends(get_member_service),
) -> Response:
    """Translate Member deletion outcomes into HTTP responses."""
    try:
        service.delete_member(member_id)
    except MemberNotFoundError:
        raise member_not_found() from None
    except MemberHasBooksError:
        raise member_has_books() from None
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# This nested URL reads the Books that belong to one Member.
@router.get(
    "/{member_id}/books",
    response_model=list[BookResponse],
    summary="List a member's books",
    description="Return every book currently associated with the requested member.",
    responses={404: {"description": "Member not found"}},
)
def list_member_books(
    member_id: int,
    service: MemberService = Depends(get_member_service),
) -> list[Book]:
    """Return related Books after the service verifies the Member."""
    try:
        return service.list_member_books(member_id)
    except MemberNotFoundError:
        raise member_not_found() from None
