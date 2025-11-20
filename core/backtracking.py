"""
Thuật toán Backtracking để tìm lịch hợp lệ

Tìm kiếm tất cả các tổ hợp có thể để gán môn học vào lịch,
đảm bảo thỏa mãn tất cả ràng buộc cứng.
"""

import random
from typing import Dict, List, Optional, Tuple
from core.model import Schedule, Assignment, Course, Room, Teacher, Timeslot
from core.constraint import ConstraintChecker


class BacktrackingSolver:
    """
    Lớp giải bài toán xếp lịch bằng Backtracking
    
    Thuật toán:
    1. Sắp xếp môn học theo độ khó (môn có ít lựa chọn trước)
    2. Duyệt từng môn, thử tất cả tổ hợp (giáo viên, phòng, timeslot)
    3. Kiểm tra ràng buộc trước khi gán
    4. Quay lui nếu không tìm được giải pháp
    """

    def __init__(self, courses: Dict[str, Course], rooms: Dict[str, Room],
                 teachers: Dict[str, Teacher], timeslots: Dict[str, Timeslot]):
        """
        Khởi tạo solver
        
        Args:
            courses: Dictionary các môn học
            rooms: Dictionary các phòng học
            teachers: Dictionary các giáo viên
            timeslots: Dictionary các khung giờ
        """
        self.courses = courses
        self.rooms = rooms
        self.teachers = teachers
        self.timeslots = timeslots
        self.constraint_checker = ConstraintChecker(courses, rooms, teachers, timeslots)
        
        # Tạo mapping từ tên môn đến danh sách giáo viên có thể dạy
        self.course_to_teachers = self._build_course_teacher_mapping(teachers)

    def _build_course_teacher_mapping(self, teachers: Dict[str, Teacher]) -> Dict[str, List[str]]:
        """
        Xây dựng mapping từ tên môn đến danh sách giáo viên có thể dạy
        
        Returns:
            Dictionary: {course_name: [teacher_id1, teacher_id2, ...]}
        """
        mapping = {}
        for teacher_id, teacher in teachers.items():
            for course_name in teacher.courses:
                if course_name not in mapping:
                    mapping[course_name] = []
                mapping[course_name].append(teacher_id)
        return mapping

    def solve(self, max_iterations: int = 10000, verbose: bool = False) -> Optional[Schedule]:
        """
        Giải bài toán bằng Backtracking
        
        Args:
            max_iterations: Số lần thử tối đa (không dùng trong backtracking nhưng giữ để tương thích)
            verbose: In thông tin debug
            
        Returns:
            Schedule hợp lệ nếu tìm được, None nếu không
        """
        schedule = Schedule()
        course_ids = list(self.courses.keys())
        
        # Sắp xếp môn học theo độ khó (môn có ít lựa chọn hơn trước)
        # Điều này giúp phát hiện xung đột sớm hơn
        course_ids.sort(key=lambda cid: self._calculate_course_difficulty(cid))
        
        if verbose:
            print(f"  Đang tìm lịch cho {len(course_ids)} môn học...")
            print(f"  Thứ tự xử lý: {[self.courses[cid].name for cid in course_ids[:5]]}...")
        
        if self._backtrack(schedule, course_ids, 0, verbose):
            return schedule
        return None

    def _backtrack(self, schedule: Schedule, course_ids: List[str], 
                   index: int, verbose: bool = False) -> bool:
        """
        Hàm đệ quy Backtracking
        
        Args:
            schedule: Lịch hiện tại
            course_ids: Danh sách ID môn học cần gán
            index: Chỉ số môn học hiện tại đang xử lý
            verbose: In thông tin debug
            
        Returns:
            True nếu tìm được lịch hợp lệ, False nếu không
        """
        # Điều kiện dừng: đã gán hết tất cả môn
        if index >= len(course_ids):
            return True
        
        course_id = course_ids[index]
        course = self.courses[course_id]
        
        # Lấy các lựa chọn có thể cho môn này
        available_options = self._get_available_options(course)
        if not available_options:
            if verbose:
                print(f"  Không có lựa chọn cho môn: {course.name} - {course.student_class}")
            return False
        
        # Sắp xếp ngẫu nhiên để tăng tính đa dạng
        random.shuffle(available_options)
        
        # Thử từng lựa chọn
        for teacher_id, room_id, timeslot_id in available_options:
            new_assignment = Assignment(
                course_id=course_id,
                room_id=room_id,
                teacher_id=teacher_id,
                timeslot_id=timeslot_id
            )
            
            # Kiểm tra ràng buộc
            if self.constraint_checker.check_all_constraints(schedule, new_assignment):
                # Gán môn này
                schedule.add_assignment(new_assignment)
                
                # Đệ quy cho môn tiếp theo
                if self._backtrack(schedule, course_ids, index + 1, verbose):
                    return True
                
                # Quay lui: xóa assignment vừa thêm
                schedule.assignments.pop()
        
        return False

    def _get_available_options(self, course: Course) -> List[Tuple[str, str, str]]:
        """
        Lấy tất cả các tổ hợp (giáo viên, phòng, timeslot) có thể cho môn học
        
        Args:
            course: Môn học cần tìm lựa chọn
            
        Returns:
            List các tuple (teacher_id, room_id, timeslot_id)
        """
        available_teachers = self.course_to_teachers.get(course.name, [])
        available_rooms = self._get_available_rooms(course)
        available_timeslots = list(self.timeslots.keys())
        
        # Tạo tất cả tổ hợp có thể
        options = []
        for teacher_id in available_teachers:
            for room_id in available_rooms:
                for timeslot_id in available_timeslots:
                    options.append((teacher_id, room_id, timeslot_id))
        
        return options

    def _get_available_rooms(self, course: Course) -> List[str]:
        
      
        
        available_rooms = []
        required_location = course.required_location
        
        for room_id, room in self.rooms.items():
            # Kiểm tra ràng buộc địa điểm
            if self._is_room_location_valid(room.location, required_location):
                available_rooms.append(room_id)
        
        return available_rooms

    def _is_room_location_valid(self, room_location: str, required_location: str) -> bool:
       
        if "|" in required_location:
            allowed_locations = required_location.split("|")
            return room_location in allowed_locations
        else:
            return room_location == required_location
        
        