# Sâm Lốc Pro - Python Pygame Edition

Một trò chơi đánh bài Sâm Lốc chuyên nghiệp được phát triển bằng ngôn ngữ Python, sử dụng thư viện **Pygame** cho giao diện đồ họa mượt mà (60 FPS). Game hỗ trợ từ 2 đến 4 người chơi (Người chơi thực đấu với Bot thông minh).

## 🌟 Tính năng nổi bật

- **Giao diện hiện đại (Pygame):**
    - Đồ họa mượt mà, hiệu ứng lá bài nhô cao khi chọn.
    - Logic chọn bài thông minh: Ưu tiên lá bài nằm trên cùng khi các lá bài xếp chồng lên nhau.
    - Chế độ **Xem bài Bot** chuyên nghiệp: Bài Bot hàng trên hiện ngang, bài Bot hai bên hiện dọc bám sát cạnh màn hình.
- **Phòng chờ (Lobby) & Session linh hoạt:** 
    - Thêm/Xóa Bot hoặc Người chơi thực vào các vị trí trống bất cứ lúc nào (kể cả khi ván đấu đang diễn ra).
    - Người chơi thêm vào khi đang đánh sẽ ở trạng thái **"(Chờ ván sau)"**.
    - Nút **TIẾP TỤC** ở cuối ván cho phép bắt đầu ván mới ngay lập tức với cấu hình người chơi hiện tại.
- **Luật chơi Sâm Lốc chuẩn:**
    - Đầy đủ các tổ hợp: Đơn, Đôi, Sám, Tứ quý, Sảnh (3 lá trở lên, không phân biệt chất).
    - **Luật Chặn Sâm:** Nếu người báo Sâm bị chặn dù chỉ 1 nước, ván đấu kết thúc ngay lập tức và người báo Sâm phải đền Sâm cho cả làng.
    - Luật Ăn trắng: Sảnh rồng, Tứ quý 2, Đồng màu, 3 Sám cô, 5 Đôi.
- **Hệ thống tính điểm & Tiền:**
    - Tự động lưu tên và số vốn của người chơi thực qua các ván đấu (`data/save_game.json`).
    - Phạt thối 2, phạt Cóng, phạt thối Tứ quý chuẩn luật.

## 🛠 Yêu cầu hệ thống

- Python 3.x
- Thư viện Pygame

## 🚀 Cài đặt và Khởi chạy

1. **Cài đặt thư viện Pygame:**
   ```bash
   pip install pygame
   ```

2. **Tải mã nguồn và asset:**
   Đảm bảo thư mục dự án có đầy đủ thư mục `img/` chứa ảnh bài và `logic/` chứa bộ não của game.

3. **Chạy game:**
   ```bash
   python main.py
   ```

## 📁 Cấu trúc dự án

- `main.py`: Điểm khởi đầu của chương trình.
- `logic/`: Chứa bộ não xử lý game.
    - `game_engine.py`: Điều khiển luồng trận đấu, chặn sâm, chuyển lượt.
    - `rules.py`: Định nghĩa các tổ hợp bài và luật ăn trắng.
    - `move_validator.py`: Kiểm tra tính hợp lệ của nước đi.
    - `scoring.py`: Tính toán tiền thắng/thua.
- `ui/`: Giao diện người dùng.
    - `gui.py`: Toàn bộ logic đồ họa Pygame, xử lý sự kiện click bài và menu.
- `player/`: Quản lý người chơi và AI (Bot V0, V1, V2).
- `img/`: Tài nguyên hình ảnh (Cards, Background).

## 🎮 Hướng dẫn chơi

1. Nhấn dấu **(+)** để thêm người chơi hoặc Bot (tối thiểu 2 người để bắt đầu).
2. Nhấn **BẮT ĐẦU** để chia bài.
3. Trong giai đoạn **Báo Sâm**, xem bài ở dưới và quyết định có báo Sâm hay không.
4. Click vào lá bài để chọn, sau đó nhấn **ĐÁNH** hoặc **BỎ LƯỢT**.
5. Sau khi ván kết thúc, nhấn **TIẾP TỤC** để giữ vốn và đánh ván tiếp theo.

---
*Chúc bạn có những giây phút giải trí vui vẻ!* 🃏
