"""
Mô hình dữ liệu cho bài toán xếp lịch môn học
"""

from dataclasses import dataclass
from typing import List, Optional, Dict


@dataclass
class Teacher:
    """Lớp đại diện cho giáo viên"""
    id: str
    name: str
    courses: List[str]


@dataclass
class Room:
    """Lớp đại diện cho phòng học"""
    id: str
    name: str
    capacity: int
    location: str  # "A", "B", hoặc "N"


@dataclass
class Course:
    """Lớp đại diện cho môn học"""
    id: str
    name: str
    student_class: str
    required_location: str  # "A", "B", "N", hoặc "A|B"


@dataclass
class Timeslot:
    """Lớp đại diện cho khung giờ học"""
    id: str
    day: str
    period: int
    time: str
    session: str = ""  # "Sáng" hoặc "Chiều" (optional để tương thích ngược)


@dataclass
class Assignment:
    """Lớp đại diện cho một gán lịch (môn - phòng - giáo viên - timeslot)"""
    course_id: str
    room_id: str
    teacher_id: str
    timeslot_id: str

    def __eq__(self, other):
        if not isinstance(other, Assignment):
            return False
        return (self.course_id == other.course_id and
                self.room_id == other.room_id and
                self.teacher_id == other.teacher_id and
                self.timeslot_id == other.timeslot_id)

    def __hash__(self):
        return hash((self.course_id, self.room_id, self.teacher_id, self.timeslot_id))


@dataclass
class Schedule:
    """Lớp đại diện cho một lịch học hoàn chỉnh"""
    assignments: List[Assignment]

    def __init__(self, assignments: Optional[List[Assignment]] = None):
        self.assignments = assignments if assignments else []

    def add_assignment(self, assignment: Assignment):
        """Thêm một gán lịch vào lịch"""
        self.assignments.append(assignment)

    def copy(self):
        """Tạo bản sao của lịch"""
        return Schedule([Assignment(a.course_id, a.room_id, a.teacher_id, a.timeslot_id)
                        for a in self.assignments])

