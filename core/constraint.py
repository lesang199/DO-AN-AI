

from typing import Dict, Set
from core.model import Assignment, Schedule, Course, Room, Teacher, Timeslot


class ConstraintChecker:
   

    def __init__(self, courses: Dict[str, Course], rooms: Dict[str, Room],
                 teachers: Dict[str, Teacher], timeslots: Dict[str, Timeslot]):
       
        self.courses = courses
        self.rooms = rooms
        self.teachers = teachers
        self.timeslots = timeslots

    def check_all_constraints(self, schedule: Schedule, new_assignment: Assignment) -> bool:
        """
        Kiểm tra tất cả ràng buộc cứng cho một gán lịch mới
        
        Args:
            schedule: Lịch hiện tại
            new_assignment: Assignment mới cần kiểm tra
            
        Returns:
            True nếu tất cả ràng buộc được thỏa mãn, False nếu không
        """
        # Kiểm tra từng ràng buộc theo thứ tự (dừng sớm nếu vi phạm)
        if not self.check_teacher_conflict(schedule, new_assignment):
            return False
        
        if not self.check_room_conflict(schedule, new_assignment):
            return False
        
        if not self.check_student_class_conflict(schedule, new_assignment):
            return False
        
        if not self.check_location_constraint(new_assignment):
            return False
        
        return True

    def check_teacher_conflict(self, schedule: Schedule, new_assignment: Assignment) -> bool:
        """
        Ràng buộc 1: Giáo viên không được dạy 2 môn cùng thời điểm
        
        Một giáo viên chỉ có thể dạy một môn tại một thời điểm.
        
        Args:
            schedule: Lịch hiện tại
            new_assignment: Assignment mới
            
        Returns:
            True nếu không có xung đột, False nếu có xung đột
        """
        for assignment in schedule.assignments:
            if (assignment.teacher_id == new_assignment.teacher_id and
                assignment.timeslot_id == new_assignment.timeslot_id):
                return False
        return True

    def check_room_conflict(self, schedule: Schedule, new_assignment: Assignment) -> bool:
        """
        Ràng buộc 2: Phòng học không được sử dụng cho 2 môn cùng thời điểm
        
        Một phòng chỉ có thể được sử dụng cho một môn tại một thời điểm.
        Điều này cho phép nhiều lớp học cùng buổi nhưng ở các phòng khác nhau.
        
        Args:
            schedule: Lịch hiện tại
            new_assignment: Assignment mới
            
        Returns:
            True nếu không có xung đột, False nếu có xung đột
        """
        for assignment in schedule.assignments:
            if (assignment.room_id == new_assignment.room_id and
                assignment.timeslot_id == new_assignment.timeslot_id):
                return False
        return True

    def check_student_class_conflict(self, schedule: Schedule, new_assignment: Assignment) -> bool:
        """
        Ràng buộc 3: Mỗi lớp sinh viên không được học 2 môn cùng thời điểm
        
        Một lớp sinh viên chỉ có thể học một môn tại một thời điểm.
        Điều này đảm bảo sinh viên không bị trùng lịch.
        
        Args:
            schedule: Lịch hiện tại
            new_assignment: Assignment mới
            
        Returns:
            True nếu không có xung đột, False nếu có xung đột
        """
        new_course = self.courses.get(new_assignment.course_id)
        if not new_course:
            return False
        
        for assignment in schedule.assignments:
            existing_course = self.courses.get(assignment.course_id)
            if (existing_course and 
                existing_course.student_class == new_course.student_class and
                assignment.timeslot_id == new_assignment.timeslot_id):
                return False
        return True

    def check_location_constraint(self, assignment: Assignment) -> bool:
        """
        Ràng buộc 4: Kiểm tra ràng buộc địa điểm
        
        - Môn Thể dục phải học tại cơ sở N
        - Môn Tiếng Anh có thể học tại cơ sở A hoặc B
        - Các môn còn lại chỉ được học tại cơ sở B
        
        Args:

        
            assignment: Assignment cần kiểm tra
            
        Returns:
            True nếu thỏa mãn ràng buộc địa điểm, False nếu không
        """
        course = self.courses.get(assignment.course_id)
        room = self.rooms.get(assignment.room_id)
        
        if not course or not room:
            return False
        
        course_name = course.name
        required_location = course.required_location
        room_location = room.location
        
        # Môn Thể dục phải học tại cơ sở N
        if course_name == "Thể dục":
            return room_location == "N"
        
        # Môn Tiếng Anh có thể học tại cơ sở A hoặc B
        if course_name == "Tiếng Anh":
            return room_location in ["A", "B"]
        
        # Các môn còn lại chỉ được học tại cơ sở B
        return room_location == "B"

    def is_valid_schedule(self, schedule: Schedule) -> bool:
        """
        Kiểm tra xem một lịch có hợp lệ và hoàn chỉnh hay không
        
        Một lịch hợp lệ phải:
        1. Mỗi môn chỉ được gán một lần
        2. Tất cả môn đều được gán
        
        Args:
            schedule: Lịch cần kiểm tra
            
        Returns:
            True nếu lịch hợp lệ và hoàn chỉnh, False nếu không
        """
        # Kiểm tra mỗi môn chỉ được gán một lần
        assigned_courses = set()
        for assignment in schedule.assignments:
            if assignment.course_id in assigned_courses:
                return False  # Môn đã được gán 2 lần
            assigned_courses.add(assignment.course_id)
        
        # Kiểm tra tất cả môn đều được gán
        return len(assigned_courses) == len(self.courses)

    def get_unassigned_courses(self, schedule: Schedule) -> Set[str]:
        """
        Lấy danh sách các môn chưa được gán
        
        Args:
            schedule: Lịch cần kiểm tra
            
        Returns:
            Set các course_id chưa được gán
        """
        assigned_courses = {a.course_id for a in schedule.assignments}
        all_courses = set(self.courses.keys())
        return all_courses - assigned_courses
