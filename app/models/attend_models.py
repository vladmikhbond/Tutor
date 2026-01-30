from datetime import datetime, timedelta, timezone
from typing import Dict, List, Set
from sqlalchemy import Boolean, Integer, String, DateTime, Text
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


# ===================== Not for DB ===================
    

    
def attend_dict(snapshots: List[Snapshot]) -> Dict[str, str]:
    """
    Створює словник відвідувань одного заняття. Ключі - імена, значення - рядки.
    d["Іван"] == "+++"
    """
    def list_to_str(ints: List[int], n):
        return ''.join('+' if i in ints else '-' for i in range(n))
    # ------------
    
    dic: dict[str, List[int]] = dict()
    for i, shot in enumerate(snapshots):
        for name in shot.names:
            if name in dic:
                dic[name].append(i)
            else:
                dic[name] = [i]
    dic2: Dict[str, str] = dict()
    n = len(snapshots)
    for k in dic:
        dic2[k] = list_to_str(dic[k], n)

    return dic2 


def get_lesson_dict(shad: Shadule, shots: List[Snapshot]):
    """
    Поділяємо знімки на заняття за розкладом
    """
    lesson_dict: dict[int, List[Snapshot]] = dict()

    for i, begin in enumerate(shad.begins):
        end = begin + timedelta(minutes=95)
        for shot in shots:
            if begin <= shot.when <= end:
                if i in lesson_dict:
                    lesson_dict[i].append(shot)
                else:
                    lesson_dict[i] = [shot]
    return lesson_dict



def create_matrix(shad: Shadule, shots: List[Snapshot]):
    """
    з тих словників будуємо матрицю відвідувань
    """
    lesson_dict = get_lesson_dict(shad, shots)
    col_dict_list: List[Dict[str, str]] = [attend_dict(lesson_dict[i]) for i in lesson_dict]

    # find all names
    sets = map(lambda x: Set(x.keys()), col_dict_list)
    names = sorted(List(Set().union(*sets)))

    # create empty matrix with column of names
    matrix = []
    for name in names:
        row = []
        for col_dict in col_dict_list:
            if name in col_dict:
                row.append(col_dict[name])
            else: 
                row.append("")
        matrix.append[row]

    return names, matrix 

    
        






    
    


        

    
        
    
    