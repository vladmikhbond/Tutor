from datetime import datetime, timedelta, timezone
from typing import Dict, List, Set, Tuple
from .attend_models import Snapshot, Shadule

def list_to_str(ints: List[int], n):
    return ''.join('█' if i in ints else '─' for i in range(n))
    
def get_column_dict(shots: List[Snapshot]) -> Dict[str, str]:
    """
    Створює словник відвідувань одного заняття. Ключі - імена, значення - рядки.
    d["Іван"] == "+++"
    """
    
    dic: dict[str, List[int]] = dict()
    for i, shot in enumerate(shots):
        for name in shot.get_names():
            if name in dic:
                dic[name].append(i)
            else:
                dic[name] = [i]
    dic2: Dict[str, str] = dict()
    n = len(shots)
    for k in dic:
        dic2[k] = list_to_str(dic[k], n)

    return dic2 


def get_begin_shots_dict(shad: Shadule, shots: List[Snapshot]) -> Dict[datetime, List[Snapshot]]:
    """
    Створює словник, який поділяє знімки на заняття. Ключ - дата-час початку, значення - список знимків того заняття.
    d["12-1-2026 7:45"] == [shot1, shot2, shot3, shot4]

    """
    lesson_dict: dict[datetime, List[Snapshot]] = dict()

    for begin in shad.get_begins():
        end = begin + timedelta(seconds=95*60)
        for shot in shots:
            if begin <= shot.when <= end:
                if begin in lesson_dict:
                    lesson_dict[begin].append(shot)
                else:
                    lesson_dict[begin] = [shot]
    return lesson_dict


type Matrix = List[List[str]]
        
def create_matrix(shad: Shadule, shots: List[Snapshot]) -> Tuple[List[str], Matrix, List[str]]:
    """
    З розкладу і знімків будуємо матрицю відвідувань
    """
    begin_shots_dict: Dict[datetime, List[Snapshot]] = get_begin_shots_dict(shad, shots)

    column_dict_list: Dict[datetime, Dict[str, str]] = \
        {begin : get_column_dict(begin_shots_dict[begin]) for begin in begin_shots_dict}

    # all names - left header
    sets = map(lambda x: set(x.keys()), column_dict_list.values())
    names = sorted(list(set().union(*sets)))

    # all begins - upper header
    begins = shad.get_begins()

    # create matrix 
    matrix: Matrix = []
    for name in names:
        row: List[str] = []
        for begin in begins:
            col_dict = column_dict_list.get(begin, dict())
            if name in col_dict:
                row.append(col_dict[name])
            else: 
                row.append("")
        matrix.append(row)

    return names, begins, matrix 
