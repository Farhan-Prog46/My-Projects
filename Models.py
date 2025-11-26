from sqlalchemy.orm import declarative_base, Mapped, mapped_column, Session
from sqlalchemy import Column, ForeignKey, Integer, String, Text, DateTime
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    user_id: Mapped[int] = \
        mapped_column(Integer, primary_key=True)
    username: Mapped[str] = \
        mapped_column(String(50), nullable=False, unique = True)
    password_hash: Mapped[str] = \
        mapped_column(String(100), nullable=False)
    
class Message(Base):
    __tablename__ = "messages"
    id: Mapped[int] = \
        mapped_column(Integer, primary_key=True, autoincrement=True)
    sender: Mapped[str] = \
        mapped_column(String(50), ForeignKey("users.username"), nullable=False)
    content: Mapped[str] = \
        mapped_column(Text, nullable=False)
    timestamp: Mapped[datetime] = \
        mapped_column(DateTime, default=datetime.utcnow, nullable=False)