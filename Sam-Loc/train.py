# train.py
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import os
import sys

# Thêm đường dẫn để import từ các thư mục con
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from logic.rl_env import SamLocEnv
from ai_agent import DMCAgent
from logic.ai_utils import evaluate_tier

# --- CÁC THAM SỐ HUẤN LUYỆN (HYPERPARAMETERS) ---
NUM_EPISODES = 5000       # Số ván game muốn AI tự chơi
LEARNING_RATE = 1e-4      # Tốc độ học
GAMMA = 0.99              # Hệ số suy giảm phần thưởng
EPSILON_START = 1.0       # Epsilon đầu (khám phá)
EPSILON_END = 0.05        # Epsilon cuối (sau khi decay)
EPSILON_DECAY_FRAC = 0.8  # Decay epsilon trong 80% số ván đầu, 20% cuối pure exploitation
GRAD_CLIP_NORM = 1.0      # Clip gradient để tránh bùng nổ

def calculate_returns(rewards, gamma):
    """Tính toán phần thưởng tích lũy (G_t) từ cuối ván ngược lên đầu ván."""
    returns = []
    G = 0
    for r in reversed(rewards):
        G = r + gamma * G
        returns.insert(0, G)
    return returns

def train():
    print("--- BẮT ĐẦU HUẤN LUYỆN AI SÂM LỐC ---")
    env = SamLocEnv(num_players=4)
    # Khởi tạo 1 "Bộ não" dùng chung cho cả 4 người chơi để học nhanh hơn
    agent = DMCAgent(is_training=True)
    
    # Load model cũ nếu có để tiếp tục train
    model_path = "samloc_ai_model.pth"
    if os.path.exists(model_path):
        try:
            agent.model.load_state_dict(torch.load(model_path, weights_only=True))
            print(f"Đã tải model cũ từ {model_path}")
        except Exception as e:
            print(f"Không thể tải model cũ: {e}")

    optimizer = optim.Adam(agent.model.parameters(), lr=LEARNING_RATE)
    criterion = nn.MSELoss()
    decay_episodes = max(1, int(NUM_EPISODES * EPSILON_DECAY_FRAC))

    for episode in range(NUM_EPISODES):
        obs = env.reset()
        done = False
        transitions_by_player = {i: [] for i in range(4)}
        epsilon = max(EPSILON_END, EPSILON_START - (EPSILON_START - EPSILON_END) * episode / decay_episodes)

        while not done:
            cur_player = env.game.state.current_player
            valid_actions = env.game.get_valid_moves()
            action = agent.select_action(obs, valid_actions, is_lead=(env.game.state.last_move is None), epsilon=epsilon)

            tier_val = evaluate_tier(action)
            state_vec = np.concatenate([
                obs["M_hand"].flatten(),
                obs["M_board"].flatten(),
                obs["V_size"]
            ])
            s_tensor = torch.FloatTensor(state_vec).unsqueeze(0)
            a_tensor = torch.FloatTensor(agent._encode_action(action).flatten()).unsqueeze(0)
            t_tensor = torch.FloatTensor(agent._encode_tier(tier_val)).unsqueeze(0)

            next_obs, reward, done, info = env.step(action)
            transitions_by_player[cur_player].append((s_tensor, a_tensor, t_tensor, reward))
            obs = next_obs

        # Shared model: gom loss của tất cả người chơi rồi update 1 lần (gradient nhất quán)
        agent.model.train()
        all_losses = []
        for player_id, player_transitions in transitions_by_player.items():
            if not player_transitions:
                continue
            rewards = [t[3] for t in player_transitions]
            returns = calculate_returns(rewards, GAMMA)
            for i, (s_tensor, a_tensor, t_tensor, _) in enumerate(player_transitions):
                predicted_q = agent.model(s_tensor, a_tensor, t_tensor)
                target_q = torch.tensor([[returns[i]]], dtype=torch.float32)
                all_losses.append(criterion(predicted_q, target_q))

        if all_losses:
            optimizer.zero_grad()
            avg_loss = torch.stack(all_losses).mean()
            avg_loss.backward()
            torch.nn.utils.clip_grad_norm_(agent.model.parameters(), max_norm=GRAD_CLIP_NORM)
            optimizer.step()

        if all_losses and (episode + 1) % 100 == 0:
            total_reward = sum(t[3] for trans in transitions_by_player.values() for t in trans)
            print(f"Ván {episode + 1}/{NUM_EPISODES} - Tổng thưởng: {total_reward:.2f} - Loss: {avg_loss.item():.6f}")
            # Lưu model định kỳ mỗi 500 ván
            if (episode + 1) % 500 == 0:
                torch.save(agent.model.state_dict(), model_path)

    # Lưu lại "Bộ não" sau khi học xong
    torch.save(agent.model.state_dict(), model_path)
    print("Huấn luyện hoàn tất! Đã lưu model.")

if __name__ == "__main__":
    train()
