# player/bot.py
import random
from .base_player import BasePlayer
from logic.rules import get_combination_value

class RandomBot(BasePlayer):
    def __init__(self, name, money=100000):
        """Bot Ngẫu Nhiên: Đánh không cần tính toán."""
        super().__init__(name, money)
        self.is_human = False

    def choose_move(self, valid_moves, can_pass=False):
        if not valid_moves: return None
        
        # Logic theo yêu cầu: Nếu còn 1 lá và là lá 2
        if len(self.hand) == 1 and self.hand[0].rank == 15:
            twos = [m for m in valid_moves if any(c.rank == 15 for c in m)]
            if twos: return twos[0]
            if can_pass: return None
            # Không chặn được, không bỏ lượt — valid_moves có thể rỗng (chỉ có 2)
            if not valid_moves: return None

        if can_pass and random.random() < 0.3: return None
        return random.choice(valid_moves)

class BotV0(BasePlayer):
    def __init__(self, name, money=100000):
        """Bot V0: Thuật toán Greedy (Tham lam). 
        Luôn chọn nước đi nhỏ nhất đủ để chặn bài trên bàn.
        """
        super().__init__(name, money)
        self.is_human = False

    def choose_move(self, valid_moves, can_pass=False):
        if not valid_moves: return None
        
        # Logic theo yêu cầu: Ưu tiên tống khứ quân 2 khi còn ít bài
        if len(self.hand) <= 3:
            twos = [m for m in valid_moves if any(c.rank == 15 for c in m)]
            if twos: return twos[0] # "Phải đánh 2 trước"

        # Nếu chỉ còn 1 lá và là lá 2 mà không chặn được (không có trong valid_moves)
        if len(self.hand) == 1 and self.hand[0].rank == 15:
            if can_pass: return None # "Không thì bỏ lượt không được đánh"

        # Luôn lấy nước đi có giá trị nhỏ nhất trong danh sách hợp lệ
        sorted_moves = sorted(valid_moves, key=lambda m: get_combination_value(m))
        return sorted_moves[0]

# Alias để không làm hỏng code cũ
class BasicBot(BotV0):
    pass
