"""PostgreSQL engine and the session factory used by database services."""

from dataclasses import dataclass

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import Settings


@dataclass(frozen=True)
class DatabaseInfrastructure:
    """Database engine and session factory created from validated settings."""

    engine: Engine
    session_factory: sessionmaker[Session]


def create_database(settings: Settings) -> DatabaseInfrastructure:
    """Create the engine and session factory for one application instance."""

    if settings.database_url is None:
        raise ValueError("DATABASE_URL is required to create database infrastructure")

    # The engine owns the connection pool and is created once per application.
    # pool_pre_ping discards connections that PostgreSQL closed while idle.
    engine = create_engine(
        settings.database_url,
        echo=settings.database_echo_sql,
        pool_pre_ping=True,
    )

    # The factory is shared, but every service operation asks it for its own
    # Session, so a Session is never shared between concurrent requests.
    # expire_on_commit=False keeps returned objects readable after the Session
    # closes; autoflush=False makes repositories flush explicitly.
    session_factory = sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
    )
    return DatabaseInfrastructure(engine=engine, session_factory=session_factory)
