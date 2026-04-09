# ai_model.py
import torch
import torch.nn as nn

class SamLocQNetwork(nn.Module):
    def __init__(self):
        super(SamLocQNetwork, self).__init__()
        
        # KÍCH THƯỚC ĐẦU VÀO MỚI (216 features):
        # M_hand(52) + M_board(52) + M_played(52) + V_size(3) + Action(52) + Tier(5) = 216
        input_size = 216
        
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
        x = torch.cat([state_vector, action_vector, tier_vector], dim=-1)
        q_value = self.network(x)
        return q_value
