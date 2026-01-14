"""Database session management"""

import os
from contextlib import contextmanager, asynccontextmanager
from typing import Generator, AsyncGenerator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from alembic.config import Config
from alembic import command

from fork_backend.core.auth import hash_password
from fork_backend.models.system import System
from fork_backend.models.user import User
from fork_backend.models.goals import Goals

# --- Sync database setup ---
PG_USER = os.environ.get("FORK_POSTGRES_USER", default="fork_user")
PG_PW = os.environ.get("FORK_POSTGRES_PASSWORD", default="fork_password")
PG_URL = os.environ.get("FORK_POSTGRES_URL", default="localhost:5432")
PG_DB = os.environ.get("FORK_POSTGRES_DB_NAME", default="fork_db")

SQLALCHEMY_DATABASE_URL = f"postgresql://{PG_USER}:{PG_PW}@{PG_URL}/{PG_DB}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)

# --- Async database setup ---
ASYNC_SQLALCHEMY_DATABASE_URL = f"postgresql+asyncpg://{PG_USER}:{PG_PW}@{PG_URL}/{PG_DB}"

async_engine = create_async_engine(
    ASYNC_SQLALCHEMY_DATABASE_URL,
    echo=False,
)

AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


@contextmanager
def get_sync_db() -> Generator[Session, None, None]:
    """
    Context manager that yields a database session.
    The session is closed automatically when the context block exits.
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

def get_sync_db_fastapi() -> Generator[Session, None, None]:
    """
    FastAPI dependency without contextmanager decorator.
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@asynccontextmanager
async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Async context manager that yields an async database session.
    The session is closed automatically when the context block exits.
    """
    session = AsyncSessionLocal()
    try:
        yield session
    finally:
        await session.close()

async def get_async_db_fastapi() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency without contextmanager decorator.
    """
    session = AsyncSessionLocal()
    try:
        yield session
    finally:
        await session.close()

def create_admin_user() -> None:
    """Create admin user if it doesn't exist"""
    # Get admin credentials from environment or use defaults
    with get_sync_db() as session:
        admin_username = os.getenv("FORK_BACKEND_ADMIN_USERNAME", "admin")
        admin_email = os.getenv("FORK_BACKEND_ADMIN_EMAIL", "fork-admin@example.com")
        admin_password = os.getenv("FORK_BACKEND_ADMIN_PASSWORD", "admin")
        
        existing_admin = session.query(User).filter(
            (User.username == admin_username) | (User.email == admin_email)
        ).first()
        
        if not existing_admin:
            hashed_password = hash_password(admin_password)
            admin_user = User(
                id="admin",
                username=admin_username,
                email=admin_email,
                hashed_password=hashed_password,
            )
            goals = Goals(user_id=admin_user.id)

            session.add(admin_user)
            session.add(goals)

            session.commit()
            print(f"Admin user created: {admin_username}")
        else:
            print(f"Admin user already exists: {existing_admin.username}")


def create_system_row() -> None:
    """Create the initial row in System table"""
    with get_sync_db() as session:
        existing_system_row = session.query(System).first()
        
        if existing_system_row:
            print("System row already exists")
            return

        session.add(System())
        session.commit()
        print("System row created")





def init_db():
    """Initialize database - create tables and enable extensions"""
    
    # with engine.connect() as conn:
    #     # Enable pgvector extension
    #     conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    #     conn.commit()
    
    # # Now create all tables
    # Base.metadata.create_all(bind=engine)
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    create_admin_user()
    create_system_row()

async def init_db_async():
    """Async version - initialize database"""
    
    # async with async_engine.begin() as conn:
    #     # Enable pgvector extension
    #     await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        
    #     # Create all tables
    #     await conn.run_sync(Base.metadata.create_all)
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")

    create_admin_user()
    create_system_row()