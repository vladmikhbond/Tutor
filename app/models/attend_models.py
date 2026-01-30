from datetime import datetime, timezone
from typing import List
from sqlalchemy import Integer, String, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase

class Base(DeclarativeBase):
    pass


class Shadule(Base):
    __tablename__ = "schedules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    username: Mapped[str] = mapped_column(String)
    classes: Mapped[str] = mapped_column(String)
    moments: Mapped[str] = mapped_column(String)     # '27/01/2026 11:15,    12/02/2026 11:15,    13/02/2026 11:15'

    @property
    def begins(self) -> List[datetime]:
        not_empty_str = map(lambda x: x.strip(), self.moments.split(','))
        return [datetime.strptime(x, "%d/%m/%Y %H:%M").replace(tzinfo=timezone.utc) 
                    for x in not_empty_str if x ]



class Snapshot(Base):
    __tablename__ = "snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    username: Mapped[str] = mapped_column(String)
    when: Mapped[datetime] = mapped_column(DateTime)
    visitors: Mapped[str] = mapped_column(Text)

    @property
    def names(self) -> List[str]:
        not_empty_str = map(lambda x: x.strip(), self.visitors.split(','))
        return [x for x in not_empty_str if x ]

