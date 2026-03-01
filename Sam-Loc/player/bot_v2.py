# player/bot_v2.py
from .base_player import BasePlayer
from logic.rules import get_combination_value, get_combination_type

class BotV2(BasePlayer):
    def __init__(self, name, money=100000):
        super().__init__(name, money)
        self.is_human = False

    def choose_move(self, valid_moves, can_pass=False):
        if not valid_moves: return None

        # Logic theo yêu cầu: Nếu còn 1 lá và là lá 2
        if len(self.hand) == 1 and self.hand[0].rank == 15:
            twos = [m for m in valid_moves if any(c.rank == 15 for c in m)]
            if twos: return twos[0] # "Phải đánh 2 trước"
            if can_pass: return None # "Không thì bỏ lượt không được đánh"

        sorted_desc = sorted(valid_moves, key=lambda m: get_combination_value(m), reverse=True)
        sorted_asc = sorted(valid_moves, key=lambda m: get_combination_value(m))

        # LUẬT QUAN TRỌNG: GIẢI PHÓNG 2 SỚM
        # Bot V2 thông minh hơn, nếu còn ít lá hoặc có cơ hội là đánh 2 ngay để tránh thối
        if len(self.hand) <= 4:
            twos = [m for m in valid_moves if any(c.rank == 15 for c in m)]
            if twos: return twos[0]

        if can_pass:
            # Ưu tiên đánh quân to nhất (ép bài) nhưng né quân 2 nếu chưa cần thiết
            best_non_two = [m for m in sorted_desc if not any(c.rank == 15 for c in m)]
            if best_non_two: return best_non_two[0]
            return sorted_desc[0]
        else:
            straights = [m for m in valid_moves if get_combination_type(m) == "STRAIGHT"]
            if straights: return max(straights, key=len)
            for combo_type in ["FOUR_OF_A_KIND", "TRIPLE", "PAIR"]:
                combos = [m for m in valid_moves if get_combination_type(m) == combo_type]
                if combos: return sorted(combos, key=lambda m: get_combination_value(m), reverse=True)[0]
            return sorted_desc[0]
