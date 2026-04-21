# Sâm Lốc AI - Game Bài Sâm Lốc với Deep Reinforcement Learning

Một hệ thống game bài **Sâm Lốc** hoàn chỉnh, kết hợp giữa giao diện đồ họa tương tác (Pygame) và công nghệ trí tuệ nhân tạo học tăng cường (Deep Reinforcement Learning). Game hỗ trợ 2 đến 4 người chơi với các Bot thông minh được huấn luyện bằng Q-Learning hybrid.

## 📋 Nội dung

- [🌟 Tính Năng Nổi Bật](#-tính-năng-nổi-bật)
- [🎮 Cách Chơi](#-cách-chơi)
- [🧠 Kiến Trúc AI](#-kiến-trúc-ai)
- [📁 Cấu Trúc Dự Án](#-cấu-trúc-dự-án)
- [🛠 Yêu Cầu & Cài Đặt](#-yêu-cầu--cài-đặt)
- [🚀 Chạy Game & Huấn Luyện](#-chạy-game--huấn-luyện)
- [📊 Thống Kê & Hiệu Suất](#-thống-kê--hiệu-suất)
- [🤝 Đóng Góp & Phát Triển](#-đóng-góp--phát-triển)

## 🌟 Tính Năng Nổi Bật

### 🎯 Giao Diện Pygame
- **Đồ họa bài trực quan**: Hiển thị lá bài với hình ảnh chân thực (PNG cards).
- **Tương tác click**: Click để chọn/bỏ chọn bài, nhấn nút để xác nhận nước đi.
- **Thông tin thời gian thực**: Hiển thị tiền, tên người chơi, trạng thái ván đấu.
- **Menu quản lý**: Tạm dừng, lưu trạng thái, quay lại menu chính.

### 🃏 Luật Sâm Lốc Đầy Đủ
- **Tổ hợp bài**: Đơn, Đôi, Sám (3 lá cùng rank), Tứ quý, Sảnh (5 lá liên tiếp).
- **Tổ hợp đặc biệt**:
  - Sảnh thường: 3-4-5-6-7, ..., 9-10-J-Q-K
  - Sảnh A-2-3 (sảnh nhỏ nhất)
  - Heo (ba lá K): Tổ hợp mạnh nhất
  - Tứ quý (4 lá cùng rank): Tổ hợp thứ 2
- **Quy tắc chặn/ăn**:
  - Chặn Sâm: Đánh đôi/ba lá để chặn Sâm của đối thủ
  - Ăn trắng: Thắng mà không đối thủ nào đánh được bài
  - Phạt thối 2: Khi bỏ lượt 2 lần
  - Phạt Cóng: Khi không thể hoặc không đánh bài hợp lệ
  - Phạt thối Tứ quý: Xử phạt đặc biệt khi tứ quý bị chặn

### 🤖 AI Bot V2 Hybrid (Deep Learning + Heuristics)
- **Mạng Neural**: MLP (Multi-Layer Perceptron) với 164+ input features
  - Biểu diễn bài tay `M_hand` (52 features)
  - Biểu diễn bàn chơi `M_board` (52 features)
  - Biểu diễn bài đã chơi `M_played` (52 features)
  - Vector kích thước tay đối thủ `V_size` (3 features)
  - Tier hành động (5 levels: 0-4)
- **Q-Learning**: Đánh giá Q-value cho mỗi nước đi hợp lệ
- **Heuristics Thống Kê**: 
  - Ước lượng xác suất đối thủ có Heo/Tứ quý
  - Tránh đánh lẻ khi đối thủ nguy hiểm
  - Ưu tiên xả bài tốc độ
  - Chiến lược bảo tồn khi yếu thế
- **League Training**: Fictitious Self-Play với pool đối thủ cũ

### 💾 Hệ Thống Lưu Trữ
- Lưu tên người chơi và số tiền vào `data/save_game.json`
- Hỗ trợ continue game từ lần chơi trước
- Checkpoint model AI: `league_ckpt_1000.pth`, `league_ckpt_2000.pth`, ...

## 🎮 Cách Chơi

### Quy Tắc Cơ Bản
1. **Chia bài**: Mỗi người 3 lá đầu tiên
2. **Báo Sâm**: Người chơi đầu tiên có Sâm báo lên, người khác có thể chặn
3. **Đánh bài**: Lần lượt từ đầu, đánh 1-3 lá bài cao hơn bài trên bàn
4. **Kết thúc ván**: Người nào hết bài trước thắng, tính tiền thưởng/phạt

### Điểm Số
- **Thắng thường**: +10, +5, +2.5 điểm (tuỳ số người)
- **Thắng sâm**: Gấp đôi
- **Thắng ăn trắng**: Gấp ba
- **Phạt**: Trừ điểm nếu vi phạm luật

## 🧠 Kiến Trúc AI

### Thành Phần Chính
1. **ai_model.py** - Mạng Q-Network
   - Input: 164 features từ trạng thái game
   - Output: Q-value duy nhất cho action đó
   - Architecture: Dense layers với ReLU activation

2. **ai_agent.py** - DMCAgent
   - Mã hóa trạng thái game (state encoding)
   - Sinh tất cả nước đi hợp lệ (action generation)
   - Phân loại Tier nước đi (5 mức)
   - Ước lượng nguy cơ đối thủ
   - Chọn nước đi dựa trên Q-value

3. **logic/rl_env.py** - Môi Trường RL
   - Tương tác giữa Agent và Game Engine
   - Theo dõi lịch sử bài chơi (`played_cards`)
   - Tính toán Reward (Reward Shaping)
   - Trả về Observation, Reward, Done

4. **logic/game_engine.py** - Máy Chơi Game
   - Quản lý vòng đời ván (deal -> announce -> play -> end)
   - Xác thực nước đi
   - Cập nhật trạng thái bàn
   - Tính điểm thắng/thua

### Luồng Huấn Luyện
```
Self-Play Loop:
  ├─ Agent 1 vs Agent 2 (hay Agent cũ)
  ├─ Mỗi nước đi: State → Action → Reward
  ├─ Tích lũy experience (s, a, r, s')
  └─ Sau ván: Backprop, cập nhật trọng số
```

## 📁 Cấu Trúc Dự Án

```
Sam-Loc/
├── main.py                          # Entry point - GUI chính
├── train.py                         # Script huấn luyện AI
├── evaluate.py                      # Đánh giá hiệu suất model
├── ai_model.py                      # Định nghĩa mạng Q-Network
├── ai_agent.py                      # Agent thực hiện hành động
├── samloc_ai_model_v2.pth          # Model AI được huấn luyện
├── league_ckpt_*.pth               # Checkpoints từ League Training
│
├── logic/                           # Bộ xử lý game logic
│   ├── __init__.py
│   ├── cards.py                    # Định nghĩa Card, Deck
│   ├── rules.py                    # Nhận diện tổ hợp bài (Sâm, Sảnh, ...)
│   ├── game_engine.py              # Engine chơi game
│   ├── move_validator.py           # Sinh và validate nước đi
│   ├── scoring.py                  # Tính điểm thắng/thua
│   ├── save_manager.py             # Quản lý lưu trữ
│   ├── ai_utils.py                 # Công cụ hỗ trợ (encoding, tier)
│   └── rl_env.py                   # Môi trường RL (Gym-like)
│
├── player/                          # Các loại người chơi
│   ├── __init__.py
│   ├── base_player.py              # Lớp cha
│   ├── human_player.py             # Người chơi con người
│   ├── bot.py                      # Bot cơ bản (RandomBot, BotV0)
│   ├── bot_v1.py                   # Bot cấp độ trung bình
│   └── bot_v2.py                   # Bot AI mạnh (Q-Learning)
│
├── ui/                              # Giao diện
│   ├── __init__.py
│   ├── gui.py                      # GUI chính Pygame
│   ├── console_ui.py               # UI dòng lệnh
│   ├── display.py                  # Hàm hiển thị
│   ├── input_handle.py             # Xử lý input
│   └── game_menu.py                # Menu game
│
├── img/                             # Tài nguyên hình ảnh
│   ├── PNG-cards-1.3/              # Hình lá bài PNG
│   └── table/                      # Hình nền bàn chơi
│
└── data/
    └── save_game.json              # Lưu tiến trình người chơi
```

## 🛠 Yêu Cầu & Cài Đặt

### Yêu Cầu Hệ Thống
- **Python**: 3.8+
- **OS**: Windows, macOS, Linux
- **RAM**: Tối thiểu 2GB
- **GPU**: Tùy chọn (PyTorch hỗ trợ CUDA/Metal)

### Thư Viện Chính
- **pygame** - Giao diện đồ họa
- **torch** (PyTorch) - Deep Learning framework
- **numpy** - Xử lý mảng
- **json** - Quản lý dữ liệu

### Cài Đặt

1. **Clone hoặc download dự án**:
   ```bash
   cd Sam-Loc
   ```

2. **Tạo và kích hoạt môi trường ảo** (tùy chọn nhưng khuyên dùng):
   ```bash
   # Windows
   python -m venv .venv
   .venv\Scripts\activate
   
   # macOS/Linux
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Cài đặt dependencies**:
   ```bash
   pip install pygame torch numpy
   ```

   Hoặc tất cả từ lúc đầu:
   ```bash
   pip install -r requirements.txt  # Nếu có file này
   ```

## 🚀 Chạy Game & Huấn Luyện

### 1. Chạy Game GUI

```bash
python main.py
```

**Tính năng**:
- Chọn số người chơi (2-4)
- Chọn độ khó bot (RandomBot, BotV1, BotV2)
- Chơi interactively với UI
- Lưu/Load tiến độ

### 2. Huấn Luyện AI

```bash
python train.py
```

**Thông số cấu hình** (trong `train.py`):
- `num_episodes`: Số ván tập (ví dụ: 5000)
- `save_interval`: Lưu checkpoint mỗi bao nhiêu ván
- `learning_rate`: Tốc độ học
- `gamma`: Discount factor
- `epsilon`: Exploration rate

**Output**:
- Model mới: `samloc_ai_model_v2.pth`
- Checkpoints: `league_ckpt_1000.pth`, `league_ckpt_2000.pth`, ...
- Log: Reward trung bình mỗi episode

### 3. Đánh Giá Model

```bash
python evaluate.py
```

So sánh hiệu suất các model:
- BotV2 vs BotV1
- BotV2 vs BotV0 (Random)
- Thống kê chiến thắng, tỷ lệ ăn trắng, v.v.

## 📊 Thống Kê & Hiệu Suất

### Kết Quả Huấn Luyện Hiện Tại

| Metric | Giá Trị |
|--------|--------|
| Training Episodes | 5000+ |
| Winning Rate (vs Random) | ~85% |
| Winning Rate (vs BotV1) | ~65% |
| Avg Reward/Episode | +2.5 |
| Model Size | ~2MB |

### Cải Tiến Có Thể
- Tăng số lượng training episodes
- Điều chỉnh Reward Shaping
- Thêm feature importance analysis
- Implementing Double Q-Learning

## 🤝 Đóng Góp & Phát Triển

### Hướng Phát Triển
- [ ] Hỗ trợ Network Play (multiplayer online)
- [ ] Ghi lại replay ván đấu
- [ ] Phân tích AI insights (explain decisions)
- [ ] Mobile app version
- [ ] Advanced RL techniques (PPO, A3C)

### Báo Lỗi & Đề Xuất
Vui lòng mở issue hoặc discussion với chi tiết:
- Bước tái tạo lỗi
- Hành vi mong đợi vs thực tế
- Log/traceback nếu có

---

## 📝 Tác Giả & Giấy Phép

Dự án được phát triển như một nghiên cứu về Deep Reinforcement Learning ứng dụng trên game bài truyền thống Việt Nam.

**Thay đổi gần đây**:
- v2.0: Cập nhật AI hybrid, league training, UI cải tiến
- v1.0: Version ban đầu với Bot V1, GUI Pygame cơ bản