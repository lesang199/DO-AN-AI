"""
BACKTRACKING - Thuật toán Quay lui
===================================
Giải bài toán xếp lịch bằng thuật toán Backtracking (Quay lui)

Cách hoạt động:
1. Thử xếp từng trận đấu vào các ngày và sân có thể
2. Kiểm tra ràng buộc (ngày nghỉ, số trận mỗi ngày, xung đột sân)
3. Nếu vi phạm ràng buộc, quay lui (backtrack) và thử phương án khác
4. Tìm giải pháp tối ưu (ít ngày nhất)
"""

import copy
from typing import List, Tuple, Dict
from models import Match


class BacktrackingSolver:
    """
    Giải bài toán xếp lịch bằng thuật toán Backtracking (Quay lui)
    """
    
    def __init__(self, data: Dict):
        self.data = data
        self.best_schedule = None
        self.best_days = float('inf')
        self.iterations = 0
        self.max_iterations = 100000  # Giới hạn số lần thử để tránh quá lâu
    
    def is_valid_assignment(self, schedule: List[Match], match_idx: int, day: int, stadium: int) -> bool:
        """
        Kiểm tra xem việc gán trận đấu match_idx vào ngày day và sân stadium có hợp lệ không
        
        Args:
            schedule: Lịch hiện tại
            match_idx: Chỉ số trận đấu cần kiểm tra
            day: Ngày muốn xếp
            stadium: Sân muốn xếp
        
        Returns:
            True nếu hợp lệ, False nếu không
        """
        match = schedule[match_idx]
        num_teams = self.data['num_teams']
        num_stadiums = self.data['num_stadiums']
        max_matches_per_day = self.data['max_matches_per_day']
        min_rest_days = self.data['min_rest_days']
        
        # Kiểm tra sân hợp lệ
        if stadium < 0 or stadium >= num_stadiums:
            return False
        
        # Kiểm tra số trận mỗi ngày
        day_matches = [m for m in schedule[:match_idx] if m.day == day]
        if len(day_matches) >= max_matches_per_day:
            return False
        
        # Kiểm tra sân đã được sử dụng trong ngày đó chưa
        for m in day_matches:
            if m.stadium == stadium:
                return False
        
        # Kiểm tra đội đã thi trong ngày đó chưa
        for m in day_matches:
            if m.team1 == match.team1 or m.team1 == match.team2 or \
               m.team2 == match.team1 or m.team2 == match.team2:
                return False
        
        # Kiểm tra ngày nghỉ cho đội 1
        team1_matches = [m for m in schedule[:match_idx] 
                         if (m.team1 == match.team1 or m.team2 == match.team1) and m.day >= 0]
        if team1_matches:
            last_match_day = max([m.day for m in team1_matches])
            rest_days = day - last_match_day - 1
            if rest_days < min_rest_days:
                return False
        
        # Kiểm tra ngày nghỉ cho đội 2
        team2_matches = [m for m in schedule[:match_idx] 
                         if (m.team1 == match.team2 or m.team2 == match.team2) and m.day >= 0]
        if team2_matches:
            last_match_day = max([m.day for m in team2_matches])
            rest_days = day - last_match_day - 1
            if rest_days < min_rest_days:
                return False
        
        return True
    
    def backtrack(self, schedule: List[Match], match_idx: int, current_max_day: int):
        """
        Hàm đệ quy quay lui để tìm lịch tối ưu
        
        Args:
            schedule: Lịch hiện tại
            match_idx: Chỉ số trận đấu đang xét
            current_max_day: Ngày lớn nhất đã sử dụng
        """
        self.iterations += 1
        
        # Giới hạn số lần thử
        if self.iterations > self.max_iterations:
            return
        
        # Nếu đã xếp hết tất cả trận đấu
        if match_idx == len(schedule):
            # Kiểm tra xem có tốt hơn giải pháp hiện tại không
            if current_max_day + 1 < self.best_days:
                self.best_days = current_max_day + 1
                self.best_schedule = copy.deepcopy(schedule)
            return
        
        # Thử xếp trận đấu vào các ngày và sân
        # Giới hạn số ngày thử để tránh quá lâu
        max_day_to_try = min(current_max_day + 5, self.best_days - 1)
        
        for day in range(max_day_to_try + 1):
            for stadium in range(self.data['num_stadiums']):
                if self.is_valid_assignment(schedule, match_idx, day, stadium):
                    # Gán trận đấu
                    schedule[match_idx].day = day
                    schedule[match_idx].stadium = stadium
                    
                    # Tiếp tục với trận đấu tiếp theo
                    new_max_day = max(current_max_day, day)
                    self.backtrack(schedule, match_idx + 1, new_max_day)
                    
                    # Quay lui: bỏ gán
                    schedule[match_idx].day = -1
                    schedule[match_idx].stadium = -1
    
    def solve(self) -> Tuple[List[Match], float, int]:
        """
        Giải bài toán bằng Backtracking
        
        Returns:
            Tuple (lịch tốt nhất, số ngày, số lần lặp)
        """
        schedule = copy.deepcopy(self.data['matches'])
        self.iterations = 0
        self.best_days = float('inf')
        self.best_schedule = None
        
        # Bắt đầu quay lui
        self.backtrack(schedule, 0, -1)
        
        if self.best_schedule is None:
            # Nếu không tìm được giải pháp, trả về lịch rỗng
            return schedule, float('inf'), self.iterations
        
        return self.best_schedule, self.best_days, self.iterations

