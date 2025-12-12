"""Database session management for Gospel Keys

Provides async SQLAlchemy session factory and database dependency injection.
"""

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings

# Database URL for SQLite with async driver
DATABASE_URL = f"sqlite+aiosqlite:///{settings.base_dir}/gospel_keys.db"

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL query logging
    future=True,
)

# Create async session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db():
    """
    Dependency that provides a database session
    
    Usage in FastAPI routes:
        @router.get("/songs")
        async def list_songs(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with async_session_maker() as session:
        yield session


async def init_db():
    """Initialize database schema - creates all tables"""
    from app.database.models import Base
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """Close database connection pool"""
    await engine.dispose()
