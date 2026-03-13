# logic/rl_env.py
import numpy as np
from logic.game_engine import GameEngine
from logic.ai_utils import get_state_matrix, evaluate_tier
from logic.rules import get_combination_type

class SamLocEnv:
    def __init__(self, num_players=4):
        self.game = GameEngine(num_players=num_players)
        
    def reset(self):
        """Khởi tạo lại ván bài và trả về trạng thái đầu tiên."""
        self.game.setup_game()
        
        # Bỏ qua giai đoạn ANNOUNCING (Báo Sâm) tạm thời để AI học đánh bài cơ bản trước
        if self.game.state.phase == "ANNOUNCING":
            self.game.state.phase = "PLAYING"
            
        return self._get_observation()

    def _get_observation(self):
        """Đóng gói toàn bộ thông tin ván bài thành Tensors."""
        current_p = self.game.state.current_player
        hand = self.game.player_hands[current_p]
        
        # 1. Ma trận bài trên tay
        M_hand = get_state_matrix(hand)
        
        # 2. Đếm số bài của đối thủ
        V_size = np.array([len(self.game.player_hands[i]) for i in range(self.game.num_players) if i != current_p], dtype=np.float32)
        
        # 3. Ma trận bài đang nằm trên bàn (last_move)
        M_board = get_state_matrix(self.game.state.last_move) if self.game.state.last_move else np.zeros((4, 13), dtype=np.float32)
        
        # Trả về Dictionary chứa các tensor này
        return {"M_hand": M_hand, "V_size": V_size, "M_board": M_board}

    def step(self, action_cards):
        """
        AI thực hiện 1 bước đi.
        action_cards: List các object Card (hoặc list rỗng [] nếu bỏ lượt)
        """
        # Lưu lại thông tin trước khi đánh để tính reward
        prev_player = self.game.state.current_player

        # 1. Gọi game engine thực hiện nước đi
        valid, msg = self.game.play_move(action_cards)
        
        if not valid:
            # Phạt rất nặng nếu AI chọn nước đi không hợp lệ
            return self._get_observation(), -10.0, True, {"msg": msg}
            
        # 2. Tính toán Phần thưởng (Reward Shaping)
        reward = self._calculate_reward(action_cards, prev_player)
        
        # 3. Kiểm tra game kết thúc chưa
        done = self.game.state.phase == "FINISHED"
        
        return self._get_observation(), reward, done, {"msg": msg}

    def _calculate_reward(self, action_cards, player_idx):
        reward = 0.0
        
        # 1. Phần thưởng cơ bản (r_step): Thưởng nhẹ khi đánh được bài đi (để AI thích xả bài)
        if action_cards:
            reward += 0.1 * len(action_cards)
            
        # 2. Thưởng "Chặt Heo" (r_chop)
        if self.game.state.last_move and action_cards:
            last_typ = get_combination_type(self.game.state.last_move)
            curr_typ = get_combination_type(action_cards)
            
            # Nếu bài trước là 2 đơn và mình chặn bằng Tứ quý
            if last_typ == "SINGLE" and self.game.state.last_move[0].rank == 15:
                if curr_typ == "FOUR_OF_A_KIND":
                    reward += 5.0
                    
        # 3. Kết thúc game (r_win, r_thoi)
        if self.game.state.phase == "FINISHED":
            if self.game.state.winner == player_idx:
                reward += 10.0 # Thưởng thắng ván
            else:
                reward -= 5.0 # Phạt thua ván
                
                # Phạt thối 2
                hand = self.game.player_hands[player_idx]
                thoi_count = sum(1 for c in hand if c.rank == 15)
                if thoi_count > 0:
                    reward -= (2.0 * thoi_count)
                    
        return reward
