"""FastAPI application for the Library Management System API."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import models  # noqa: F401  # Register ORM models before create_all().
from app.config import Settings, StorageBackend
from app.database.session import create_database
from app.models.base import Base
from app.routers.books import router as books_router
from app.routers.members import router as members_router
from app.services.books import DatabaseBookService, InMemoryBookService
from app.services.in_memory_store import InMemoryStore
from app.services.members import DatabaseMemberService, InMemoryMemberService

# Tag descriptions organize related operations and explain each resource
# group in Swagger UI and ReDoc.
tags_metadata = [
    {
        "name": "General",
        "description": "Basic application information and health checks.",
    },
    {
        "name": "Books",
        "description": "Create and manage books and the member who has each one checked out.",
    },
    {
        "name": "Members",
        "description": "Create and manage members and view the books they have checked out.",
    },
]


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Create the settings and the selected services once, at startup."""
    settings = Settings()
    application.state.settings = settings
    database = None

    if settings.storage_backend is StorageBackend.MEMORY:
        store = InMemoryStore.with_demo_data()
        application.state.member_service = InMemoryMemberService(store)
        application.state.book_service = InMemoryBookService(store)
    elif settings.storage_backend is StorageBackend.DATABASE:
        database = create_database(settings)
        # Missing tables are created at startup; schema migrations are out of
        # scope until a later module.
        Base.metadata.create_all(bind=database.engine)
        # Services are stateless and safe to share. They receive the session
        # factory, not a Session, so each operation opens its own Session and
        # controls its own transaction.
        application.state.member_service = DatabaseMemberService(
            database.session_factory
        )
        application.state.book_service = DatabaseBookService(
            database.session_factory
        )

    yield

    # Shutdown: close pooled database connections.
    if database is not None:
        database.engine.dispose()


# Create the FastAPI application object that Uvicorn will load and run.
# This metadata is also displayed in the generated API documentation.
app = FastAPI(
    title="Library Management System API",
    description=(
        "Manage library Books and Members. Each Book is checked out by exactly "
        "one Member, and a Member may have many Books. Data is stored in "
        "PostgreSQL by default, or in process memory when STORAGE_BACKEND=memory."
    ),
    version="0.2.0",
    openapi_tags=tags_metadata,
    lifespan=lifespan,
)

# Add every Book and Member route to the application. Keeping resource
# routes in a router prevents main.py from becoming crowded.
app.include_router(books_router)
app.include_router(members_router)


@app.get("/", tags=["General"], summary="Introduce the API")
def read_root() -> dict[str, str]:
    """Return a short introduction to the API."""
    return {"message": "Library Management System API"}


@app.get(
    "/health",
    tags=["General"],
    summary="Check API health",
    description="Confirm that the API process is running",
)
def health_check() -> dict[str, str]:
    """Confirm that the API process is running."""
    return {"status": "healthy"}
