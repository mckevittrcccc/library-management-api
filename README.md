# Library Management System API

The Library Management System API is a backend for managing library **Books** and **Members**. Library staff can create, view, update, and delete both resources. Each Book is checked out by exactly one Member, and a Member may have many Books. This is Assignment 1 for SDEV 3310, built on the REST, Pydantic, router, HTTP-status, and OpenAPI practices demonstrated in the course's Project and Task Management API.

Database persistence is intentionally out of scope for this milestone. Books and Members are stored in Python lists in application memory, so all data resets when the server restarts. A later assignment replaces this with SQLAlchemy and a relational database.

## Setup

You need Python 3.11+ and [uv](https://docs.astral.sh/uv/) installed. `uv` manages the virtual environment and dependencies for you.

## Install project dependencies

From the `library-management-api` folder, run:

```bash
uv sync
```

`uv` creates a virtual environment and installs the dependencies recorded in `uv.lock`.

## Run the API

```bash
uv run uvicorn app.main:app --reload
```

- FastAPI defines the routes and handles requests.
- Uvicorn listens for HTTP connections and passes them to FastAPI.
- `--reload` restarts the server automatically when source files change.

The development server is available at `http://localhost:8000`.

## Explore the API

The application exposes three views of the same OpenAPI contract:

- `http://localhost:8000/docs` — Swagger UI for exploring and calling endpoints
- `http://localhost:8000/redoc` — ReDoc for reading reference documentation
- `http://localhost:8000/openapi.json` — the machine-readable OpenAPI document

| Method | URL | CRUD operation | Successful status |
|---|---|---|---|
| `GET` | `/` | Read API introduction | `200 OK` |
| `GET` | `/health` | Read API health | `200 OK` |
| `GET` | `/books` | Read all Books | `200 OK` |
| `GET` | `/books/{book_id}` | Read one Book | `200 OK` |
| `POST` | `/books` | Create a Book | `201 Created` |
| `PUT` | `/books/{book_id}` | Update a Book | `200 OK` |
| `DELETE` | `/books/{book_id}` | Delete a Book | `204 No Content` |
| `GET` | `/members` | Read all Members | `200 OK` |
| `GET` | `/members/{member_id}` | Read one Member | `200 OK` |
| `POST` | `/members` | Create a Member | `201 Created` |
| `PUT` | `/members/{member_id}` | Update a Member | `200 OK` |
| `DELETE` | `/members/{member_id}` | Delete a Member | `204 No Content` |
| `GET` | `/members/{member_id}/books` | Read one Member's Books | `200 OK` |

## Example: create a Member

`POST /members`

```json
{
  "name": "Casey Rivera",
  "email": "casey@example.com",
  "membership_id": "MBR-1002",
  "phone": "214-555-0199"
}
```

Member validation rules:

- `name` is required, 1-120 characters after trimming surrounding whitespace.
- `email` is required, must be a valid email address, and must be unique.
- `membership_id` is required and must be unique.
- `phone` is required and must match `NNN-NNN-NNNN` (e.g. `214-555-0199`). Any other format returns `422 Unprocessable Content`.
- Unexpected fields are rejected.
- Creating or updating a Member with a duplicate `email` or `membership_id` returns `409 Conflict`.

## Example: create a Book

`POST /books`

```json
{
  "title": "Clean Code",
  "author": "Robert C. Martin",
  "isbn": "978-0132350884",
  "published_year": 2008,
  "member_id": 2
}
```

Book validation rules:

- `title` is required, 1-200 characters after trimming surrounding whitespace.
- `author` is required, 1-120 characters after trimming surrounding whitespace.
- `isbn` is required and must be unique.
- `published_year` must be between 1450 and the current year.
- `member_id` must reference an existing Member. Creating or updating a Book with a nonexistent `member_id` returns `404 Not Found`.
- Creating or updating a Book with a duplicate `isbn` returns `409 Conflict`.

## Example: retrieve a Member's Books

`GET /members/2/books`

```json
[
  {
    "title": "Clean Code",
    "author": "Robert C. Martin",
    "isbn": "978-0132350884",
    "published_year": 2008,
    "member_id": 2,
    "id": 2
  }
]
```

## The Member-Book relationship

Each Book belongs to exactly one Member (`member_id`), and a Member may have many Books. Deleting a Member who still has associated Books returns `409 Conflict`; the Books must be deleted or reassigned to a different Member first. Requesting a nonexistent Book or Member returns `404 Not Found`.

## Temporary data

Books and Members are stored in Python lists while the application is running. Changes disappear when the development server restarts. One Member (`Jordan Lee`) and one Book (`The Pragmatic Programmer`, checked out by that Member) are seeded at startup so the relationship endpoints have data to demonstrate immediately.

## Current project structure

```text
library-management-api/
├── app/
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── books.py
│   │   └── members.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── books.py
│   │   └── members.py
│   ├── __init__.py
│   ├── main.py
│   └── storage.py
├── notes/
│   └── design-notes.md
├── .gitignore
├── .python-version
├── pyproject.toml
├── README.md
└── uv.lock
```

The project uses a simple layer-first structure. Route handlers live in `app/routers/`, and API data contracts live in `app/schemas/`. A service and repository layer can be added when the course introduces the responsibilities they contain.

## Next step

A future assignment replaces the in-memory collections with database persistence.
