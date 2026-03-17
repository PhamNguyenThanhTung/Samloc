# logic/rl_env.py
import numpy as np
from logic.game_engine import GameEngine
from logic.ai_utils import get_state_matrix, evaluate_tier
from logic.rules import get_combination_type


class SamLocEnv:
    def __init__(self, num_players=4):
        self.game = GameEngine(num_players=num_players)

    def reset(self, skip_announce=True):
        """Khởi tạo lại ván bài và trả về trạng thái đầu tiên.
        skip_announce: Nếu True thì bỏ qua giai đoạn ANNOUNCING (Báo Sâm) để AI học đánh bài cơ bản trước.
        """
        self.game.setup_game()
        if skip_announce and self.game.state.phase == "ANNOUNCING":
            self.game.state.phase = "PLAYING"
        return self._get_observation()

    def _get_observation(self):
        """Đóng gói toàn bộ thông tin ván bài thành Tensors."""
        current_p = self.game.state.current_player
        hand = self.game.player_hands[current_p]

        # 1. Ma trận bài trên tay
        M_hand = get_state_matrix(hand)

        # 2. Đếm số bài của đối thủ
        V_size = np.array([len(self.game.player_hands[i]) for i in range(self.game.num_players) if i != current_p],
                          dtype=np.float32)

        # 3. Ma trận bài đang nằm trên bàn (last_move)
        M_board = get_state_matrix(self.game.state.last_move) if self.game.state.last_move else np.zeros((4, 13),
                                                                                                         dtype=np.float32)

        # Trả về Dictionary chứa các tensor này
        return {"M_hand": M_hand, "V_size": V_size, "M_board": M_board}

    def step(self, action_cards):
        """
        AI thực hiện 1 bước đi.
        action_cards: List các object Card (hoặc list rỗng [] nếu bỏ lượt)
        """
        # Lưu lại thông tin trước khi đánh để tính reward (sau play_move state đã thay đổi)
        prev_player = self.game.state.current_player
        prev_last_move = self.game.state.last_move
        prev_thoi_count = sum(1 for c in self.game.player_hands[prev_player] if c.rank == 15)
        # Số bài còn lại của từng đối thủ TRƯỚC nước đi (để phát hiện đối thủ sắp về)
        prev_opponent_sizes = [
            len(self.game.player_hands[i])
            for i in range(self.game.num_players)
            if i != prev_player
        ]

        # 1. Gọi game engine thực hiện nước đi
        valid, msg = self.game.play_move(action_cards)

        if not valid:
            return self._get_observation(), -10.0, False, {"msg": msg}

        # 2. Tính reward — dùng prev_* vì sau play_move state đã đổi (tay rỗng khi "về")
        reward = self._calculate_reward(action_cards, prev_player, prev_last_move, prev_thoi_count, prev_opponent_sizes)

        # 3. Kiểm tra game kết thúc chưa
        done = self.game.state.phase == "FINISHED"

        return self._get_observation(), reward, done, {"msg": msg}

    def _calculate_reward(self, action_cards, player_idx, prev_last_move, prev_thoi_count=0, prev_opponent_sizes=None):
        reward = 0.0

        # 1. Thưởng cơ bản: xả được bài
        if action_cards:
            reward += 0.1 * len(action_cards)

        # 2. Thưởng "Chặt Heo": dùng Tứ quý chặn đơn 2
        if prev_last_move and action_cards:
            last_typ = get_combination_type(prev_last_move)
            curr_typ = get_combination_type(action_cards)
            if last_typ == "SINGLE" and prev_last_move[0].rank == 15 and curr_typ == "FOUR_OF_A_KIND":
                reward += 5.0

        # 3. Thưởng "Áp lực đối thủ sắp về": khi có đối thủ còn ≤2 lá,
        #    thưởng thêm nếu đánh bài TO (rank cao, nhiều lá) để xả nhanh trước khi bị thua.
        #    Ngược lại phạt nếu bỏ lượt trong tình huống nguy hiểm này.
        if prev_opponent_sizes and action_cards:
            opponent_near_win = any(s <= 2 for s in prev_opponent_sizes)
            if opponent_near_win:
                # Tính "độ to" của nước đi: rank trung bình + bonus số lá
                avg_rank = sum(c.rank for c in action_cards) / len(action_cards)
                # Chuẩn hóa rank 3–15 về 0–1
                rank_score = (avg_rank - 3) / 12.0
                # Thưởng tỉ lệ với độ to của bài (tối đa +2.0 khi đánh 2 đơn)
                reward += 2.0 * rank_score
                # Thưởng thêm nếu xả được nhiều lá cùng lúc (sảnh, sám, tứ quý)
                if len(action_cards) >= 3:
                    reward += 0.5

        # 4. Phạt bỏ lượt khi đối thủ sắp về (nguy hiểm — nên đánh chặn)
        if prev_opponent_sizes and not action_cards:
            opponent_near_win = any(s <= 2 for s in prev_opponent_sizes)
            if opponent_near_win:
                reward -= 1.5

        # 5. Kết thúc game
        if self.game.state.phase == "FINISHED":
            if self.game.state.winner == player_idx:
                reward += 10.0
            else:
                reward -= 5.0
                # Phạt thối 2: dùng số lá 2 TRƯỚC play_move (sau play_move tay đã rỗng nếu vừa về)
                if prev_thoi_count > 0:
                    reward -= 2.0 * prev_thoi_count
        return reward