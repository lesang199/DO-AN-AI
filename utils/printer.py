"""
Module in lịch học ra màn hình
"""

from typing import Dict
from core.model import Schedule, Assignment, Course, Room, Teacher, Timeslot


class SchedulePrinter:
    """Lớp in lịch học"""

    def __init__(self, courses: Dict[str, Course], rooms: Dict[str, Room],
                 teachers: Dict[str, Teacher], timeslots: Dict[str, Timeslot]):
        self.courses = courses
        self.rooms = rooms
        self.teachers = teachers
        self.timeslots = timeslots

    def print_schedule(self, schedule: Schedule, title: str = "LỊCH HỌC"):
        """In lịch học ra màn hình"""
        print("\n" + "=" * 100)
        print(f"  {title}")
        print("=" * 100)
        
        if not schedule.assignments:
            print("  Lịch trống!")
            print("=" * 100 + "\n")
            return
        
        # Sắp xếp assignments theo timeslot
        sorted_assignments = sorted(schedule.assignments, 
                                   key=lambda a: self._get_timeslot_order(a.timeslot_id))
        
        # In header
        print(f"{'Thứ':<10} {'Buổi':<8} {'Thời gian':<20} {'Môn học':<30} {'Lớp':<15} {'Giáo viên':<25} {'Phòng học':<30}")
        print("-" * 100)
        
        # In từng dòng
        for assignment in sorted_assignments:
            course = self.courses.get(assignment.course_id)
            teacher = self.teachers.get(assignment.teacher_id)
            room = self.rooms.get(assignment.room_id)
            timeslot = self.timeslots.get(assignment.timeslot_id)
            
            if course and teacher and room and timeslot:
                session = timeslot.session if timeslot.session else f"Tiết {timeslot.period}"
                print(f"{timeslot.day:<10} {session:<8} {timeslot.time:<20} "
                      f"{course.name:<30} {course.student_class:<15} {teacher.name:<25} {room.name:<30}")
        
        print("=" * 100 + "\n")

    def print_schedule_by_course(self, schedule: Schedule, title: str = "LỊCH HỌC THEO MÔN"):
        """In lịch học theo từng môn"""
        print("\n" + "=" * 100)
        print(f"  {title}")
        print("=" * 100)
        
        if not schedule.assignments:
            print("  Lịch trống!")
            print("=" * 100 + "\n")
            return
        
        # Nhóm theo môn học
        course_assignments: Dict[str, Assignment] = {}
        for assignment in schedule.assignments:
            course_assignments[assignment.course_id] = assignment
        
        # In từng môn
        for course_id, assignment in sorted(course_assignments.items()):
            course = self.courses.get(course_id)
            teacher = self.teachers.get(assignment.teacher_id)
            room = self.rooms.get(assignment.room_id)
            timeslot = self.timeslots.get(assignment.timeslot_id)
            
            if course and teacher and room and timeslot:
                session = timeslot.session if timeslot.session else f"Tiết {timeslot.period}"
                print(f"\n  Môn: {course.name} - Lớp: {course.student_class}")
                print(f"  Giáo viên: {teacher.name}")
                print(f"  Phòng: {room.name}")
                print(f"  Thời gian: {timeslot.day}, {session} ({timeslot.time})")
                print("-" * 100)
        
        print("\n")

    def _get_timeslot_order(self, timeslot_id: str) -> int:
        """Lấy thứ tự của timeslot để sắp xếp"""
        timeslot = self.timeslots.get(timeslot_id)
        if not timeslot:
            return 999
        
        day_order = {"Thứ 2": 0, "Thứ 3": 1, "Thứ 4": 2, "Thứ 5": 3, "Thứ 6": 4, "Thứ 7": 5}
        day_index = day_order.get(timeslot.day, 99)
        # Sắp xếp: sáng trước, chiều sau
        session_order = 0 if timeslot.session == "Sáng" else 1 if timeslot.session == "Chiều" else timeslot.period
        return day_index * 100 + session_order * 10 + timeslot.period

    def print_statistics(self, schedule: Schedule):
        """In thống kê về lịch học"""
        print("\n" + "=" * 100)
        print("  THỐNG KÊ LỊCH HỌC")
        print("=" * 100)
        
        if not schedule.assignments:
            print("  Lịch trống!")
            print("=" * 100 + "\n")
            return
        
        # Đếm số phòng sử dụng
        used_rooms = set()
        for assignment in schedule.assignments:
            used_rooms.add(assignment.room_id)
        
        # Đếm số giáo viên sử dụng
        used_teachers = set()
        for assignment in schedule.assignments:
            used_teachers.add(assignment.teacher_id)
        
        # Đếm số timeslot sử dụng
        used_timeslots = set()
        for assignment in schedule.assignments:
            used_timeslots.add(assignment.timeslot_id)
        
        print(f"  Tổng số môn học: {len(schedule.assignments)}")
        print(f"  Số phòng học sử dụng: {len(used_rooms)}")
        print(f"  Số giáo viên sử dụng: {len(used_teachers)}")
        print(f"  Số khung giờ sử dụng: {len(used_timeslots)}")
        print("=" * 100 + "\n")

