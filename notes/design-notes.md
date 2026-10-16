# Design notes — Assignment 2 (persistence and layered design)

Working notes, not a graded deliverable (the README is).

## Layer boundaries

- `routers/` — HTTP only. Call a service through `Depends(...)`, catch application exceptions, map them in `routers/http_errors.py`.
- `services/<resource>/base.py` — abstract contract. `database.py` and `in_memory.py` implement it. Services never import FastAPI.
- `repositories/` — SQLAlchemy queries only. They `flush()` so IDs and constraint errors surface inside the service's transaction; they never commit.
- `models/` — ORM tables. `schemas/` — API contract. Responses use `from_attributes=True` to serialize ORM objects.

## Transactions

Reads: `with session_factory() as session`. Writes: `with session_factory.begin() as session` in the service, so the whole use case commits or rolls back together. `create_book` checks the Member, checks the ISBN, and inserts in one Session/transaction.

## Duplicates and races

Services pre-check email / membership_id / ISBN for clear errors (excluding the record's own id on replace). Two requests can still race past the pre-check, so the unique constraints are named and `services/integrity.py` reads the violated constraint name from the Psycopg diagnostics. The service re-raises the same application exception the pre-check would have. The `books.member_id` foreign key does the same for a Member deleted mid-create (404) or a Book added mid-delete (409).

## Backend selection

`Settings` (pydantic-settings) validates `STORAGE_BACKEND` (`StorageBackend` enum, default `database`) and requires `DATABASE_URL` for the database backend. `lifespan` builds the matching services once and stores them on `app.state`. The in-memory backend keeps Assignment 1's seed Member and Book; the database backend starts empty.

## Out of scope

Tests, authentication, migrations (tables come from `create_all` at startup).
