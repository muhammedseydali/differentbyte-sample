from fastapi import Depends
from typing import AsyncGenerator
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
# from fastapi_users.db import SQLAlchemyUserDatabase, SQLAlchemyBaseUserTableUUID

from sqlalchemy.orm import DeclarativeBase, relationship

# Use async engine for SQLite
DATABASE_URL = "sqlite+aiosqlite:///./contact.db"

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Create async session factory
async_session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

# Base class for models
class Base(DeclarativeBase):
    pass

# class User(SQLAlchemyBaseUserTableUUID, Base):
#     posts = relationship("Post", back_populates="user")

# Function to create tables
async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Dependency: async session
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

# async def get_user_db(session:AsyncSession = Depends(get_async_session)):
#     yield SQLAlchemyUserDatabase(session, User)