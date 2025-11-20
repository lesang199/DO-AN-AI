

import os
import sys
import time
from utils.loader import load_all_data
from core.backtracking import BacktrackingSolver
from core.gwo import GWOSolver
from core.evaluator import ScheduleEvaluator
from core.constraint import ConstraintChecker
from utils.printer import SchedulePrinter

1
def print_header(title: str):
    """In header với format đẹp"""
    print("\n" + "=" * 100)
    print(f"  {title}")
    print("=" * 100)


def print_menu():
    """In menu chính"""
    print_header("CHƯƠNG TRÌNH XẾP LỊCH MÔN HỌC")
    print("  1. Chạy Backtracking tìm lịch hợp lệ")
    print("  2. Chạy GWO tối ưu lịch")
    print("  3. So sánh Backtracking và GWO")
    print("  4. In lịch ra màn hình")
    print("  5. Thoát")
    print("=" * 100)


def load_data_and_init():
    """
    Load dữ liệu và khởi tạo các đối tượng cần thiết
    
    Returns:
        Tuple (teachers, rooms, courses, timeslots, printer, evaluator, constraint_checker)
    """
    print("\n  Đang tải dữ liệu...")
    try:
        teachers, rooms, courses, timeslots = load_all_data()
        print(f"  ✓ Đã tải: {len(teachers)} giáo viên, {len(rooms)} phòng, "
              f"{len(courses)} môn học, {len(timeslots)} khung giờ")
        
        printer = SchedulePrinter(courses, rooms, teachers, timeslots)
        evaluator = ScheduleEvaluator(courses, rooms, teachers, timeslots)
        constraint_checker = ConstraintChecker(courses, rooms, teachers, timeslots)
        
        return teachers, rooms, courses, timeslots, printer, evaluator, constraint_checker
    except Exception as e:
        print(f"  ✗ Lỗi khi tải dữ liệu: {e}")
        return None


def run_backtracking(printer, evaluator, constraint_checker, 
                    courses, rooms, teachers, timeslots):
    """Chạy thuật toán Backtracking"""
    print_header("CHẠY THUẬT TOÁN BACKTRACKING")
    
    # Khởi tạo solver
    solver = BacktrackingSolver(courses, rooms, teachers, timeslots)
    
    # Giải bài toán
    print("\n  Đang tìm lịch hợp lệ bằng Backtracking...")
    print("  (Thuật toán sẽ tìm tất cả tổ hợp có thể để gán môn học)")
    start_time = time.time()
    schedule = solver.solve(verbose=True)
    elapsed_time = time.time() - start_time
    
    # Hiển thị kết quả
    print_result(schedule, elapsed_time, printer, evaluator, constraint_checker, 
                "BACKTRACKING")
    
    return schedule


def run_gwo(printer, evaluator, constraint_checker,
           courses, rooms, teachers, timeslots):
    """Chạy thuật toán GWO"""
    print_header("CHẠY THUẬT TOÁN GWO (GREY WOLF OPTIMIZER)")
    
    # Khởi tạo solver
    solver = GWOSolver(courses, rooms, teachers, timeslots)
    
    # Nhập tham số
    print("\n  Nhập tham số GWO (nhấn Enter để dùng giá trị mặc định):")
    try:
        population_input = input("  Số lượng sói trong đàn (mặc định 20): ").strip()
        population_size = int(population_input) if population_input else 20
        
        iterations_input = input("  Số lần lặp tối đa (mặc định 100): ").strip()
        max_iterations = int(iterations_input) if iterations_input else 100
    except ValueError:
        population_size = 20
        max_iterations = 100
        print("  ⚠ Giá trị không hợp lệ, sử dụng giá trị mặc định")
    
    # Giải bài toán
    print(f"\n  Đang tối ưu lịch bằng GWO...")
    print(f"  Tham số: population={population_size}, iterations={max_iterations}")
    start_time = time.time()
    schedule = solver.solve(population_size=population_size, 
                          max_iterations=max_iterations,
                          verbose=True)
    elapsed_time = time.time() - start_time
    
    # Hiển thị kết quả
    print_result(schedule, elapsed_time, printer, evaluator, constraint_checker, 
                "GWO")
    
    return schedule


def print_result(schedule, elapsed_time, printer, evaluator, constraint_checker, 
                algorithm_name):
    """
    In kết quả của thuật toán
    
    Args:
        schedule: Lịch tìm được
        elapsed_time: Thời gian chạy
        printer: SchedulePrinter
        evaluator: ScheduleEvaluator
        constraint_checker: ConstraintChecker
        algorithm_name: Tên thuật toán
    """
    if schedule:
        print(f"\n  ✓ Hoàn thành sau {elapsed_time:.2f} giây!")
        
        # Kiểm tra tính hợp lệ
        is_valid = constraint_checker.is_valid_schedule(schedule)
        assigned_count = len(schedule.assignments)
        total_courses = len(constraint_checker.courses)
        
        if is_valid:
            print(f"  ✓ Lịch hợp lệ và hoàn chỉnh ({assigned_count}/{total_courses} môn được gán)")
        else:
            unassigned = constraint_checker.get_unassigned_courses(schedule)
            print(f"  ⚠ Lịch không hoàn chỉnh ({assigned_count}/{total_courses} môn được gán)")
            if unassigned:
                unassigned_names = [constraint_checker.courses[cid].name 
                                  for cid in list(unassigned)[:5]]
                print(f"  Môn chưa gán: {', '.join(unassigned_names)}" + 
                      (f" và {len(unassigned)-5} môn khác" if len(unassigned) > 5 else ""))
        
        # Tính fitness
        fitness = evaluator.evaluate(schedule)
        print(f"  Điểm fitness: {fitness:.2f}/100")
        
        # In lịch
        printer.print_schedule(schedule, f"LỊCH HỌC - {algorithm_name}")
        printer.print_statistics(schedule)
    else:
        print(f"\n  ✗ Không tìm thấy lịch hợp lệ sau {elapsed_time:.2f} giây!")
        print("  Gợi ý:")
        print("    - Kiểm tra lại dữ liệu (đủ giáo viên, phòng, timeslot)")
        print("    - Thử chạy GWO với tham số lớn hơn")
        print("    - Kiểm tra ràng buộc có quá chặt không")


def compare_algorithms(printer, evaluator, constraint_checker,
                      courses, rooms, teachers, timeslots):
    """So sánh Backtracking và GWO"""
    print_header("SO SÁNH BACKTRACKING VÀ GWO")
    
    results = {}
    
    # Chạy Backtracking
    print("\n" + "-" * 100)
    print("  [1/2] Chạy Backtracking...")
    print("-" * 100)
    backtracking_solver = BacktrackingSolver(courses, rooms, teachers, timeslots)
    start_time = time.time()
    bt_schedule = backtracking_solver.solve(verbose=False)
    bt_time = time.time() - start_time
    
    if bt_schedule:
        bt_fitness = evaluator.evaluate(bt_schedule)
        bt_valid = constraint_checker.is_valid_schedule(bt_schedule)
        results['backtracking'] = {
            'schedule': bt_schedule,
            'time': bt_time,
            'fitness': bt_fitness,
            'valid': bt_valid,
            'assigned': len(bt_schedule.assignments)
        }
    
    # Chạy GWO
    print("\n" + "-" * 100)
    print("  [2/2] Chạy GWO...")
    print("-" * 100)
    gwo_solver = GWOSolver(courses, rooms, teachers, timeslots)
    start_time = time.time()
    gwo_schedule = gwo_solver.solve(population_size=20, max_iterations=100, verbose=True)
    gwo_time = time.time() - start_time
    
    if gwo_schedule:
        gwo_fitness = evaluator.evaluate(gwo_schedule)
        gwo_valid = constraint_checker.is_valid_schedule(gwo_schedule)
        results['gwo'] = {
            'schedule': gwo_schedule,
            'time': gwo_time,
            'fitness': gwo_fitness,
            'valid': gwo_valid,
            'assigned': len(gwo_schedule.assignments)
        }
    
    # So sánh kết quả
    print_header("KẾT QUẢ SO SÁNH")
    
    total_courses = len(courses)
    
    if 'backtracking' in results:
        bt = results['backtracking']
        print(f"\n  BACKTRACKING:")
        print(f"    - Thời gian: {bt['time']:.2f} giây")
        print(f"    - Fitness: {bt['fitness']:.2f}/100")
        print(f"    - Hợp lệ: {'Có' if bt['valid'] else 'Không'}")
        print(f"    - Số môn được gán: {bt['assigned']}/{total_courses}")
    else:
        print(f"\n  BACKTRACKING: Không tìm thấy lịch hợp lệ")
    
    if 'gwo' in results:
        gwo = results['gwo']
        print(f"\n  GWO:")
        print(f"    - Thời gian: {gwo['time']:.2f} giây")
        print(f"    - Fitness: {gwo['fitness']:.2f}/100")
        print(f"    - Hợp lệ: {'Có' if gwo['valid'] else 'Không'}")
        print(f"    - Số môn được gán: {gwo['assigned']}/{total_courses}")
    else:
        print(f"\n  GWO: Không tìm thấy lịch hợp lệ")
    
    # Kết luận
    if 'backtracking' in results and 'gwo' in results:
        print(f"\n  KẾT LUẬN:")
        if results['gwo']['fitness'] > results['backtracking']['fitness']:
            print(f"    - GWO có fitness cao hơn ({results['gwo']['fitness']:.2f} vs {results['backtracking']['fitness']:.2f})")
        else:
            print(f"    - Backtracking có fitness cao hơn ({results['backtracking']['fitness']:.2f} vs {results['gwo']['fitness']:.2f})")
        
        if results['backtracking']['time'] < results['gwo']['time']:
            print(f"    - Backtracking nhanh hơn ({results['backtracking']['time']:.2f}s vs {results['gwo']['time']:.2f}s)")
        else:
            print(f"    - GWO nhanh hơn ({results['gwo']['time']:.2f}s vs {results['backtracking']['time']:.2f}s)")
    
    print("\n" + "=" * 100)
    
    # In lịch
    if 'backtracking' in results:
        printer.print_schedule(results['backtracking']['schedule'], 
                              "LỊCH HỌC - BACKTRACKING")
    
    if 'gwo' in results:
        printer.print_schedule(results['gwo']['schedule'], 
                             "LỊCH HỌC - GWO")


def print_schedule_menu(printer, evaluator, constraint_checker,
                       courses, rooms, teachers, timeslots):
    """In lịch từ file đã lưu hoặc tạo mới"""
    print_header("IN LỊCH HỌC")
    
    print("\n  Chọn nguồn lịch:")
    print("  1. Tạo lịch mới bằng Backtracking")
    print("  2. Tạo lịch mới bằng GWO")
    print("  3. Quay lại menu chính")
    
    choice = input("\n  Nhập lựa chọn (1-3): ").strip()
    
    if choice == "1":
        schedule = run_backtracking(printer, evaluator, constraint_checker,
                                  courses, rooms, teachers, timeslots)
        if schedule:
            printer.print_schedule_by_course(schedule, "LỊCH HỌC THEO MÔN - BACKTRACKING")
    elif choice == "2":
        schedule = run_gwo(printer, evaluator, constraint_checker,
                         courses, rooms, teachers, timeslots)
        if schedule:
            printer.print_schedule_by_course(schedule, "LỊCH HỌC THEO MÔN - GWO")
    elif choice == "3":
        return
    else:
        print("  ⚠ Lựa chọn không hợp lệ!")


def main():
    """Hàm main"""
    # Kiểm tra thư mục data
    if not os.path.exists("data"):
        print("✗ Lỗi: Không tìm thấy thư mục 'data'!")
        print("Vui lòng đảm bảo các file JSON nằm trong thư mục 'data/'")
        sys.exit(1)
    
    # Load dữ liệu một lần để khởi tạo các đối tượng
    data = load_data_and_init()
    if data is None:
        sys.exit(1)
    
    teachers, rooms, courses, timeslots, printer, evaluator, constraint_checker = data
    
    # Menu chính
    while True:
        print_menu()
        choice = input("  Nhập lựa chọn (1-5): ").strip()
        
        if choice == "1":
            run_backtracking(printer, evaluator, constraint_checker,
                           courses, rooms, teachers, timeslots)
        elif choice == "2":
            run_gwo(printer, evaluator, constraint_checker,
                   courses, rooms, teachers, timeslots)
        elif choice == "3":
            compare_algorithms(printer, evaluator, constraint_checker,
                             courses, rooms, teachers, timeslots)
        elif choice == "4":
            print_schedule_menu(printer, evaluator, constraint_checker,
                              courses, rooms, teachers, timeslots)
        elif choice == "5":
            print("\n  Cảm ơn bạn đã sử dụng chương trình!")
            break
        else:
            print("\n  ⚠ Lựa chọn không hợp lệ! Vui lòng chọn lại.")
        
        input("\n  Nhấn Enter để tiếp tục...")


if __name__ == "__main__":
    main()