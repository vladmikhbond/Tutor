from datetime import datetime, timezone
from typing import List

from sqlalchemy import Integer, String, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from ..routers.utils import str_to_time

class Base(DeclarativeBase):
    pass


class Shadule(Base):
    __tablename__ = "schedules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    username: Mapped[str] = mapped_column(String)
    classes: Mapped[str] = mapped_column(String)
    moments: Mapped[str] = mapped_column(String)     # (за Київом) '27/01/2026 11:15,    12/02/2026 11:15,    13/02/2026 11:15'


    def get_begins(self) -> List[datetime]:
        not_empty_str = map(lambda x: x.strip(), self.moments.split(','))
        return [str_to_time(x, "%d/%m/%Y %H:%M") for x in not_empty_str if x ]
    
    def moments_ok(self):
        try:
            self.get_begins()
        except Exception as e:
            return e
        else: 
            return "ok"



class Snapshot(Base):
    __tablename__ = "snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    username: Mapped[str] = mapped_column(String)
    when: Mapped[datetime] = mapped_column(DateTime)
    visitors: Mapped[str] = mapped_column(Text)


    def get_names(self) -> List[str]:
        not_empty_str = map(lambda x: x.strip(), self.visitors.split(','))
        return [x for x in not_empty_str if x ]

# --------------------- лог відвіування лекцій ---------------

class Log(Base):
    __tablename__ = "logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String)
    when: Mapped[datetime] = mapped_column(DateTime)
    body: Mapped[str] = mapped_column(Text)

