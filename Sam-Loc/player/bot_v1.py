# player/bot_v1.py
from .base_player import BasePlayer
from logic.rules import get_combination_value, get_combination_type

class BotV1(BasePlayer):
    def __init__(self, name, money=100000):
        super().__init__(name, money)
        self.is_human = False

    def _opponent_near_win(self, game_engine):
        if game_engine is None:
            return False
        me = game_engine.state.current_player
        return any(
            len(game_engine.player_hands[i]) <= 2
            for i in range(game_engine.num_players)
            if i != me
        )

    def choose_move(self, valid_moves, can_pass=False, game_engine=None):
        if not valid_moves: return None
        
        # Logic theo yêu cầu: Nếu còn 1 lá và là lá 2
        if len(self.hand) == 1 and self.hand[0].rank == 15:
            twos = [m for m in valid_moves if any(c.rank == 15 for c in m)]
            if twos: return twos[0] # "Phải đánh 2 trước"
            if can_pass: return None # "Không thì bỏ lượt không được đánh"

        sorted_moves = sorted(valid_moves, key=lambda m: get_combination_value(m))

        # Đối thủ sắp về → đánh bài to nhất, không bỏ lượt
        if self._opponent_near_win(game_engine):
            sorted_desc = sorted(valid_moves, key=lambda m: get_combination_value(m), reverse=True)
            non_two = [m for m in sorted_desc if not any(c.rank == 15 for c in m)]
            return non_two[0] if non_two else sorted_desc[0]

        # Khi đi đầu (không được bỏ lượt = can_pass False): ưu tiên sảnh, tứ quý, sám, đôi
        is_lead = not can_pass
        if is_lead:
            straights = [m for m in valid_moves if get_combination_type(m) == "STRAIGHT"]
            if straights: return max(straights, key=len)
            for combo_type in ["FOUR_OF_A_KIND", "TRIPLE", "PAIR"]:
                combos = [m for m in valid_moves if get_combination_type(m) == combo_type]
                if combos: return sorted(combos, key=lambda m: get_combination_value(m))[0]
            return sorted_moves[0]

        # Chặn bài (có bài trên bàn): né dùng 2 trừ khi cần
        non_two_moves = [m for m in sorted_moves if not any(c.rank == 15 for c in m)]
        if non_two_moves: return non_two_moves[0]
        return sorted_moves[0]
