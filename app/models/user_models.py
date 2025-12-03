
import datetime as dt
from sqlalchemy import ForeignKey, String, DateTime, Integer, Text, LargeBinary, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from ..lectorium.parser import Parser

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String, primary_key=True)
    hashed_password: Mapped[bytes] = mapped_column(LargeBinary)
    role: Mapped[str] = mapped_column(String)
    