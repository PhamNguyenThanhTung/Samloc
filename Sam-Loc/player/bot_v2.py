import os
import torch
import numpy as np
from .base_player import BasePlayer

from ai_agent import DMCAgent
from logic.ai_utils import get_state_matrix

# Đường dẫn file model: cùng thư mục với player/, file nằm ở thư mục gốc project
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_DEFAULT_MODEL_PATH = os.path.normpath(os.path.join(_SCRIPT_DIR, "..", "samloc_ai_model_v2.pth"))


class BotV2(BasePlayer):
    def __init__(self, name, money=100000):
        super().__init__(name, money)
        self.is_human = False
        self.agent = DMCAgent(is_training=False)
        try:
            self.agent.model.load_state_dict(torch.load(_DEFAULT_MODEL_PATH, map_location=torch.device("cpu")))
            self.agent.model.eval()  # Khóa mạng nơ-ron, không học thêm nữa
            print(f"[{name}] Đã nạp thành công bộ não AI!")
        except Exception as e:
            print(f"[{name}] Lỗi không tìm thấy bộ não AI: {e}")

    def choose_move(self, valid_moves, can_pass=False, game_engine=None):
        """
        Ghi đè hàm chọn nước đi. AI dùng toán học để chọn bài thay vì if/else.
        LƯU Ý: Phải truyền thêm game_engine vào đây để AI nhìn được bàn chơi!
        """
        # Nếu không có nước đi hợp lệ
        if not valid_moves:
            return None

        # Console/CLI không truyền game_engine — fallback dùng greedy nhỏ nhất như BotV0
        if game_engine is None:
            from logic.rules import get_combination_value
            return min(valid_moves, key=lambda m: get_combination_value(m)) if valid_moves else None

        # --- AI BẮT ĐẦU QUAN SÁT (OBSERVATION) ---
        current_p = game_engine.state.current_player

        # 1. Trích xuất ma trận bài trên tay
        M_hand = get_state_matrix(self.hand)

        # --- CODE SỬA LỖI MỚI ---
        # Lấy số bài của các người chơi đang ngồi trong bàn
        opponents_cards = [len(game_engine.player_hands[i]) for i in range(game_engine.num_players) if i != current_p]

        # Bơm thêm các số 0 vào cho đủ 3 đối thủ (ghế trống) để chiều lòng mạng nơ-ron 164 features
        while len(opponents_cards) < 3:
            opponents_cards.append(0)

        V_size = np.array(opponents_cards, dtype=np.float32)
        # ------------------------

        # 3. Trích xuất ma trận bài đối thủ vừa đánh (nằm trên bàn)
        last_move = game_engine.state.last_move
        M_board = get_state_matrix(last_move) if last_move else np.zeros((4, 13), dtype=np.float32)

        # [MỚI] Khởi tạo M_played bằng 0 cho Bot trên giao diện
        M_played = np.zeros((4, 13), dtype=np.float32)

        obs = {"M_hand": M_hand, "V_size": V_size, "M_board": M_board, "M_played": M_played}

        # --- AI SUY LUẬN ---
        # AI sẽ được quyền tự do bung bài (is_lead = True) nếu trên bàn chưa có ai đánh (last_move là None)
        is_lead = (last_move is None)

        best_action = self.agent.select_action(obs, valid_moves, is_lead=is_lead)

        # Trả về kết quả: Nếu AI quyết định bỏ lượt (best_action rỗng) thì trả về None theo chuẩn code cũ của bạn
        if not best_action and can_pass:
            return None

        return best_action