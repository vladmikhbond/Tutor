from datetime import datetime, timedelta, timezone
from typing import Dict, List, Set
from .attend_models import Snapshot, Shadule

def list_to_str(ints: List[int], n):
    return ''.join('+' if i in ints else '-' for i in range(n))
    
def attend_dict(snapshots: List[Snapshot]) -> Dict[str, str]:
    """
    Створює словник відвідувань одного заняття. Ключі - імена, значення - рядки.
    d["Іван"] == "+++"
    """
    
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

    
        






    
    


        

    
        
    
    