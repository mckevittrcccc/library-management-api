"""HTTP endpoints for the Book resource."""

from fastapi import APIRouter, HTTPException, Response, status

from app.routers.members import find_member
from app.schemas.books import BookInput, BookResponse
from app.storage import books

# Every route in this file begins with /books and appears under the
# Books heading in FastAPI's generated API documentation.
router = APIRouter(prefix="/books", tags=["Books"])


def find_book(book_id: int) -> BookResponse:
    """Find one book or return an HTTP 404 error to the client."""
    for book in books:
        if book.id == book_id:
            return book

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Book not found",
    )


def _check_unique_isbn(isbn: str, *, exclude_id: int | None = None) -> None:
    """Reject an ISBN already used by a different Book."""
    for book in books:
        if exclude_id is not None and book.id == exclude_id:
            continue
        if book.isbn == isbn:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A book with this ISBN already exists",
            )


@router.get(
    "",
    response_model=list[BookResponse],
    summary="List all books",
    description="Return every book currently stored by the application.",
)
def list_books() -> list[BookResponse]:
    """Return every book currently stored in memory."""
    return books


@router.get(
    "/{book_id}",
    response_model=BookResponse,
    summary="Get one book",
    description="Return the book identified by the path parameter.",
    responses={404: {"description": "Book not found"}},
)
def get_book(book_id: int) -> BookResponse:
    """Return the book with the requested ID."""
    return find_book(book_id)


# A Book can be created only when its related Member exists.
@router.post(
    "",
    response_model=BookResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a book",
    description="Create a book and associate it with an existing member.",
    responses={
        404: {"description": "Related member not found"},
        409: {"description": "ISBN already in use"},
    },
)
def create_book(data: BookInput) -> BookResponse:
    """Create a book associated with an existing member."""
    # FastAPI validates BookInput before this function runs and uses the
    # same schema in OpenAPI. This application-level check then confirms
    # that the related Member resource actually exists.
    find_member(data.member_id)
    _check_unique_isbn(data.isbn)
    next_book_id = max((book.id for book in books), default=0) + 1

    book = BookResponse(
        id=next_book_id,
        **data.model_dump(),
    )
    books.append(book)
    return book


# PUT replaces all editable Book values, including its Member relationship.
@router.put(
    "/{book_id}",
    response_model=BookResponse,
    summary="Replace a book",
    description="Replace all editable fields and verify the related member.",
    responses={
        404: {"description": "Book or related member not found"},
        409: {"description": "ISBN already in use"},
    },
)
def replace_book(
    book_id: int,
    data: BookInput,
) -> BookResponse:
    """Replace an existing book after checking its related member."""
    book = find_book(book_id)
    find_member(data.member_id)
    _check_unique_isbn(data.isbn, exclude_id=book_id)
    updated_book = BookResponse(
        id=book_id,
        **data.model_dump(),
    )
    books[books.index(book)] = updated_book
    return updated_book


@router.delete(
    "/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a book",
    description="Delete the book identified by the path parameter.",
    responses={404: {"description": "Book not found"}},
)
def delete_book(book_id: int) -> Response:
    """Remove a book from the in-memory collection."""
    book = find_book(book_id)
    books.remove(book)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
