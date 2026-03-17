# ai_model.py
import torch
import torch.nn as nn

class SamLocQNetwork(nn.Module):
    def __init__(self):
        super(SamLocQNetwork, self).__init__()
        
        # Kích thước đầu vào (Input Size):
        # - M_hand (Bài trên tay): 4x13 = 52
        # - M_board (Bài trên bàn): 4x13 = 52
        # - V_size (Bài đối thủ - game 4 người thì có 3 đối thủ): 3
        # - Action (Hành động đang xét): 4x13 = 52
        # - Tier Feature (Đặc trưng Tier của hành động): 5 (one-hot cho Tier 0-4)
        # Tổng cộng: 52 + 52 + 3 + 52 + 5 = 164 features
        input_size = 164
        
        # Thiết kế mạng Multi-Layer Perceptron (MLP) với Dropout để giảm overfitting
        self.network = nn.Sequential(
            nn.Linear(input_size, 512),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(512, 512),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, 1)
        )

    def forward(self, state_vector, action_vector, tier_vector):
        """
        Ghép nối (concatenate) tất cả thông tin lại rồi đưa qua mạng nơ-ron
        """
        # Nối các tensor lại thành 1 vector phẳng theo chiều cuối (dim=-1)
        x = torch.cat([state_vector, action_vector, tier_vector], dim=-1)
        q_value = self.network(x)
        return q_value
