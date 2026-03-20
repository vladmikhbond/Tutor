from datetime import datetime, timedelta, timezone
from typing import Dict, List, Set, Tuple
from .attend_models import Snapshot, Shadule

def list_to_str(ints: List[int], n):
    return ''.join('█' if i in ints else '─' for i in range(n))
    
def get_column_dict(shots: List[Snapshot]) -> Dict[str, str]:
    """
    Створює словник відвідувань одного заняття. Ключі - імена, значення - рядки.
    d["Іван Петренко"] == "─██──█"
    """
    # dic["Іван Петренко"] = [1, 2, 5]
    dic: dict[str, List[int]] = dict()   
    for i, shot in enumerate(shots):
        for name in shot.get_names():
            if name in dic:
                dic[name].append(i)
            else:
                dic[name] = [i]

    # dic["Іван Петренко"] = "─██──█"
    dic2: Dict[str, str] = dict()
    n = len(shots)
    for k in dic:
        dic2[k] = list_to_str(dic[k], n)

    return dic2 


def get_begin_shots_dict(shad: Shadule, shots: List[Snapshot]) -> Dict[datetime, List[Snapshot]]:
    """
    Створює словник, який поділяє знімки на заняття.  
    d["12-1-2026 7:45"] == [shot1, shot2, shot3, shot4]
    Ключ - дата-час початку, значення - список знимків того заняття, 
    зроблених на протязі півтори години з початку заняття.
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
        
def create_matrix(shad: Shadule, shots: List[Snapshot]) -> Tuple[List[datetime], Matrix]:
    """
    З розкладу і знімків будуємо матрицю відвідувань
    """
    begin_shots_dict: Dict[datetime, List[Snapshot]] = get_begin_shots_dict(shad, shots)
    
    # словник словнків для колонок матриці
    # { time: {name : lines} } 
    column_dict_dict: Dict[datetime, Dict[str, str]] = \
        {begin : get_column_dict(begin_shots_dict[begin]) for begin in begin_shots_dict}

    # all names - the left headers of matrix
    sets = map(lambda x: set(x.keys()), column_dict_dict.values())
    names = list(set().union(*sets))

    # all begins - the upper headers of matrix
    begins = shad.get_begins()

    # create matrix 
    matrix: Matrix = []
    for name in names:
        row: List[str] = [name]
        for begin in begins:
            col_dict = column_dict_dict.get(begin, dict())
            if name in col_dict:
                row.append(col_dict[name])
            else: 
                row.append("")
        matrix.append(row)

    # normalize names  
    for row in matrix:
        arr = row[0].split()
        if len(arr) == 2:
            """ John Doe -> Doe John """
            row[0] = f"{arr[1]} {arr[0]}"
     
    matrix.sort(key=lambda r: r[0])

    return begins, matrix 
