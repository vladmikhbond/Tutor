import pytest
from datetime import datetime, timezone, timedelta
from app.models.attend_models import Lesson, Snapshot, list_to_str


# @pytest.fixture
def base_datetime():
    """Base datetime for testing"""
    return datetime(2026, 1, 30, 10, 0, 0, tzinfo=timezone.utc)


# @pytest.fixture
def create_snapshot(base_datetime):
    """Factory fixture to create snapshots"""
    def _create_snapshot(minutes_offset=0, visitors="Alice,Bob"):
        snapshot = Snapshot()
        snapshot.visitors = visitors
        snapshot.when = base_datetime + timedelta(minutes=minutes_offset)
        return snapshot
    return _create_snapshot

def test_Snapshot_names():
    snapshot = Snapshot()
    snapshot.visitors = "Alice, , Bob "
    assert snapshot.names == ["Alice","Bob"]
    snapshot.visitors = ""
    assert snapshot.names == []


def test_list_to_str():
    assert list_to_str([0,2,4], 5) == "+-+-+"

def test_matrix():
    t0 = base_datetime()
    sh1 = create_snapshot(t0)(1, "111, 222, 333")
    sh2 = create_snapshot(t0)(2, "111, 222")    
    sh3 = create_snapshot(t0)(3, "111")    
    les = Lesson(t0, [sh1, sh2, sh3])
    d = les.matrix()
    assert d["111"] == "+++"
    assert d["222"] == "++-"
    assert d["333"] == "+--"
    
    print(dic)


# class TestLesson:
#     """Test suite for Lesson class"""

#     def test_lesson_initialization(self, base_datetime, create_snapshot):
#         """Test that Lesson initializes with correct begin and end times"""
#         snapshots = [create_snapshot(0), create_snapshot(30)]
#         lesson = Lesson(base_datetime, snapshots)
        
#         assert lesson.begin == base_datetime
#         assert lesson.end == base_datetime + timedelta(minutes=95)

#     def test_lesson_filters_snapshots_outside_range(self, base_datetime, create_snapshot):
#         """Test that snapshots outside the lesson time range are filtered out"""
#         snapshots = [
#             create_snapshot(-10),  # Before lesson
#             create_snapshot(30),   # Within lesson
#             create_snapshot(96),   # After lesson
#         ]
#         lesson = Lesson(base_datetime, snapshots)
        
#         # Should only contain the snapshot at 30 minutes
#         assert len(lesson.shots) == 1
#         assert lesson.shots[0].when == base_datetime + timedelta(minutes=30)

#     def test_lesson_filters_empty_visitors(self, base_datetime, create_snapshot):
#         """Test that snapshots with empty visitors are filtered out"""
#         snapshots = [
#             create_snapshot(10, "Alice,Bob"),
#             create_snapshot(20, ""),          # Empty
#             create_snapshot(30, "   "),       # Whitespace only
#             create_snapshot(40, "Charlie"),
#         ]
#         lesson = Lesson(base_datetime, snapshots)
        
#         # Should only contain snapshots with visitors
#         assert len(lesson.shots) == 2

#     def test_lesson_sorts_snapshots_by_time(self, base_datetime, create_snapshot):
#         """Test that snapshots are sorted chronologically"""
#         snapshots = [
#             create_snapshot(60),
#             create_snapshot(10),
#             create_snapshot(40),
#         ]
#         lesson = Lesson(base_datetime, snapshots)
        
#         # Verify shots are sorted
#         for i in range(len(lesson.shots) - 1):
#             assert lesson.shots[i].when <= lesson.shots[i + 1].when

#     def test_matrix_single_snapshot(self, base_datetime, create_snapshot):
#         """Test matrix method with a single snapshot"""
#         snapshots = [create_snapshot(10, "Alice,Bob")]
#         lesson = Lesson(base_datetime, snapshots)
        
#         matrix = lesson.matrix()
        
#         assert "Alice" in matrix
#         assert "Bob" in matrix
#         assert matrix["Alice"] == "+"
#         assert matrix["Bob"] == "+"

#     def test_matrix_multiple_snapshots(self, base_datetime, create_snapshot):
#         """Test matrix method with multiple snapshots"""
#         snapshots = [
#             create_snapshot(10, "Alice,Bob"),
#             create_snapshot(30, "Alice,Charlie"),
#             create_snapshot(50, "Bob,Charlie"),
#         ]
#         lesson = Lesson(base_datetime, snapshots)
        
#         matrix = lesson.matrix()
        
#         # Alice present in snapshots 0 and 1
#         assert matrix["Alice"] == "++-"
#         # Bob present in snapshots 0 and 2
#         assert matrix["Bob"] == "+-+"
#         # Charlie present in snapshots 1 and 2
#         assert matrix["Charlie"] == "-++"

#     def test_matrix_no_snapshots(self, base_datetime):
#         """Test matrix method with no valid snapshots"""
#         lesson = Lesson(base_datetime, [])
        
#         matrix = lesson.matrix()
        
#         assert matrix == {}

#     def test_matrix_participant_in_all_snapshots(self, base_datetime, create_snapshot):
#         """Test matrix method for participant present in all snapshots"""
#         snapshots = [
#             create_snapshot(10, "Alice,Bob"),
#             create_snapshot(30, "Alice,Charlie"),
#             create_snapshot(50, "Alice,Dave"),
#         ]
#         lesson = Lesson(base_datetime, snapshots)
        
#         matrix = lesson.matrix()
        
#         assert matrix["Alice"] == "+++"

#     def test_matrix_participant_in_no_snapshots(self, base_datetime, create_snapshot):
#         """Test that participants who appear in some snapshots are tracked"""
#         snapshots = [
#             create_snapshot(10, "Alice"),
#             create_snapshot(30, "Bob"),
#             create_snapshot(50, "Charlie"),
#         ]
#         lesson = Lesson(base_datetime, snapshots)
        
#         matrix = lesson.matrix()
        
#         assert matrix["Alice"] == "+-"
#         assert matrix["Bob"] == "-+-"
#         assert matrix["Charlie"] == "--+"

#     def test_list_to_str_helper(self):
#         """Test the list_to_str helper function"""
#         # Test with attended indices
#         result = list_to_str([0, 2], 3)
#         assert result == "+-+"
        
#         # Test with no attendance
#         result = list_to_str([], 3)
#         assert result == "---"
        
#         # Test with full attendance
#         result = list_to_str([0, 1, 2], 3)
#         assert result == "+++"

#     def test_lesson_boundary_conditions(self, base_datetime, create_snapshot):
#         """Test snapshots at exact lesson boundaries"""
#         snapshots = [
#             create_snapshot(0),      # Exactly at start
#             create_snapshot(95),     # Exactly at end
#             create_snapshot(96),     # Just after end
#         ]
#         lesson = Lesson(base_datetime, snapshots)
        
#         # Snapshots at boundaries should be included
#         assert len(lesson.shots) == 2

#     def test_lesson_with_special_characters_in_names(self, base_datetime, create_snapshot):
#         """Test handling of names with special characters"""
#         snapshots = [create_snapshot(10, "Алексій,Марія,José")]
#         lesson = Lesson(base_datetime, snapshots)
        
#         matrix = lesson.matrix()
        
#         assert "Алексій" in matrix
#         assert "Марія" in matrix
#         assert "José" in matrix

#     def test_lesson_with_duplicate_names_in_snapshot(self, base_datetime):
#         """Test handling when a name appears twice in same snapshot"""
#         snapshot = Snapshot()
#         snapshot.visitors = "Alice,Alice,Bob"
#         snapshot.when = base_datetime + timedelta(minutes=10)
        
#         lesson = Lesson(base_datetime, [snapshot])
#         matrix = lesson.matrix()
        
#         # Should handle duplicates gracefully
#         assert "Alice" in matrix
#         assert "Bob" in matrix
