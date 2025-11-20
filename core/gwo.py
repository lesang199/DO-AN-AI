
import random
from typing import Dict, List, Tuple, Optional
from core.model import Schedule, Assignment, Course, Room, Teacher, Timeslot
from core.constraint import ConstraintChecker
from core.evaluator import ScheduleEvaluator


class GWOSolver:
    """
    Lớp giải bài toán xếp lịch bằng Grey Wolf Optimizer
    
    Thuật toán:
    1. Khởi tạo đàn sói (các lịch ngẫu nhiên)
    2. Tính fitness cho từng sói
    3. Chọn Alpha, Beta, Delta (3 sói tốt nhất)
    4. Cập nhật vị trí các sói dựa trên Alpha, Beta, Delta
    5. Lặp lại cho đến khi đạt số lần lặp tối đa
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
        self.evaluator = ScheduleEvaluator(courses, rooms, teachers, timeslots)
        
        # Tạo mapping từ tên môn đến danh sách giáo viên có thể dạy
        self.course_to_teachers = self._build_course_teacher_mapping(teachers)

    def _build_course_teacher_mapping(self, teachers: Dict[str, Teacher]) -> Dict[str, List[str]]:
        """Xây dựng mapping từ tên môn đến danh sách giáo viên"""
        mapping = {}
        for teacher_id, teacher in teachers.items():
            for course_name in teacher.courses:
                if course_name not in mapping:
                    mapping[course_name] = []
                mapping[course_name].append(teacher_id)
        return mapping

    def solve(self, population_size: int = 20, max_iterations: int = 100, 
              verbose: bool = True) -> Schedule:
        """
        Giải bài toán bằng GWO
        
        Args:
            population_size: Số lượng sói trong đàn
            max_iterations: Số lần lặp tối đa
            verbose: In thông tin tiến trình
            
        Returns:
            Lịch tốt nhất tìm được
        """
        if verbose:
            print(f"  Khởi tạo đàn {population_size} sói...")
        
        # Khởi tạo đàn sói
        population = self._initialize_population(population_size)
        
        # Tính fitness cho từng sói
        fitness_scores = [self.evaluator.evaluate(wolf) for wolf in population]
        
        # Tìm Alpha, Beta, Delta (3 sói tốt nhất)
        alpha_idx, beta_idx, delta_idx = self._get_top_three(fitness_scores)
        alpha = population[alpha_idx].copy()
        beta = population[beta_idx].copy()
        delta = population[delta_idx].copy()
        alpha_fitness = fitness_scores[alpha_idx]
        
        if verbose:
            print(f"  Fitness ban đầu: {alpha_fitness:.2f}")
            print(f"  Bắt đầu tối ưu hóa...\n")
        
        # Vòng lặp chính
        for iteration in range(max_iterations):
            # Tham số a giảm từ 2 xuống 0 (điều khiển khả năng khám phá)
            a = 2.0 - (2.0 * iteration / max_iterations)
            
            # Cập nhật từng sói trong đàn
            for i in range(population_size):
                # Tính toán vị trí mới dựa trên Alpha, Beta, Delta
                new_wolf = self._update_wolf_position(
                    population[i], alpha, beta, delta, a
                )
                
                # Sửa lịch để đảm bảo hợp lệ và hoàn chỉnh
                new_wolf = self._repair_schedule(new_wolf)
                
                # Tính fitness mới
                new_fitness = self.evaluator.evaluate(new_wolf)
                
                # Cập nhật nếu tốt hơn
                if new_fitness > fitness_scores[i]:
                    population[i] = new_wolf
                    fitness_scores[i] = new_fitness
            
            # Cập nhật Alpha, Beta, Delta
            alpha_idx, beta_idx, delta_idx = self._get_top_three(fitness_scores)
            
            if fitness_scores[alpha_idx] > alpha_fitness:
                alpha = population[alpha_idx].copy()
                beta = population[beta_idx].copy()
                delta = population[delta_idx].copy()
                alpha_fitness = fitness_scores[alpha_idx]
            
            # In tiến trình
            if verbose and (iteration + 1) % 10 == 0:
                assigned_count = len(alpha.assignments)
                total_courses = len(self.courses)
                print(f"  Iteration {iteration + 1}/{max_iterations}: "
                      f"Fitness = {alpha_fitness:.2f}, "
                      f"Assigned = {assigned_count}/{total_courses}")
        
        if verbose:
            print(f"\n  Hoàn thành! Fitness cuối: {alpha_fitness:.2f}")
        
        return alpha

    def _initialize_population(self, size: int) -> List[Schedule]:
        """
        Khởi tạo đàn sói ban đầu (các lịch ngẫu nhiên)
        
        Args:
            size: Số lượng sói
            
        Returns:
            Danh sách các lịch ngẫu nhiên
        """
        population = []
        
        for _ in range(size):
            schedule = self._create_random_schedule()
            population.append(schedule)
        
        return population

    def _create_random_schedule(self) -> Schedule:
        """
        Tạo một lịch ngẫu nhiên hợp lệ
        
        Returns:
            Lịch ngẫu nhiên
        """
        schedule = Schedule()
        course_ids = list(self.courses.keys())
        random.shuffle(course_ids)
        
        for course_id in course_ids:
            course = self.courses[course_id]
            assignment = self._try_create_assignment(course_id, course, schedule)
            
            if assignment:
                schedule.add_assignment(assignment)
        
        return schedule

    def _try_create_assignment(self, course_id: str, course: Course, 
                              schedule: Schedule, max_tries: int = 200) -> Optional[Assignment]:
        """
        Thử tạo một assignment hợp lệ cho môn học
        
        Args:
            course_id: ID môn học
            course: Đối tượng Course
            schedule: Lịch hiện tại
            max_tries: Số lần thử tối đa
            
        Returns:
            Assignment nếu thành công, None nếu không
        """
        available_teachers = self.course_to_teachers.get(course.name, [])
        available_rooms = self._get_available_rooms(course)
        available_timeslots = list(self.timeslots.keys())
        
        if not available_teachers or not available_rooms:
            return None
        
        # Thử ngẫu nhiên
        for _ in range(max_tries):
            teacher_id = random.choice(available_teachers)
            room_id = random.choice(available_rooms)
            timeslot_id = random.choice(available_timeslots)
            
            assignment = Assignment(
                course_id=course_id,
                room_id=room_id,
                teacher_id=teacher_id,
                timeslot_id=timeslot_id
            )
            
            if self.constraint_checker.check_all_constraints(schedule, assignment):
                return assignment
        
        return None

    def _get_available_rooms(self, course: Course) -> List[str]:
        """Lấy danh sách phòng phù hợp với ràng buộc địa điểm"""
        available_rooms = []
        required_location = course.required_location
        
        for room_id, room in self.rooms.items():
            if self._is_room_location_valid(room.location, required_location):
                available_rooms.append(room_id)
        
        return available_rooms

    def _is_room_location_valid(self, room_location: str, required_location: str) -> bool:
        """Kiểm tra vị trí phòng có phù hợp không"""
        if "|" in required_location:
            allowed_locations = required_location.split("|")
            return room_location in allowed_locations
        else:
            return room_location == required_location

    def _get_top_three(self, fitness_scores: List[float]) -> Tuple[int, int, int]:
        """
        Tìm 3 chỉ số có fitness cao nhất (Alpha, Beta, Delta)
        
        Returns:
            Tuple (alpha_idx, beta_idx, delta_idx)
        """
        indexed_scores = [(i, score) for i, score in enumerate(fitness_scores)]
        indexed_scores.sort(key=lambda x: x[1], reverse=True)
        
        alpha_idx = indexed_scores[0][0]
        beta_idx = indexed_scores[1][0] if len(indexed_scores) > 1 else alpha_idx
        delta_idx = indexed_scores[2][0] if len(indexed_scores) > 2 else beta_idx
        
        return alpha_idx, beta_idx, delta_idx

    def _update_wolf_position(self, wolf: Schedule, alpha: Schedule, 
                            beta: Schedule, delta: Schedule, a: float) -> Schedule:
        """
        Cập nhật vị trí của một sói dựa trên Alpha, Beta, Delta
        
        Args:
            wolf: Sói cần cập nhật
            alpha: Sói Alpha (tốt nhất)
            beta: Sói Beta (tốt thứ 2)
            delta: Sói Delta (tốt thứ 3)
            a: Tham số điều khiển (giảm từ 2 xuống 0)
            
        Returns:
            Sói mới sau khi cập nhật
        """
        new_wolf = Schedule()
        
        # Với mỗi môn học, chọn assignment từ Alpha, Beta, Delta
        for course_id in self.courses.keys():
            # Lấy assignment từ top 3
            alpha_assignment = self._get_assignment_for_course(alpha, course_id)
            beta_assignment = self._get_assignment_for_course(beta, course_id)
            delta_assignment = self._get_assignment_for_course(delta, course_id)
            
            # Chọn assignment dựa trên xác suất (Alpha cao hơn)
            selected = self._select_assignment(alpha_assignment, beta_assignment, delta_assignment)
            
            # Nếu không có assignment từ top 3, tạo mới
            if selected is None:
                course = self.courses[course_id]
                selected = self._try_create_assignment(course_id, course, new_wolf)
            
            # Thêm vào lịch nếu hợp lệ
            if selected and self.constraint_checker.check_all_constraints(new_wolf, selected):
                new_wolf.add_assignment(selected)
            elif selected:
                # Nếu không hợp lệ, thử tạo assignment mới
                course = self.courses[course_id]
                new_assignment = self._try_create_assignment(course_id, course, new_wolf)
                if new_assignment:
                    new_wolf.add_assignment(new_assignment)
        
        return new_wolf

    def _select_assignment(self, alpha_assignment: Optional[Assignment],
                          beta_assignment: Optional[Assignment],
                          delta_assignment: Optional[Assignment]) -> Optional[Assignment]:
        """
        Chọn assignment từ Alpha, Beta, Delta dựa trên xác suất
        
        Args:
            alpha_assignment: Assignment từ Alpha
            beta_assignment: Assignment từ Beta
            delta_assignment: Assignment từ Delta
            
        Returns:
            Assignment được chọn
        """
        rand = random.random()
        
        # Xác suất: Alpha 50%, Beta 30%, Delta 20%
        if rand < 0.5 and alpha_assignment:
            return alpha_assignment
        elif rand < 0.8 and beta_assignment:
            return beta_assignment
        elif delta_assignment:
            return delta_assignment
        
        # Fallback
        if alpha_assignment:
            return alpha_assignment
        elif beta_assignment:
            return beta_assignment
        else:
            return delta_assignment

    def _get_assignment_for_course(self, schedule: Schedule, course_id: str) -> Optional[Assignment]:
        """Lấy assignment của một môn học trong lịch"""
        for assignment in schedule.assignments:
            if assignment.course_id == course_id:
                return assignment
        return None

    def _repair_schedule(self, schedule: Schedule) -> Schedule:
        """
        Sửa lịch để đảm bảo tất cả môn đều được gán và hợp lệ
        
        Quy trình:
        1. Giữ lại các assignment hợp lệ từ lịch cũ
        2. Thêm các môn chưa được gán với assignment hợp lệ
        
        Args:
            schedule: Lịch cần sửa
            
        Returns:
            Lịch đã được sửa và hoàn chỉnh
        """
        repaired = Schedule()
        
        # Bước 1: Giữ lại các assignment hợp lệ từ lịch cũ
        for assignment in schedule.assignments:
            if self.constraint_checker.check_all_constraints(repaired, assignment):
                repaired.add_assignment(assignment)
        
        # Bước 2: Thêm các môn chưa được gán
        assigned_courses = {a.course_id for a in repaired.assignments}
        
        for course_id in self.courses.keys():
            if course_id not in assigned_courses:
                course = self.courses[course_id]
                assignment = self._try_create_assignment(course_id, course, repaired, max_tries=300)
                
                if assignment:
                    repaired.add_assignment(assignment)
        
        return repaired
