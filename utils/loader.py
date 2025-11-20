"""
Module tải dữ liệu từ các file JSON
"""

import json
import os
from typing import Dict
from core.model import Teacher, Room, Course, Timeslot


def load_teachers(data_dir: str = "data") -> Dict[str, Teacher]:
    """Tải danh sách giáo viên từ JSON"""
    file_path = os.path.join(data_dir, "teachers.json")
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    teachers = {}
    for item in data:
        teacher = Teacher(
            id=item["id"],
            name=item["name"],
            courses=item["courses"]
        )
        teachers[teacher.id] = teacher
    
    return teachers


def load_rooms(data_dir: str = "data") -> Dict[str, Room]:
    """Tải danh sách phòng học từ JSON"""
    file_path = os.path.join(data_dir, "rooms.json")
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    rooms = {}
    for item in data:
        room = Room(
            id=item["id"],
            name=item["name"],
            capacity=item["capacity"],
            location=item["location"]
        )
        rooms[room.id] = room
    
    return rooms


def load_courses(data_dir: str = "data") -> Dict[str, Course]:
    """Tải danh sách môn học từ JSON"""
    file_path = os.path.join(data_dir, "courses.json")
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    courses = {}
    for item in data:
        course = Course(
            id=item["id"],
            name=item["name"],
            student_class=item["student_class"],
            required_location=item["required_location"]
        )
        courses[course.id] = course
    
    return courses


def load_timeslots(data_dir: str = "data") -> Dict[str, Timeslot]:
    """Tải danh sách khung giờ từ JSON"""
    file_path = os.path.join(data_dir, "timeslots.json")
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    timeslots = {}
    for item in data:
        timeslot = Timeslot(
            id=item["id"],
            day=item["day"],
            period=item["period"],
            time=item["time"],
            session=item.get("session", "")  # Lấy session nếu có, mặc định là ""
        )
        timeslots[timeslot.id] = timeslot
    
    return timeslots


def load_all_data(data_dir: str = "data"):
    """Tải tất cả dữ liệu"""
    teachers = load_teachers(data_dir)
    rooms = load_rooms(data_dir)
    courses = load_courses(data_dir)
    timeslots = load_timeslots(data_dir)
    
    return teachers, rooms, courses, timeslots

