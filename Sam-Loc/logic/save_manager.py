# logic/save_manager.py
import json
import os

SAVE_FILE = "data/save_game.json"

def save_game(player_name, money):
    """Lưu tên người chơi và số tiền vào file JSON."""
    if not os.path.exists("data"):
        os.makedirs("data")
    
    data = {
        "player_name": player_name,
        "money": money
    }
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_game():
    """Tải dữ liệu đã lưu. Nếu không có, trả về mặc định."""
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"player_name": "Bạn", "money": 100000}
