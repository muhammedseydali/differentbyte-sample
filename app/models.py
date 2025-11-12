import uuid
from database import Base  
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
# from fastapi_users.db import SQLAlchemyBaseUserTableUUID


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    message = Column(Text, nullable=False)


# class User(SQLAlchemyBaseUserTableUUID, Base):
#     __tablename__ = "users"

#     posts = relationship("New_Post", back_populates="user")


class New_Post(Base):
    __tablename__ = "Newposts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    url = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_name = Column(String, nullable=False)

    # user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    # user = relationship("User", back_populates="posts")
