import time
from logic.game_engine import GameEngine # Đảm bảo import đúng đường dẫn GameEngine của cậu
from player.bot_v2 import BotV2
from player.bot_v1 import BotV1
# Giả sử file bot_v0.py chứa class BotV0. Cậu nhớ sửa lại tên class/import cho đúng nhé!
from player.bot import BotV0 

def run_evaluation(num_games=100):
    print(f"BẮT ĐẦU GIẢI ĐẤU MÔ PHỎNG {num_games} VÁN SÂM LỐC...")
    print("Thành phần tham dự: 1 Bot V2 (AI), 1 Bot V1 (Heuristics), 2 Bot V0 (Tham lam)")
    print("-" * 50)
    
    # Biến lưu trữ số trận thắng
    win_counts = {
        "Bot V2 (Hybrid AI)": 0,
        "Bot V1 (Heuristics)": 0,
        "Bot V0 (Ngốc nghếch 1)": 0,
        "Bot V0 (Ngốc nghếch 2)": 0
    }
    
    start_time = time.time()

    for i in range(num_games):
        # 1. Khởi tạo người chơi cho ván mới
        players = [
            BotV2("Bot V2 (Hybrid AI)", money=100000),
            BotV1("Bot V1 (Heuristics)", money=100000),
            BotV0("Bot V0 (Ngốc nghếch 1)", money=100000),
            BotV0("Bot V0 (Ngốc nghếch 2)", money=100000)
        ]
        
       # 2. Khởi tạo bàn chơi (Engine)
        engine = GameEngine(4)
        engine.players = players 
        
        # GỌI HÀM CHIA BÀI CHUẨN CỦA CẬU
        if hasattr(engine, 'setup_game'):
            # Thường setup_game sẽ khởi tạo lại bộ bài và chia cho người chơi
            engine.setup_game() 
        else:
            print("Cảnh báo: Không tìm thấy hàm setup_game, hãy kiểm tra lại engine.")

        # --- ĐỒNG BỘ BÀI TỪ ENGINE SANG BOT ---
        # Dựa trên dir(engine), biến chứa bài của cậu chắc chắn là 'player_hands'
        if hasattr(engine, 'player_hands') and engine.player_hands:
            for idx in range(4):
                # Đưa bài từ engine vào tay của từng Bot để Bot có bài mà tính toán
                players[idx].hand = engine.player_hands[idx]
        
        # Kiểm tra lại lần cuối
        if len(players[0].hand) == 0:
            print(f"\n[LỖI] Ván {i}: Bài vẫn rỗng sau khi gọi setup_game!")
            return
        # 3. Vòng lặp ván đấu
        move_count = 0
        while all(len(p.hand) > 0 for p in engine.players) and move_count < 500:
            current_idx = engine.state.current_player
            current_player = engine.players[current_idx]
            
            # 1. Lấy danh sách nước đi (Không truyền tham số)
            valid_moves = engine.get_valid_moves() 
            
            # 2. Kiểm tra quyền bỏ lượt
            can_pass = engine.state.last_move is not None
            
            # 3. Bot suy luận
            # Chỉ đưa 'game_engine' cho Bot V1 và V2 (vì chúng biết dùng)
            # Còn Bot V0 thì chỉ đưa những cái cơ bản
            if isinstance(current_player, (BotV2, BotV1)):
                action = current_player.choose_move(valid_moves, can_pass=can_pass, game_engine=engine)
            else:
                # Đây là trường hợp dành cho Bot V0
                action = current_player.choose_move(valid_moves, can_pass=can_pass)
            
            # 4. Thực hiện nước đi (Chỉ truyền action)
            engine.play_move(action)
            
            move_count += 1
        
            
        # 4. Tìm người chiến thắng (Người hết bài đầu tiên)
        # Quét tay tìm người còn 0 lá bài cho chắc cốp
        for p in players:
            if len(p.hand) == 0:
                win_counts[p.name] += 1
                break
                
        # In tiến độ cho đỡ chán
        if (i + 1) % 10 == 0:
            print(f"Đã đánh xong {i + 1}/{num_games} ván...")

    end_time = time.time()
    
    # --- IN KẾT QUẢ RA MÀN HÌNH ---
    print("\n" + "="*50)
    print(f"🏆 KẾT QUẢ WIN RATE SAU {num_games} VÁN 🏆")
    print("="*50)
    for name, wins in win_counts.items():
        win_rate = (wins / num_games) * 100
        print(f" - {name: <25}: {wins} trận thắng ({win_rate:.1f}%)")
    print(f"\nThời gian chạy: {end_time - start_time:.2f} giây")

if __name__ == "__main__":
    run_evaluation(100)