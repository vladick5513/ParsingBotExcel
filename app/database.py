from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, declared_attr
from app.config import settings

async_engine = create_async_engine(url=settings.DATABASE_URL_asyncpg, echo=True)

async_session_factory = async_sessionmaker(async_engine, expire_on_commit=False)

class Base(DeclarativeBase):
    __abstract__ = True
