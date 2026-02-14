from datetime import datetime, timedelta, timezone
from typing import Dict, List, Set
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
        for name in shot.names:
            if name in dic:
                dic[name].append(i)
            else:
                dic[name] = [i]
    dic2: Dict[str, str] = dict()
    n = len(shots)
    for k in dic:
        dic2[k] = list_to_str(dic[k], n)

    return dic2 


def get_shadule_dict(shad: Shadule, shots: List[Snapshot]) -> Dict[datetime, List[Shadule]]:
    """
    Поділяємо знімки на заняття за розкладом
    """
    lesson_dict: dict[int, List[Snapshot]] = dict()

    for b in shad.begins:
        end = b + timedelta(minutes=95)
        for shot in shots:
            if b <= shot.when <= end:
                if b in lesson_dict:
                    lesson_dict[b].append(shot)
                else:
                    lesson_dict[b] = [shot]
    return lesson_dict



def create_matrix(shad: Shadule, shots: List[Snapshot]):
    """
    З розкладу і знімків будуємо матрицю відвідувань
    """
    shad_dict = get_shadule_dict(shad, shots)
    column_dict_list = [get_column_dict(shad_dict[b]) for b in shad_dict]

    # all names
    sets = map(lambda x: set(x.keys()), column_dict_list)
    names = sorted(list(set().union(*sets)))
    # all begins
    begins = shad.begins

    # create matrix with column of names
    matrix = []
    for name in names:
        row = []
        for col_dict in column_dict_list:
            if name in col_dict:
                row.append(col_dict[name])
            else: 
                row.append("")
        matrix.append(row)

    return names, begins, matrix 

    
        






    
    


        

    
        
    
    