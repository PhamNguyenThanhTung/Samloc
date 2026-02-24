# player/bot.py
import random
from .base_player import BasePlayer
from logic.rules import get_combination_value  # thêm dòng này

class RandomBot(BasePlayer):
    def __init__(self, name, money=100000):
        super().__init__(name, money)
        self.is_human = False

    def choose_move(self, valid_moves, can_pass=False):
        if not valid_moves:
            return None
        if can_pass and random.random() < 0.3:
            return None
        return random.choice(valid_moves)

class BasicBot(BasePlayer):
    def __init__(self, name, money=100000):
        super().__init__(name, money)
        self.is_human = False

    def choose_move(self, valid_moves, can_pass=False):
        if not valid_moves:
            return None
        # Sắp xếp theo giá trị tăng dần
        sorted_moves = sorted(valid_moves, key=lambda m: get_combination_value(m))
        return sorted_moves[0]