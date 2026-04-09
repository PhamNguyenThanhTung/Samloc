# train.py
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import os
import sys
import random # [MỚI] Import random

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from logic.rl_env import SamLocEnv
from ai_agent import DMCAgent
from logic.ai_utils import evaluate_tier

# --- HYPERPARAMETERS ---
NUM_EPISODES = 5000
LEARNING_RATE = 1e-4
GAMMA = 0.99
EPSILON_START = 1.0
EPSILON_END = 0.05
EPSILON_DECAY_FRAC = 0.8
GRAD_CLIP_NORM = 1.0

# [MỚI] CẤU HÌNH LEAGUE TRAINING (GIẢI ĐẤU)
LEAGUE_POOL = []
LEAGUE_SAVE_INTERVAL = 1000
LEAGUE_OPPONENT_PROB = 0.3
MAX_LEAGUE_SIZE = 10

def calculate_returns(rewards, gamma):
    returns = []
    G = 0
    for r in reversed(rewards):
        G = r + gamma * G
        returns.insert(0, G)
    return returns

# [MỚI] Hàm nạp đối thủ từ quá khứ
def load_league_opponent(pool):
    opp = DMCAgent(is_training=False)
    path = random.choice(pool)
    opp.model.load_state_dict(torch.load(path, weights_only=True))
    return opp

def train():
    print("--- BẮT ĐẦU HUẤN LUYỆN AI SÂM LỐC (V2 - CÓ TRÍ NHỚ & LEAGUE) ---")
    env = SamLocEnv(num_players=4)
    agent = DMCAgent(is_training=True)
    
    # [MỚI] ĐỔI TÊN MODEL MỚI TRÁNH LỖI SIZE MISMATCH
    model_path = "samloc_ai_model_v2.pth"
    if os.path.exists(model_path):
        try:
            agent.model.load_state_dict(torch.load(model_path, weights_only=True))
            print(f"Đã tải model cũ từ {model_path}")
        except Exception as e:
            print(f"Không thể tải model: {e}")

    optimizer = optim.Adam(agent.model.parameters(), lr=LEARNING_RATE)
    criterion = nn.MSELoss()
    decay_episodes = max(1, int(NUM_EPISODES * EPSILON_DECAY_FRAC))

    for episode in range(NUM_EPISODES):
        obs = env.reset()
        done = False
        
        # [MỚI] Chỉ thu thập dữ liệu huấn luyện cho Player 0 (Main Agent)
        transitions_p0 = [] 
        epsilon = max(EPSILON_END, EPSILON_START - (EPSILON_START - EPSILON_END) * episode / decay_episodes)

        # [MỚI] LOGIC LEAGUE TRAINING: Quyết định có dùng đối thủ cũ không
        use_league = (len(LEAGUE_POOL) > 0 and random.random() < LEAGUE_OPPONENT_PROB)
        league_agent = load_league_opponent(LEAGUE_POOL) if use_league else None

        while not done:
            cur_player = env.game.state.current_player
            valid_actions = env.game.get_valid_moves()

            # [MỚI] Chọn Action tùy thuộc vào tác tử
            if cur_player == 0 or league_agent is None:
                # Agent chính đang học
                action = agent.select_action(obs, valid_actions, is_lead=(env.game.state.last_move is None), epsilon=epsilon)
            else:
                # Đối thủ dùng model cũ đánh nghiêm túc (epsilon = 0)
                action = league_agent.select_action(obs, valid_actions, is_lead=(env.game.state.last_move is None), epsilon=0.0)

            # [MỚI] Mã hóa và lưu Transition (Chỉ lưu nếu là Player 0 đánh)
            if cur_player == 0:
                tier_val = evaluate_tier(action)
                state_vec = np.concatenate([
                    obs["M_hand"].flatten(),
                    obs["M_board"].flatten(),
                    obs["M_played"].flatten(),
                    obs["V_size"]
                ])
                s_tensor = torch.FloatTensor(state_vec).unsqueeze(0)
                a_tensor = torch.FloatTensor(agent._encode_action(action).flatten()).unsqueeze(0)
                t_tensor = torch.FloatTensor(agent._encode_tier(tier_val)).unsqueeze(0)

            next_obs, reward, done, info = env.step(action)
            
            # [MỚI] Chỉ lưu reward vào mảng của Player 0
            if cur_player == 0:
                transitions_p0.append((s_tensor, a_tensor, t_tensor, reward))
            
            obs = next_obs

        # Update trọng số cho Main Agent (Chỉ dùng data từ Player 0)
        agent.model.train()
        if transitions_p0:
            rewards = [t[3] for t in transitions_p0]
            returns = calculate_returns(rewards, GAMMA)
            all_losses = []
            
            for i, (s_tensor, a_tensor, t_tensor, _) in enumerate(transitions_p0):
                predicted_q = agent.model(s_tensor, a_tensor, t_tensor)
                target_q = torch.tensor([[returns[i]]], dtype=torch.float32)
                all_losses.append(criterion(predicted_q, target_q))

            if all_losses:
                optimizer.zero_grad()
                avg_loss = torch.stack(all_losses).mean()
                avg_loss.backward()
                torch.nn.utils.clip_grad_norm_(agent.model.parameters(), max_norm=GRAD_CLIP_NORM)
                optimizer.step()

        # In log và lưu Model
        if (episode + 1) % 100 == 0:
            total_reward = sum(t[3] for t in transitions_p0) if transitions_p0 else 0
            loss_val = avg_loss.item() if transitions_p0 and all_losses else 0.0
            print(f"Ván {episode + 1}/{NUM_EPISODES} - Tổng thưởng P0: {total_reward:.2f} - Loss: {loss_val:.6f}")
            
        # [MỚI] LƯU CHECKPOINT CHO LEAGUE POOL MỖI 1000 VÁN
        if (episode + 1) % LEAGUE_SAVE_INTERVAL == 0:
            ckpt_path = f"league_ckpt_{episode+1}.pth"
            torch.save(agent.model.state_dict(), ckpt_path)
            LEAGUE_POOL.append(ckpt_path)
            if len(LEAGUE_POOL) > MAX_LEAGUE_SIZE:
                old = LEAGUE_POOL.pop(0)
                if os.path.exists(old): os.remove(old)
            print(f"  → Đã lưu checkpoint vào League Pool ({len(LEAGUE_POOL)} models)")
            
        # Lưu model chính sau mỗi 500 ván
        if (episode + 1) % 500 == 0:
            torch.save(agent.model.state_dict(), model_path)

    torch.save(agent.model.state_dict(), model_path)
    print("Huấn luyện hoàn tất! Đã lưu model V2.")

if __name__ == "__main__":
    train()
