# ai_agent.py
import random
import torch
import numpy as np
from logic.ai_utils import get_state_matrix, evaluate_tier
from logic.rules import get_combination_type # [MỚI] Import để check loại bài đánh ra
from ai_model import SamLocQNetwork

class DMCAgent:
    def __init__(self, is_training=True):
        self.model = SamLocQNetwork()
        self.is_training = is_training
        if not is_training:
            self.model.eval()
        
    def _encode_action(self, action_cards):
        if not action_cards: return np.zeros((4, 13), dtype=np.float32)
        return get_state_matrix(action_cards)
        
    def _encode_tier(self, tier_val):
        tier_vec = np.zeros(5, dtype=np.float32)
        tier_vec[tier_val] = 1.0
        return tier_vec

    # [MỚI] Hàm Hệ Chuyên Gia: Suy luận xác suất dựa trên M_played
    def _estimate_opponent_threats(self, observation):
        M_played = observation["M_played"]  # 4x13
        M_hand   = observation["M_hand"]    # 4x13
        col_two = 12  # index cột của quân 2 (rank 15)

        # Tính xác suất đối thủ có 2
        twos_played = int(M_played[:, col_two].sum())
        twos_in_hand = int(M_hand[:, col_two].sum())
        twos_opponent = 4 - twos_played - twos_in_hand
        prob_has_two = max(0.0, twos_opponent / 4.0)

        # Tính xác suất đối thủ có Tứ quý
        prob_has_quads = 0.0
        for col in range(13):
            played = int(M_played[:, col].sum())
            in_hand = int(M_hand[:, col].sum())
            remaining = 4 - played - in_hand
            if remaining == 4:  
                prob_has_quads = max(prob_has_quads, 0.8) # Còn nguyên 4 lá
            elif remaining == 3:
                prob_has_quads = max(prob_has_quads, 0.4) # Còn 3 lá ẩn

        return prob_has_two, prob_has_quads

    def select_action(self, observation, valid_actions, is_lead=False, epsilon=0.0):
        if not valid_actions:
            return []

        if self.is_training and epsilon > 0 and np.random.random() < epsilon:
            return random.choice(valid_actions)

        # Nối thêm M_played vào vector trạng thái
        state_vec = np.concatenate([
            observation["M_hand"].flatten(),
            observation["M_board"].flatten(),
            observation["M_played"].flatten(),
            observation["V_size"]
        ])
        state_tensor = torch.FloatTensor(state_vec).unsqueeze(0)

        best_action = None
        max_q_value = -float('inf')

        # Lấy dự đoán xác suất
        prob_two, prob_quads = self._estimate_opponent_threats(observation)
        filtered_actions = [(action, evaluate_tier(action)) for action in valid_actions]

        with torch.no_grad():
            for action, tier in filtered_actions:
                action_vec = self._encode_action(action).flatten()
                tier_vec = self._encode_tier(tier)

                a_tensor = torch.FloatTensor(action_vec).unsqueeze(0)
                t_tensor = torch.FloatTensor(tier_vec).unsqueeze(0)

                q_value = self.model(state_tensor, a_tensor, t_tensor).item()
                adjusted_q = q_value  # Biến Q-value đã điều chỉnh

                # -------------------------------------------------------------
                # 1. TƯ DUY PHÒNG THỦ: Tránh bị đè, bị chặt
                # -------------------------------------------------------------
                if prob_two > 0.6:
                    if action and get_combination_type(action) == "SINGLE" and action[0].rank < 10:
                        adjusted_q -= 0.3

                if prob_quads > 0.6:
                    if action and any(c.rank == 15 for c in action):
                        adjusted_q -= 0.5

                # -------------------------------------------------------------
                # 2. TƯ DUY TẤN CÔNG: Tối ưu bài khi được quyền đi đầu
                # -------------------------------------------------------------
                if is_lead and action:
                    action_type = get_combination_type(action)
                    if action_type == "STRAIGHT" and action[0].rank < 10:
                        adjusted_q += 0.3 + (len(action) * 0.1)
                    elif action_type in ["PAIR", "TRIPLE"] and action[0].rank < 10:
                        adjusted_q += 0.2 + (len(action) * 0.1)
                    elif action_type == "SINGLE" and action[0].rank < 7:
                        adjusted_q += 0.2
                    elif action_type == "SINGLE" and action[0].rank >= 14:
                        cards_left = int(observation["M_hand"].sum())
                        if cards_left > 2:
                            adjusted_q -= 0.8

                # -------------------------------------------------------------
                # 3. TƯ DUY TÀN CUỘC: Xử lý quân 2 (Heo) chống thối
                # -------------------------------------------------------------
                if action:
                    cards_left = int(observation["M_hand"].sum())
                    twos_in_hand = int(observation["M_hand"][:, 12].sum())

                    action_length = len(action)
                    twos_in_action = sum(1 for c in action if c.rank == 15)

                    remaining_cards = cards_left - action_length
                    remaining_twos = twos_in_hand - twos_in_action

                    if remaining_cards > 0 and remaining_cards == remaining_twos:
                        adjusted_q -= 2.0
                    if cards_left <= 3 and twos_in_action > 0 and remaining_cards > 0:
                        adjusted_q += 1.0

                # -------------------------------------------------------------
                # 4. CHỐNG ĐỀN BÁO (Có người còn 1 lá)
                # -------------------------------------------------------------
                if any(size == 1 for size in observation["V_size"]) and action:
                    action_type = get_combination_type(action)
                    if action_type == "SINGLE":
                        max_rank_in_hand = -1
                        for col in range(12, -1, -1):
                            if observation["M_hand"][:, col].sum() > 0:
                                max_rank_in_hand = col + 3
                                break
                        if action[0].rank < max_rank_in_hand:
                            adjusted_q -= 1.5
                        else:
                            adjusted_q += 0.8

                # -------------------------------------------------------------
                # 5. CHỐNG CÓNG (Thoát ế)
                # -------------------------------------------------------------
                cards_left = int(observation["M_hand"].sum())
                min_enemy_cards = min(observation["V_size"]) if len(observation["V_size"]) > 0 else 10

                if cards_left >= 9 and min_enemy_cards <= 2:
                    if not action:
                        adjusted_q -= 1.2
                    else:
                        adjusted_q += 0.5

                # -------------------------------------------------------------
                # 6. CHIẾN THUẬT TỨ QUÝ (Giữ hàng chặt Heo)
                # -------------------------------------------------------------
                if action and get_combination_type(action) == "QUAD":
                    if is_lead:
                        cards_left = int(observation["M_hand"].sum())
                        if cards_left > 4:
                            adjusted_q -= 1.0

                # -------------------------------------------------------------
                # 7. CHỐT HẠ (One-hit KO)
                # -------------------------------------------------------------
                if action:
                    cards_left = int(observation["M_hand"].sum())
                    if len(action) == cards_left:
                        adjusted_q += 10.0
                # -------------------------------------------------------------
                # [MỚI] 8. TƯ DUY GÀI BÀI KHI CÒN 2 LÁ (Baiting)
                # -------------------------------------------------------------
                cards_left = int(observation["M_hand"].sum())
                if is_lead and action and cards_left == 2 and len(action) == 1:
                    action_rank = action[0].rank

                    # Quét xem 2 lá trên tay là những lá nào
                    hand_ranks = []
                    for col in range(13):
                        count = int(observation["M_hand"][:, col].sum())
                        hand_ranks.extend([col + 3] * count)

                    if len(hand_ranks) == 2:
                        small_card = min(hand_ranks)
                        big_card = max(hand_ranks)

                        if action_rank == small_card:
                            # Tình huống: Định đánh lá NHỎ trước
                            if big_card < 14:  # Lá to còn lại chỉ là J, Q, K
                                adjusted_q += 0.6  # Thưởng: Lừa mồi rất hay!
                            elif big_card == 15:
                                adjusted_q -= 1.0  # Phạt: Ôm Heo cuối cùng dễ bị "Thối", cực nguy hiểm!

                        elif action_rank == big_card:
                            # Tình huống: Định đánh lá TO trước
                            if big_card == 15:
                                adjusted_q += 1.5  # Thưởng: Phang Heo chốt sổ, cướp cái để đánh nốt lá nhỏ về nhất!
                            elif big_card < 14:
                                adjusted_q -= 0.6  # Phạt: Đánh lá to dễ bị đè, mất lượt là tịt ngòi lá nhỏ.
                # -------------------------------------------------------------
                # -------------------------------------------------------------
                # SO SÁNH VÀ CHỌN NƯỚC ĐI TỐT NHẤT
                # -------------------------------------------------------------
                if adjusted_q > max_q_value:
                    max_q_value = adjusted_q
                    best_action = action

        return best_action