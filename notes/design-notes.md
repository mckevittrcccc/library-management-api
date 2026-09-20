# Design notes — Assignment 1 (Library Management System API)

Working notes for my own reference. Not a graded deliverable (the README is).

## Resources and fields (from the assignment docx)

**Book**: id (server), title (1-200, trimmed), author (1-120, trimmed), isbn (unique), published_year (1450..current year), member_id (must reference an existing Member).

**Member**: id (server), name (1-120, trimmed), email (EmailStr, unique), membership_id (unique), phone (required, "follow and document one validation rule").

Chosen phone rule: must match `NNN-NNN-NNNN` (e.g. `214-555-0199`), enforced with a `field_validator` + documented in the field description and README. This is the "one validation rule" the assignment asks for and to document.

## Relationship

One Member -> many Books, via `Book.member_id`. Mirrors the Project->Task pattern in `project-task-api`:
- `find_member()` in `app/routers/members.py` raises 404 if missing; `books.py` imports and calls it before creating/replacing a Book.
- `GET /members/{id}/books` mirrors `GET /projects/{id}/tasks`.
- Deleting a Member with Books returns 409 (mirrors blocked Project delete), not a cascade delete — assignment explicitly requires this ("must first be deleted or reassigned").

## Duplicate checks (409 Conflict)

The reference project didn't need uniqueness checks (Projects/Tasks have no unique fields). This assignment requires ISBN, email, and membership_id to be unique, so I added `_check_unique_isbn` in books.py and `_check_unique` in members.py, both used on create and on replace (excluding the record's own id during replace so an unchanged PUT doesn't conflict with itself).

## Scope boundaries respected

- No persistence yet — plain in-memory lists in `storage.py`, per the assignment's explicit scope boundary.
- No automated tests — not introduced yet in the course; I tested manually with curl instead (see below).
- Followed the same schema pattern as the reference project: `*Base` (shared fields + `model_config` with `extra="forbid"`, `str_strip_whitespace=True`, `frozen=True`), `*Input` (create/replace body), `*Response` (adds server-generated `id`).

## Manual verification performed (all passed)

Ran the app with `uv run uvicorn app.main:app --port 8123` and exercised with curl:
- 200 on GET /members, /books, /members/{id}/books
- 201 on valid POST /members and POST /books
- 409 on duplicate email, duplicate membership_id, duplicate isbn
- 422 on malformed phone, on published_year below 1450
- 404 on POST /books with a nonexistent member_id, and on GET of a deleted member
- 409 on DELETE /members/{id} when that member still has a book
- 204 on DELETE /books/{id} and, after that, DELETE /members/{id} succeeds
