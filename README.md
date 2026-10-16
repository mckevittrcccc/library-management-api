# Library Management System API

The Library Management System API is a backend for managing library **Books** and **Members**. Library staff can create, view, update, and delete both resources. Each Book is checked out by exactly one Member, and a Member may have many Books. This is Assignment 2 for SDEV 3310, built on the REST, Pydantic, and OpenAPI behavior from Assignment 1 and the layered persistence practices from the course's Project and Task Management API.

## What Assignment 2 adds

- **PostgreSQL persistence** through SQLAlchemy 2.x and Psycopg. Library data survives API restarts.
- **A selectable storage backend.** PostgreSQL is the default; Assignment 1's in-memory behavior is still available with `STORAGE_BACKEND=memory`.
- **A layered structure:**
  - **Routers** handle HTTP requests, response models, and status codes.
  - **Services** contain Library business rules and transaction boundaries.
  - **Repositories** run SQLAlchemy queries and writes.
  - **ORM models** map Python classes to PostgreSQL tables.
  - **Pydantic schemas** define and validate the API contract.

## Prerequisites

- Python 3.11+ (`uv` downloads it for you if needed)
- [uv](https://docs.astral.sh/uv/)
- PostgreSQL 16 or newer, running locally on port `5432`

## Set up PostgreSQL

**macOS (Homebrew)**

```bash
brew install postgresql@18
/opt/homebrew/opt/postgresql@18/bin/pg_ctl \
  -D /opt/homebrew/var/postgresql@18 \
  -l /opt/homebrew/var/postgresql@18/server.log start
```

**Windows**

Install PostgreSQL from the [official installer](https://www.postgresql.org/download/windows/), keep port `5432`, and set the superuser password to `postgres`. The installer starts PostgreSQL as a service.

**Create the database** (any OS) from this folder:

```bash
psql -d postgres -f scripts/setup_database.sql
```

On Windows PowerShell, if `psql` is not on your `PATH`:

```powershell
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -d postgres -f scripts\setup_database.sql
```

The script creates the local `postgres` database user (password `postgres`) if it is missing, then creates the `library_management` database. It is safe to run again. These credentials are for local development only; never reuse them or commit real credentials.

## Configure the application

Copy the sample environment file:

```bash
cp .env.example .env
```

| Setting | Default | Purpose |
|---|---|---|
| `STORAGE_BACKEND` | `database` | `database` stores data in PostgreSQL. `memory` keeps temporary process-local lists that reset when the server stops. |
| `DATABASE_URL` | none | SQLAlchemy connection URL. Required when `STORAGE_BACKEND=database`. The sample value is `postgresql+psycopg://postgres:postgres@localhost:5432/library_management`. |
| `DATABASE_ECHO_SQL` | `false` | Set to `true` to print the SQL SQLAlchemy sends. |

`.env` is excluded from the repository. Settings are validated once at startup, so a missing `DATABASE_URL` or an unsupported `STORAGE_BACKEND` stops the application with a clear error.

## Install dependencies

From this folder:

```bash
uv sync
```

`uv` creates the virtual environment and installs the versions recorded in `uv.lock`.

## Run the API

```bash
uv run uvicorn app.main:app --reload
```

- FastAPI defines the routes and handles requests.
- Uvicorn listens for HTTP connections and passes them to FastAPI.
- `--reload` restarts the server automatically when source files change.

The development server is available at `http://localhost:8000`. On first startup against the database backend, the application creates the `members` and `books` tables if they do not exist. To confirm:

```bash
psql -h localhost -U postgres -d library_management -c '\dt'
```

Stop the server and start it again to verify that your data is still there.

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

Create a Member before creating Books for them. `POST /members`

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

Use the `id` returned for the Member as `member_id`. `POST /books`

```json
{
  "title": "Clean Code",
  "author": "Robert C. Martin",
  "isbn": "978-0132350884",
  "published_year": 2008,
  "member_id": 1
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

`GET /members/1/books`

```json
[
  {
    "title": "Clean Code",
    "author": "Robert C. Martin",
    "isbn": "978-0132350884",
    "published_year": 2008,
    "member_id": 1,
    "id": 1
  }
]
```

## The Member-Book relationship

Each Book belongs to exactly one Member (`member_id`), and a Member may have many Books. The database enforces this with a foreign key from `books.member_id` to `members.id`. Deleting a Member who still has associated Books returns `409 Conflict`; the Books must be deleted or reassigned first. Requesting a nonexistent Book or Member returns `404 Not Found`. API errors never include raw database messages.

## Request flow

```text
HTTP request
    ↓
Router         HTTP details, Pydantic schemas, status codes
    ↓
Service        Library rules and transaction decisions (BookService / MemberService)
    ↓
Repository     SQLAlchemy queries and writes
    ↓
PostgreSQL     durable Books and Members
```

- Routers receive a service through FastAPI dependency injection (`Depends(get_book_service)`); they never build a service, repository, or Session.
- Application startup reads the validated settings and creates either the database or the in-memory implementation of each service contract. Routers call the same abstract contract either way.
- Services raise application exceptions such as `MemberNotFoundError`; routers translate them into `HTTPException` responses in `app/routers/http_errors.py`.
- One Engine and session factory are created at startup. Each database service operation opens and closes its own Session. Write operations use `with session_factory.begin()`, which commits a completed use case and rolls back if an exception escapes. Use cases that touch both Members and Books share that single Session and transaction.
- Unique constraints (`uq_members_email`, `uq_members_membership_id`, `uq_books_isbn`) and the foreign key are the final guard; services translate a violation that slips past their checks into the same `409` or `404` outcome.

## Current project structure

```text
library-management-api/
├── app/
│   ├── database/
│   │   ├── __init__.py
│   │   └── session.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── book.py
│   │   └── member.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── books.py
│   │   └── members.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── books.py
│   │   ├── http_errors.py
│   │   └── members.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── books.py
│   │   └── members.py
│   ├── services/
│   │   ├── books/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── database.py
│   │   │   └── in_memory.py
│   │   ├── members/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── database.py
│   │   │   └── in_memory.py
│   │   ├── __init__.py
│   │   ├── in_memory_store.py
│   │   └── integrity.py
│   ├── __init__.py
│   ├── config.py
│   ├── dependencies.py
│   ├── exceptions.py
│   └── main.py
├── notes/
│   └── design-notes.md
├── scripts/
│   └── setup_database.sql
├── .env.example
├── .gitignore
├── .python-version
├── pyproject.toml
├── README.md
└── uv.lock
```

The project uses a layer-first structure so each responsibility is visible: routers, schemas, services, repositories, ORM models, and database/configuration code each live in their own package.

## Next step

Later assignments add automated testing, authentication, and database migrations.
