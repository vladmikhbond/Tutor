import pytest
from datetime import datetime, timezone, timedelta
from app.models.attend_models import Shadule, Snapshot
from app.models.attend_report import get_column_dict, get_begin_shots_dict, list_to_str, create_matrix

def base_datetime():
    """Base datetime for testing"""
    return datetime(2026, 1, 30, 10, 0, 0)

def create_snapshot(base_datetime, minutes_offset=0, visitors="Alice,Bob"):
    """Factory fixture to create snapshots"""  
    snapshot = Snapshot()
    snapshot.visitors = visitors
    snapshot.when = base_datetime + timedelta(minutes=minutes_offset)
    return snapshot


# =========================================================

def test_Snapshot_names():
    snapshot = Snapshot()
    snapshot.visitors = "Alice, , Bob "
    assert snapshot.get_names() == ["Alice","Bob"]
    snapshot.visitors = ""
    assert snapshot.get_names() == []

    
def test_Snapshot_get_begins():
    shad = Shadule(moments = '27/01/2026 11:15,    12/02/2026 11:15,    13/02/2026 11:15')   
    bs = shad.get_begins()
    assert bs[0].day == 27    
    assert bs[1].day == 12
    assert bs[0].minute == 15

# =========================================================

def test_list_to_str():
    assert list_to_str([0,2,4], 5) == "█─█─█"


def test_get_column_dict():
    t0 = base_datetime()
    sh1 = create_snapshot(t0, 1, "111, 222, 333")
    sh2 = create_snapshot(t0, 2, "111, 222")    
    sh3 = create_snapshot(t0, 3, "111")    
    d = get_column_dict([sh1, sh2, sh3])
    assert d["111"] == "███"
    assert d["222"] == "██─"
    assert d["333"] == "█──"

def test_get_begin_shots_dict():
    dt1 = base_datetime()
    dt2 = dt1 + timedelta(days=1)
    shad = Shadule(moments=
        f"{dt1+timedelta(hours=2):%d/%m/%Y %H:%M},{ dt2+timedelta(hours=2):%d/%m/%Y %H:%M}") 

    sh1 = create_snapshot(dt1, 1, "111, 222, 333")
    sh2 = create_snapshot(dt1, 2, "111, 222")    
    sh3 = create_snapshot(dt2, 1, "111, 222, 333")
    sh4 = create_snapshot(dt2, 2, "111, 333") 
    d = get_begin_shots_dict(shad, [sh1, sh2, sh3, sh4])
    assert d[dt1] == [sh1, sh2]
    assert d[dt2] == [sh3, sh4]

def test_create_matrix():
    dt1 = base_datetime()
    dt2 = dt1 + timedelta(days=1)
    shad = Shadule(moments=
        f"{dt1+timedelta(hours=2):%d/%m/%Y %H:%M},{ dt2+timedelta(hours=2):%d/%m/%Y %H:%M}") 
    sh1 = create_snapshot(dt1, 1, "111, 222, 333")
    sh2 = create_snapshot(dt1, 2, "111, 222")    
    sh3 = create_snapshot(dt2, 1, "111, 222, 333")
    sh4 = create_snapshot(dt2, 2, "111, 333") 
    ns, bs, m = create_matrix(shad, [sh1, sh2, sh3, sh4])
    assert ns == ["111", "222", "333"] 
    assert bs == [dt1, dt2]
    assert m[0][0] == "██"
    assert m[1][1] == "█─"