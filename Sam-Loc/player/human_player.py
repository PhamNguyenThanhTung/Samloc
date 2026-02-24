# player/human_player.py
from .base_player import BasePlayer

class HumanPlayer(BasePlayer):
    def __init__(self, name, money=100000):
        super().__init__(name, money)
        self.is_human = True

    def choose_move(self, valid_moves, can_pass=False):
        """Hiển thị menu và nhận lựa chọn từ người chơi."""
        print(f"\n📋 Bài của {self.name}: {[str(c) for c in self.hand]}")
        print("Các nước đi hợp lệ:")
        for i, move in enumerate(valid_moves):
            cards_str = [str(c) for c in move]
            print(f"  {i}: {cards_str}")
        if can_pass:
            print(f"  {len(valid_moves)}: Bỏ lượt")

        while True:
            try:
                choice = int(input("Chọn nước đi: "))
                if 0 <= choice < len(valid_moves):
                    return valid_moves[choice]
                if can_pass and choice == len(valid_moves):
                    return None
                print(f"Vui lòng chọn từ 0 đến {len(valid_moves) if not can_pass else len(valid_moves)}")
            except ValueError:
                print("Vui lòng nhập số!")