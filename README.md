# Sâm Lốc Pro - Python Tkinter Edition

Một trò chơi đánh bài Sâm Lốc chuyên nghiệp được phát triển bằng ngôn ngữ Python, sử dụng thư viện Tkinter cho giao diện đồ họa và Pillow để xử lý hình ảnh. Game hỗ trợ từ 2 đến 4 người chơi (Bạn đấu với máy).

## 🌟 Tính năng nổi bật

- **Giao diện hiện đại:** Sử dụng ảnh thật của các lá bài (kích thước 60x90 px) và ảnh nền bàn chơi chân thực.
- **Phòng chờ (Lobby) linh hoạt:** 
    - Bắt đầu ván chơi chỉ với chính bạn.
    - Thêm Bot vào ván đấu bằng cách nhấn các dấu cộng (+) ở các vị trí trống.
    - Bot có thể được thêm ngay lập tức hoặc chờ vào ván sau nếu game đang diễn ra.
- **Luật chơi Sâm Lốc chuẩn:**
    - Đầy đủ các tổ hợp: Đơn, Đôi, Sám, Tứ quý, Sảnh (3 lá trở lên, không phân biệt chất).
    - Luật Chặn bài: Tứ quý chặn được 2, sảnh chặn sảnh cùng độ dài...
    - Luật Ăn trắng: Sảnh rồng, Tứ quý 2, Đồng màu, 3 Sám cô, 5 Đôi.
- **Hệ thống tính điểm chuyên nghiệp:**
    - Tính tiền thắng/thua sau mỗi ván dựa trên số lá còn lại.
    - Phạt thối 2 (10 lá), phạt Cóng (20 lá), phạt thối Tứ quý (20 lá).
    - Số vốn của người chơi được bảo lưu và tích lũy qua các ván đấu.
- **Trải nghiệm thực tế:**
    - Bài đã đánh được xếp chồng thẩm mỹ ở giữa bàn với hiệu ứng lệch (offset) để nhìn rõ lịch sử.
    - Tự động dọn bàn khi bắt đầu vòng mới.
    - Hiệu ứng nhô cao lá bài khi chọn.
- **Công cụ Debug/Cheat:** Nút "Xem bài Bot" cho phép lật bài máy để kiểm tra logic.

## 🛠 Yêu cầu hệ thống

- Python 3.x
- Thư viện Pillow (PIL)

## 🚀 Cài đặt và Khởi chạy

1. **Cài đặt thư viện Pillow:**
   ```bash
   pip install Pillow
   ```

2. **Tải mã nguồn và asset:**
   Đảm bảo thư mục dự án có đầy đủ các file logic và thư mục `img/` chứa ảnh bài.

3. **Chạy game:**
   ```bash
   python main.py
   ```

## 📁 Cấu trúc dự án

- `main.py`: Điểm khởi đầu của chương trình.
- `logic/`: Chứa bộ não của game.
    - `game_engine.py`: Điều khiển luồng trận đấu, chuyển lượt, tính điểm.
    - `rules.py`: Định nghĩa các loại tổ hợp và luật chặn bài.
    - `move_validator.py`: Kiểm tra tính hợp lệ của từng nước đi.
    - `scoring.py`: Hệ thống tính toán tiền thắng thua.
    - `cards.py`: Quản lý lá bài và bộ bài.
- `player/`: Quản lý người chơi.
    - `human_player.py`: Xử lý tương tác của người chơi thực.
    - `bot.py`: Trí tuệ nhân tạo của máy (Basic Bot).
- `ui/`: Giao diện người dùng.
    - `gui.py`: Toàn bộ logic giao diện đồ họa Tkinter.
- `img/`: Tài nguyên hình ảnh (Cards, Background).

## 🎮 Hướng dẫn chơi

1. Nhấn dấu **(+)** để thêm Bot vào bàn chơi (tối thiểu 1 Bot).
2. Nhấn **BẮT ĐẦU** để chia bài.
3. Click vào các lá bài trên tay để chọn (lá bài sẽ nhô lên).
4. Nhấn **ĐÁNH BÀI** để hạ bài hoặc **BỎ LƯỢT** nếu không muốn chặn.
5. Sau khi kết thúc, chọn **TIẾP TỤC** để giữ số vốn hiện tại hoặc **TRANG CHỦ** để reset.

---
*Chúc bạn có những giây phút giải trí vui vẻ!* 🃏
