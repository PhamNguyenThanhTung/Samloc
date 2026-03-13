# ai_agent.py
import torch
import numpy as np
from logic.ai_utils import get_state_matrix, evaluate_tier
from ai_model import SamLocQNetwork

class DMCAgent:
    def __init__(self, is_training=True):
        self.model = SamLocQNetwork()
        self.is_training = is_training
        
    def _encode_action(self, action_cards):
        """Chuyển hành động thành ma trận 4x13 giống như state"""
        if not action_cards: # Bỏ lượt
            return np.zeros((4, 13), dtype=np.float32)
        return get_state_matrix(action_cards)
        
    def _encode_tier(self, tier_val):
        """One-hot encoding cho Tier từ 0 đến 4"""
        tier_vec = np.zeros(5, dtype=np.float32)
        tier_vec[tier_val] = 1.0
        return tier_vec

    def select_action(self, observation, valid_actions, is_lead=False):
        """
        observation: State dict từ env._get_observation()
        valid_actions: List các action hợp lệ từ rules_engine
        is_lead: True nếu đang được quyền đánh đầu
        """
        if not valid_actions:
            return [] # Bắt buộc bỏ lượt
            
        # Tiền xử lý vector trạng thái chung (s)
        # s = M_hand (flattened) + M_board (flattened) + V_size
        state_vec = np.concatenate([
            observation["M_hand"].flatten(),
            observation["M_board"].flatten(),
            observation["V_size"]
        ])
        state_tensor = torch.FloatTensor(state_vec).unsqueeze(0) # Thêm batch dimension (1, 107)

        best_action = None
        max_q_value = -float('inf')
        
        # KHÂU CẮT TỈA (PRUNING) DỰA TRÊN TIER
        filtered_actions = []
        for action in valid_actions:
            tier = evaluate_tier(action)
            # Lọc heuristic có thể thêm vào đây
            filtered_actions.append((action, tier))
            
        # Đưa các hành động qua mạng nơ-ron để chấm điểm
        self.model.eval()
        with torch.no_grad():
            for action, tier in filtered_actions:
                action_vec = self._encode_action(action).flatten()
                tier_vec = self._encode_tier(tier)
                
                a_tensor = torch.FloatTensor(action_vec).unsqueeze(0) # (1, 52)
                t_tensor = torch.FloatTensor(tier_vec).unsqueeze(0)  # (1, 5)
                
                # Dự đoán giá trị Q (Sử dụng state, action, và tier)
                q_value = self.model(state_tensor, a_tensor, t_tensor).item()
                
                if q_value > max_q_value:
                    max_q_value = q_value
                    best_action = action
                    
        return best_action
