"""FastAPI application for the Library Management System API."""

from fastapi import FastAPI

from app.routers.books import router as books_router
from app.routers.members import router as members_router

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

# Create the FastAPI application object that Uvicorn will load and run.
# This metadata is also displayed in the generated API documentation.
app = FastAPI(
    title="Library Management System API",
    description=(
        "Manage library Books and Members. Each Book is checked out by exactly "
        "one Member, and a Member may have many Books."
    ),
    version="0.1.0",
    openapi_tags=tags_metadata,
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
