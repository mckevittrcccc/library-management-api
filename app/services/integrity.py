"""Helpers for turning database constraint failures into application outcomes."""

from sqlalchemy.exc import IntegrityError


def violated_constraint(error: IntegrityError) -> str | None:
    """Return the name of the constraint PostgreSQL reported, if any.

    Services pre-check the common conflicts for clear errors, but two requests
    can still race past those checks. The database constraints are the final
    guard, and this name tells the service which rule was violated.
    """
    diagnostics = getattr(error.orig, "diag", None)
    return getattr(diagnostics, "constraint_name", None)
