# player/base_player.py
# Thứ tự chất giống Card.__lt__ (spade=0, club=1, diamond=2, heart=3)
SUIT_ORDER = {'spade': 0, 'club': 1, 'diamond': 2, 'heart': 3}

class BasePlayer:
    def __init__(self, name, money=100000):
        self.name = name
        self.money = money
        self.hand = []
        self.is_human = False
        self.has_announced = False  # Chưa nối với engine/GUI — chỉ lưu nội bộ

    def receive_cards(self, cards):
        self.hand = sorted(cards, key=lambda c: (c.rank, SUIT_ORDER.get(c.suit, 0)))

    def play_cards(self, cards):
        """Xóa các lá đã đánh khỏi tay, trả về True nếu thành công."""
        for card in cards:
            if card not in self.hand:
                return False
        for card in cards:
            self.hand.remove(card)
        if len(self.hand) == 1 and not self.has_announced:
            self.has_announced = True
        return True

    def get_hand_size(self):
        return len(self.hand)

    def reset_round(self):
        """Reset trạng thái báo cho ván mới."""
        self.has_announced = False