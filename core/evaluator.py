"""
Đánh giá lịch học dựa trên các ràng buộc mềm (Soft Constraints)
Dùng để tính fitness cho thuật toán GWO
"""

from typing import Dict, List, Set
from core.model import Schedule, Assignment, Course, Room, Teacher, Timeslot


class ScheduleEvaluator:
    """Lớp đánh giá lịch học"""

    def __init__(self, courses: Dict[str, Course], rooms: Dict[str, Room],
                 teachers: Dict[str, Teacher], timeslots: Dict[str, Timeslot]):
        self.courses = courses
        self.rooms = rooms
        self.teachers = teachers
        self.timeslots = timeslots

    def evaluate(self, schedule: Schedule) -> float:
        """
        Tính điểm fitness cho lịch học
        Điểm càng cao càng tốt (tối đa 100)
        
        Returns:
            Điểm fitness từ 0 đến 100
        """
        if not schedule.assignments:
            return 0.0
        
        # Tính điểm cho từng ràng buộc mềm
        score_consecutive = self._evaluate_teacher_consecutive(schedule)  # 0-50 điểm
        score_rooms = self._evaluate_room_usage(schedule)  # 0-50 điểm
        
        total_score = score_consecutive + score_rooms
        return min(100.0, total_score)

    def _evaluate_teacher_consecutive(self, schedule: Schedule) -> float:
        """
        Ràng buộc mềm 2: Hạn chế số tiết dạy liên tục của giáo viên
        
        Đếm số lần giáo viên dạy 3 tiết liên tiếp trở lên
        Điểm = 50 - (số lần vi phạm * 8.33), tối thiểu 0
        
        Returns:
            Điểm từ 0 đến 50
        """
        # Nhóm các assignment theo giáo viên
        teacher_schedules: Dict[str, List[Assignment]] = {}
        
        for assignment in schedule.assignments:
            teacher_id = assignment.teacher_id
            if teacher_id not in teacher_schedules:
                teacher_schedules[teacher_id] = []
            teacher_schedules[teacher_id].append(assignment)
        
        violations = 0
        
        for teacher_id, assignments in teacher_schedules.items():
            # Lấy danh sách timeslot và sắp xếp
            timeslot_indices = []
            for a in assignments:
                ts = self.timeslots.get(a.timeslot_id)
                if ts:
                    day_order = {"Thứ 2": 0, "Thứ 3": 1, "Thứ 4": 2, "Thứ 5": 3, "Thứ 6": 4, "Thứ 7": 5}
                    session_order = 0 if ts.session == "Sáng" else 1 if ts.session == "Chiều" else ts.period
                    index = day_order.get(ts.day, 0) * 100 + session_order * 10 + ts.period
                    timeslot_indices.append(index)
            
            timeslot_indices.sort()
            
            # Đếm số lần có 3 tiết liên tiếp trở lên
            consecutive_count = 1
            for i in range(len(timeslot_indices) - 1):
                if timeslot_indices[i + 1] - timeslot_indices[i] == 1:
                    consecutive_count += 1
                    if consecutive_count >= 3:
                        violations += 1
                        break  # Chỉ đếm 1 lần vi phạm cho mỗi giáo viên
                else:
                    consecutive_count = 1
        
        # Điểm = 50 - (số vi phạm * 8.33), tối thiểu 0
        score = max(0.0, 50.0 - violations * 8.33)
        return score

    def _evaluate_room_usage(self, schedule: Schedule) -> float:
        
        used_rooms = set()
        for assignment in schedule.assignments:
            used_rooms.add(assignment.room_id)
        
        num_courses = len(self.courses)
        num_used_rooms = len(used_rooms)
        
        # Số phòng dư thừa
        excess_rooms = max(0, num_used_rooms - num_courses)
        
        # Điểm = 50 - (số phòng dư * 5), tối thiểu 0
        score = max(0.0, 50.0 - excess_rooms * 5.0)
        return score

