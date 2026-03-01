# logic/scoring.py
class ScoringSystem:
    def __init__(self, base_bet=1000):
        """Khởi tạo hệ thống tính điểm."""
        self.base_bet = base_bet
        # Quy tắc Sâm Lốc chuẩn
        self.penalty_points = {
            'TWO_LEFT': 10,         # Thối 2: 10 lá/con
            'CONG': 20,             # Cóng (không đánh được lá nào): 20 lá
            'INSTANT_WIN': 20,      # Ăn trắng: 20 lá/người
            'FOUR_OF_A_KIND': 20,   # Thối tứ quý: 20 lá/bộ
        }

    def calculate_score(self, winner_idx, players_hands, instant_win_type=None):
        """
        Tính toán tiền thắng thua theo luật Sâm Lốc.
        - winner_idx: Vị trí người thắng.
        - players_hands: Bài còn lại trên tay mỗi người.
        """
        num_players = len(players_hands)
        scores = [0] * num_players

        if instant_win_type:
            # Ăn trắng: Thắng mỗi nhà 20 lá
            win_points = self.penalty_points['INSTANT_WIN'] * self.base_bet
            for i in range(num_players):
                if i == winner_idx:
                    scores[i] = win_points * (num_players - 1)
                else:
                    scores[i] = -win_points
        else:
            # Thắng thường
            for i, hand in enumerate(players_hands):
                if i == winner_idx: continue
                
                num_cards = len(hand)
                twos = sum(1 for c in hand if c.rank == 15)
                
                # LOGIC CHÍNH:
                if num_cards == 10:
                    # Trường hợp CÓNG: Tính 20 lá
                    count = self.penalty_points['CONG']
                else:
                    # Trường hợp THƯỜNG: Tính số lá trên tay
                    count = num_cards
                
                # Cộng thêm tiền thối 2 (mỗi con 10 lá)
                if twos > 0:
                    count += (twos * self.penalty_points['TWO_LEFT'])
                
                # Kiểm tra thối tứ quý (nếu có logic tứ quý trong hand thì cộng thêm 20)
                # (Hiện tại hand là list Card nên ta check rank counts)
                from collections import Counter
                counts = Counter(c.rank for c in hand)
                for rank, cnt in counts.items():
                    if cnt == 4:
                        count += self.penalty_points['FOUR_OF_A_KIND']

                points = count * self.base_bet
                scores[winner_idx] += points
                scores[i] -= points

        return scores
