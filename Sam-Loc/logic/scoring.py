# logic/scoring.py
class ScoringSystem:
    def __init__(self, base_bet=1000):
        """Khởi tạo hệ thống tính điểm."""
        self.base_bet = base_bet
        self.penalty_points = {
            'TWO_LEFT': 10,         
            'CONG': 20,             
            'INSTANT_WIN': 20,      
            'FOUR_OF_A_KIND': 20,   
            'SAM_WIN': 20,          
            'SAM_FAIL': 20,         
            'THOI_2_VE': 20,        # Phạt 20 lá nếu về bằng con 2
        }

    def calculate_score(self, winner_idx, players_hands, instant_win_type=None, sam_announcer=-1, is_thoi_2_ve=False, thoi_player=-1):
        """
        Tính toán tiền thắng thua.
        - is_thoi_2_ve: True nếu người về đánh con 2 cuối cùng.
        - thoi_player: Index người phạm luật thoi_2_ve.
        """
        num_players = len(players_hands)
        scores = [0] * num_players

        # 1. TRƯỜNG HỢP PHẠM LUẬT VỀ BẰNG 2
        if is_thoi_2_ve:
            penalty = self.penalty_points['THOI_2_VE'] * self.base_bet * (num_players - 1)
            for i in range(num_players):
                if i == thoi_player:
                    scores[i] = -penalty
                elif i == winner_idx:
                    scores[i] = penalty
                else:
                    scores[i] = 0
            return scores

        # 2. TRƯỜNG HỢP CÓ NGƯỜI BÁO SÂM
        if sam_announcer != -1:
            win_val = self.penalty_points['SAM_WIN'] * self.base_bet
            if winner_idx == sam_announcer:
                for i in range(num_players):
                    if i == winner_idx: scores[i] = win_val * (num_players - 1)
                    else: scores[i] = -win_val
            else:
                total_penalty = win_val * (num_players - 1)
                for i in range(num_players):
                    if i == sam_announcer: scores[i] = -total_penalty
                    elif i == winner_idx: scores[i] = total_penalty
                    else: scores[i] = 0
            return scores

        # 3. TRƯỜNG HỢP ĂN TRẮNG
        if instant_win_type:
            win_points = self.penalty_points['INSTANT_WIN'] * self.base_bet
            for i in range(num_players):
                if i == winner_idx: scores[i] = win_points * (num_players - 1)
                else: scores[i] = -win_points
            return scores

        # 4. TRƯỜNG HỢP THẮNG THƯỜNG
        for i, hand in enumerate(players_hands):
            if i == winner_idx: continue
            num_cards = len(hand)
            twos = sum(1 for c in hand if c.rank == 15)
            count = 20 if num_cards == 10 else num_cards
            count += (twos * self.penalty_points['TWO_LEFT'])
            from collections import Counter
            counts = Counter(c.rank for c in hand)
            for r, cnt in counts.items():
                if cnt == 4: count += self.penalty_points['FOUR_OF_A_KIND']
            points = count * self.base_bet
            scores[winner_idx] += points
            scores[i] -= points

        return scores
