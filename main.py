"""
MAIN - Chương trình chính
==========================
File chính để chạy chương trình xếp lịch thi đấu thể thao
"""

import time
from data_generator import generate_data
from core.backtracking import BacktrackingSolver
from core.gwo import GWOSolver
from core.evaluator import evaluate_schedule
from comparison import compare_algorithms, print_results, print_schedule_details


def main():
    """Hàm main chính của chương trình"""
    print("\n" + "="*60)
    print("CHƯƠNG TRÌNH XẾP LỊCH THI ĐẤU THỂ THAO")
    print("="*60)
    print("\nGiải bài toán xếp lịch bằng 2 phương pháp:")
    print("1. Backtracking (Quay lui)")
    print("2. GWO (Grey Wolf Optimizer)")
    
    # Nhập thông tin
    print("\n" + "-"*60)
    print("NHẬP THÔNG TIN")
    print("-"*60)
    
    try:
        num_teams = int(input("Nhập số đội bóng (mặc định 8): ") or "8")
        num_stadiums = int(input("Nhập số sân vận động (mặc định 2): ") or "2")
        
        if num_teams < 2:
            print("⚠ Cảnh báo: Số đội phải >= 2. Sử dụng giá trị mặc định 8.")
            num_teams = 8
        if num_stadiums < 1:
            print("⚠ Cảnh báo: Số sân phải >= 1. Sử dụng giá trị mặc định 2.")
            num_stadiums = 2
        
        print("\nChọn phương pháp giải:")
        print("1. Chạy cả hai và so sánh (mặc định)")
        print("2. Chỉ Backtracking")
        print("3. Chỉ GWO")
        choice = input("Lựa chọn (1/2/3, mặc định 1): ").strip() or "1"
        
    except ValueError:
        print("⚠ Lỗi nhập liệu. Sử dụng giá trị mặc định.")
        num_teams = 8
        num_stadiums = 2
        choice = "1"