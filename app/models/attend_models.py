from datetime import datetime, timedelta, timezone
from typing import List
from sqlalchemy import Boolean, Integer, String, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase

class Base(DeclarativeBase):
    pass


class Shadule(Base):
    __tablename__ = "schedules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    username: Mapped[str] = mapped_column(String)
    classes: Mapped[str] = mapped_column(String)
    moments: Mapped[str] = mapped_column(String)     # '27/01/2026 11:15,    02/02/2026 11:15,    27/01/2026 11:15'

    @property
    def moments_dt(self) -> List[datetime]:
        return (self.moments.split(',')
                       .map(lambda m: m.strip())
                       .filter(Boolean)
                       .map(lambda m: datetime
                            .strptime(m, "%d/%m/%Y %H:%M") 
                            .replace(tzinfo=timezone.utc) ))



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


# ===================== Not for DB ===================
    
class Lesson:
    """
    Одне заняття: початок, кінець, упорядкований список знімків
    """
    begin: datetime
    end: datetime
    shots: List[Snapshot]

    def __init__(self, begin: datetime, shots:List[Snapshot]):
        self.begin = begin
        self.end = begin + timedelta(minutes=95)
        shots = [s for s in shots if self.begin <= s.when <= self.end and s.visitors.strip() != ""]
        self.shots = sorted(shots, key=lambda s: s.when)
    
    def matrix(self):
        """
        Словник відвідувань одного заняття.
        """
        dic: dict[str, List[int]] = dict()
        for i, shot in enumerate(self.shots):
            for name in shot.names:
                if name in dic:
                    dic[name].append(i)
                else:
                    dic[name] = [i]
        dic2: dict[str, str] = dict()
        n = len(self.shots)
        for k in dic:
            dic2[k] = list_to_str(dic[k], n)
        return dic2 


def list_to_str(ints: List[int], n):
    return ''.join('+' if i in ints else '-' for i in range(n))



        
        

    
        
    
    