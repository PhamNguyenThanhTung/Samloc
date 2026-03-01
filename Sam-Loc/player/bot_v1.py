# player/bot_v1.py
from .base_player import BasePlayer
from logic.rules import get_combination_value, get_combination_type

class BotV1(BasePlayer):
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

        # Sắp xếp bài nhỏ tới lớn
        sorted_moves = sorted(valid_moves, key=lambda m: get_combination_value(m))

        # LUẬT QUAN TRỌNG: KHÔNG GIỮ 2 VỀ CUỐI
        # Nếu Bot chỉ còn ít bài (ví dụ < 4 lá), nó phải tìm cách tống khứ quân 2 đi ngay lập tức
        if len(self.hand) <= 3:
            twos = [m for m in valid_moves if any(c.rank == 15 for c in m)]
            if twos:
                # Nếu có thể đánh 2, đánh luôn để không bị thối khi về
                return twos[0]

        # Logic bình thường...
        if can_pass is False:
            straights = [m for m in valid_moves if get_combination_type(m) == "STRAIGHT"]
            if straights: return max(straights, key=len)
            for combo_type in ["FOUR_OF_A_KIND", "TRIPLE", "PAIR"]:
                combos = [m for m in valid_moves if get_combination_type(m) == combo_type]
                if combos: return sorted(combos, key=lambda m: get_combination_value(m))[0]
            return sorted_moves[0]

        # Chặn bài: Né dùng 2 trừ khi bài đối thủ quá to hoặc mình sắp hết bài
        non_two_moves = [m for m in sorted_moves if not any(c.rank == 15 for c in m)]
        if non_two_moves: return non_two_moves[0]
        return sorted_moves[0]
