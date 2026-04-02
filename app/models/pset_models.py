from sqlalchemy import String, LargeBinary
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase

import re
from datetime import datetime, timedelta
from typing import List, TypedDict
from sqlalchemy import ForeignKey, String, DateTime, Integer, Text, LargeBinary
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase


class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String, primary_key=True)
    
    hashed_password: Mapped[bytes] = mapped_column(LargeBinary)
    role: Mapped[str] = mapped_column(String)     # 'student', 'tutor', 'admin'
    
class Ticket(Base):

    class TicketRecord(TypedDict):
        when: str
        code: str
        check: str

    __tablename__ = "tickets"
 
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    username: Mapped[str] = mapped_column(String)
    problem_id: Mapped[str] = mapped_column(String, ForeignKey("problems.id", ondelete="CASCADE")) 
    records: Mapped[str] = mapped_column(Text, default="")
    track: Mapped[str] = mapped_column(Text, default="")
    expire_time: Mapped[datetime] = mapped_column(DateTime)
    state: Mapped[int] = mapped_column(Integer, default=0) # 1 - problem is solved
    #  nav
    # problem: Mapped["Problem"] = relationship(back_populates="tickets")

# --------------- record methods

    def add_record(self, solving, check_message):  
        RECORD_FORMAT = "~0~{0}\n~1~{1}\n~2~{2:%Y-%m-%d %H:%M:%S}\n~3~\n"
        self.records += RECORD_FORMAT.format(solving, check_message, datetime.now())
        if check_message.startswith("OK") and self.state == 0:
            self.state = 1
    
    def get_records(self) -> List[TicketRecord]:
        """ 
        Показ вирішень з тікету.
        """
        REGEX = r"~0~(.*?)~1~(.*?)~2~(.*?)~3~"
        matches = re.findall(REGEX, self.records, flags=re.S)
        return [{"when": m[2], "code":m[0].strip(), "check":m[1].strip()} for m in matches]

    def when_success(self) -> datetime:
        records = self.get_records()
        success_records = [r for r in records if r["check"].startswith("OK") ]
        if len(success_records) == 0:
            return datetime.min
        when = success_records[0]["when"].strip()
        return datetime.fromisoformat(when)