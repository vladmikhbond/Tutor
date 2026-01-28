import datetime as dt
from sqlalchemy import Integer, String, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase

class Base(DeclarativeBase):
    pass


class Shadule(Base):
    __tablename__ = "schedules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    username: Mapped[str] = mapped_column(String)
    classes_name: Mapped[str] = mapped_column(String)
    moments: Mapped[str] = mapped_column(String)     # '27/01/2026 11:15,    02/02/2026 11:15,    27/01/2026 11:15'



class Snapshot(Base):
    __tablename__ = "snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    username: Mapped[str] = mapped_column(String)
    # classes: Mapped[str] = mapped_column(String)
    when: Mapped[dt.datetime] = mapped_column(DateTime)
    visitors: Mapped[str] = mapped_column(Text)
    