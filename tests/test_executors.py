import pytest
from datetime import datetime, timezone, timedelta
from app.models.attend_models import Shadule, Snapshot
from app.models.attend_report import list_to_str

def base_datetime():
    """Base datetime for testing"""
    return datetime(2026, 1, 30, 10, 0, 0, tzinfo=timezone.utc)

def create_snapshot(base_datetime):
    """Factory fixture to create snapshots"""
    def _create_snapshot(minutes_offset=0, visitors="Alice,Bob"):
        snapshot = Snapshot()
        snapshot.visitors = visitors
        snapshot.when = base_datetime + timedelta(minutes=minutes_offset)
        return snapshot
    return _create_snapshot

# =========================================================

def test_Snapshot_names():
    snapshot = Snapshot()
    snapshot.visitors = "Alice, , Bob "
    assert snapshot.names == ["Alice","Bob"]
    snapshot.visitors = ""
    assert snapshot.names == []


def test_list_to_str():
    assert list_to_str([0,2,4], 5) == "+-+-+"

    
def test_begins():
    shad = Shadule(moments = '27/01/2026 11:15,    12/02/2026 11:15,    13/02/2026 11:15')   
    bs = shad.begins
    assert bs[0].day == 27    
    assert bs[1].day == 12
    assert bs[0].minute == 15

# def test_matrix():
#     t0 = base_datetime()
#     sh1 = create_snapshot(t0)(1, "111, 222, 333")
#     sh2 = create_snapshot(t0)(2, "111, 222")    
#     sh3 = create_snapshot(t0)(3, "111")    
#     les = Lesson(t0, [sh1, sh2, sh3])
#     d = les.attend_dict()
#     assert d["111"] == "+++"
#     assert d["222"] == "++-"
#     assert d["333"] == "+--"