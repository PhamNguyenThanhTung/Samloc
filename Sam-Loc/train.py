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
    criterion = nn.MSELoss() # Hàm mất mát: So sánh Q-value dự đoán và Thực tế

    for episode in range(NUM_EPISODES):
        obs = env.reset()
        done = False
        
        # Lưu trữ lịch sử của ván đấu: (state_tensor, action_tensor, tier_tensor, reward)
        transitions = []

        while not done:
            # Lấy thông tin người chơi hiện tại từ engine
            valid_actions = env.game.get_valid_moves()
            
            # Chọn hành động bằng AI
            action = agent.select_action(obs, valid_actions, is_lead=(env.game.state.last_move is None))
            
            # Đóng gói State, Action, Tier thành Tensor để lát nữa học
            tier_val = evaluate_tier(action)
            
            # Tiền xử lý state giống như trong agent.select_action
            state_vec = np.concatenate([
                obs["M_hand"].flatten(), 
                obs["M_board"].flatten(), 
                obs["V_size"]
            ])
            s_tensor = torch.FloatTensor(state_vec).unsqueeze(0)
            a_tensor = torch.FloatTensor(agent._encode_action(action).flatten()).unsqueeze(0)
            t_tensor = torch.FloatTensor(agent._encode_tier(tier_val)).unsqueeze(0)
            
            # Thực hiện hành động vào môi trường
            next_obs, reward, done, info = env.step(action)
            
            # Lưu lại bước này (lưu tensor để tránh tính toán lại)
            transitions.append((s_tensor, a_tensor, t_tensor, reward))
            
            obs = next_obs

        # --- BẮT ĐẦU CẬP NHẬT TRỌNG SỐ (HỌC) KHI VÁN KẾT THÚC ---
        if not transitions:
            continue

        rewards = [t[3] for t in transitions]
        returns = calculate_returns(rewards, GAMMA) # Tính G_t
        
        agent.model.train() # Chuyển sang chế độ train
        optimizer.zero_grad() # Xóa gradient cũ
        
        episode_loss = 0
        for i, (s_tensor, a_tensor, t_tensor, _) in enumerate(transitions):
            # 1. AI dự đoán Q-value
            predicted_q = agent.model(s_tensor, a_tensor, t_tensor)
            
            # 2. Q-value thực tế tính từ kết quả ván game (G_t)
            target_q = torch.FloatTensor([returns[i]]).unsqueeze(0)
            
            # 3. Tính độ lệch (Loss)
            loss = criterion(predicted_q, target_q)
            episode_loss += loss
            
        # 4. Truyền ngược (Backpropagation) để sửa trọng số nơ-ron
        if len(transitions) > 0:
            avg_loss = episode_loss / len(transitions)
            avg_loss.backward()
            optimizer.step()

        # In tiến độ
        if (episode + 1) % 100 == 0:
            print(f"Ván {episode + 1}/{NUM_EPISODES} - Tổng thưởng: {sum(rewards):.2f} - Loss: {avg_loss.item():.64f}")
            # Lưu model định kỳ mỗi 500 ván
            if (episode + 1) % 500 == 0:
                torch.save(agent.model.state_dict(), model_path)

    # Lưu lại "Bộ não" sau khi học xong
    torch.save(agent.model.state_dict(), model_path)
    print("Huấn luyện hoàn tất! Đã lưu model.")

if __name__ == "__main__":
    train()
