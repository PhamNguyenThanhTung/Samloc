# logic/scoring.py
class ScoringSystem:
    def __init__(self, base_bet=1000):
        self.base_bet = base_bet
        self.penalty_points = {
            'TWO_LEFT': 5,          # Thối 2: 5 lá/con
            'FOUR_OF_A_KIND': 10,    # Tứ quý thường
            'FOUR_TWOS': 15,         # Tứ quý 2
            'INSTANT_WIN': 20,       # Ăn trắng: 20 lá/người
            'CONG': 15,               # Cóng: 15 lá
            'DEN': 20,                # Đền làng: 20 lá x số người
        }

    def calculate_score(self, winner_idx, players_hands, instant_win_type=None, penalties=None):
        """Tính điểm cho ván chơi, trả về list điểm số theo index."""
        num_players = len(players_hands)
        scores = [0] * num_players

        if instant_win_type:
            # Ăn trắng: người thắng ăn 20 lá mỗi người
            win_points = self.penalty_points['INSTANT_WIN'] * self.base_bet
            for i in range(num_players):
                if i == winner_idx:
                    scores[i] = win_points * (num_players - 1)
                else:
                    scores[i] = -win_points
        else:
            # Thắng thường: ăn số lá còn lại của từng người
            for i, hand in enumerate(players_hands):
                if i == winner_idx:
                    continue
                points = len(hand) * self.base_bet
                scores[winner_idx] += points
                scores[i] -= points

        # Áp dụng các khoản phạt (nếu có)
        if penalties:
            for p in penalties:
                scores[p['player']] -= p['points']
                if 'beneficiary' in p:
                    scores[p['beneficiary']] += p['points']

        return scores

    def calculate_penalty_two(self, player_idx, num_twos=1, beneficiary=None):
        """Tạo penalty thối 2."""
        points = self.penalty_points['TWO_LEFT'] * self.base_bet * num_twos
        return {'player': player_idx, 'points': points, 'beneficiary': beneficiary}

    def calculate_penalty_four(self, player_idx, rank, beneficiary=None):
        """Tạo penalty tứ quý (nếu rank=15 là tứ quý 2)."""
        if rank == 15:
            points = self.penalty_points['FOUR_TWOS'] * self.base_bet
        else:
            points = self.penalty_points['FOUR_OF_A_KIND'] * self.base_bet
        return {'player': player_idx, 'points': points, 'beneficiary': beneficiary}