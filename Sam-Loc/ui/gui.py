import tkinter as tk
from tkinter import messagebox
import sys
import os
from PIL import Image, ImageTk

# Thêm đường dẫn gốc để import logic và player
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logic.game_engine import GameEngine
from player.human_player import HumanPlayer
from player.bot import RandomBot, BasicBot
from logic.move_validator import validate_move

class SamLocGUI:
    def __init__(self):
        """Khởi tạo cửa sổ game và trạng thái phòng chờ."""
        self.root = tk.Tk()
        self.root.title("Sâm Lốc Pro - Lobby")
        self.root.geometry("1100x850")
        self.root.resizable(False, False)

        self.engine = None
        self.selected_cards = []
        self.move_history = [] 
        self.card_images = {}
        self.bg_photo = None
        self.canvas = None
        self.show_bots = False

        # Quản lý danh sách người chơi (4 slots)
        # Slot 0 luôn là Human (Bạn)
        # Slot 1, 2, 3: True nếu có Bot, False nếu trống
        self.active_slots = [True, False, False, False]
        self.pending_bots = [False, False, False, False] # Bot chờ vào ván sau
        
        self.player_money_storage = [100000] * 4 # Lưu tiền bền vững

        # Kích thước bài
        self.card_width = 70
        self.card_height = 105
        self.card_spacing = 35 
        self.played_card_width = 65 
        self.played_card_height = 95

        self.load_assets()
        self.setup_ui()
        self.update_display()

    def load_assets(self):
        """Tải tài nguyên hình ảnh."""
        bg_path = os.path.join('img', 'table', 'table_background.png')
        if os.path.exists(bg_path):
            bg_img = Image.open(bg_path).resize((1100, 850), Image.Resampling.LANCZOS)
            self.bg_photo = ImageTk.PhotoImage(bg_img)

        suit_map = {'spade': 'spades', 'heart': 'hearts', 'diamond': 'diamonds', 'club': 'clubs'}
        rank_map = {3:'3', 4:'4', 5:'5', 6:'6', 7:'7', 8:'8', 9:'9', 10:'10', 11:'jack', 12:'queen', 13:'king', 14:'ace', 15:'2'}
        base_path = os.path.join('img', 'PNG-cards-1.3')
        
        back_path = os.path.join(base_path, 'back_card.png')
        if os.path.exists(back_path):
            back_img = Image.open(back_path).resize((60, 90), Image.Resampling.LANCZOS)
            self.card_images['back'] = ImageTk.PhotoImage(back_img)

        for rank, rank_name in rank_map.items():
            for suit, suit_name in suit_map.items():
                filename = f"{rank_name}_of_{suit_name}.png"
                path = os.path.join(base_path, filename)
                if os.path.exists(path):
                    img = Image.open(path)
                    self.card_images[(rank, suit)] = ImageTk.PhotoImage(img.resize((self.card_width, self.card_height), Image.Resampling.LANCZOS))
                    self.card_images[(rank, suit, 'played')] = ImageTk.PhotoImage(img.resize((self.played_card_width, self.played_card_height), Image.Resampling.LANCZOS))

    def setup_ui(self):
        """Thiết lập Canvas và các nút chức năng."""
        self.canvas = tk.Canvas(self.root, width=1100, height=850, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Nút chức năng luôn hiện
        self.cheat_btn = tk.Button(self.root, text="Xem bài Bot", bg="#9C27B0", fg="white", font=("Arial", 9, "bold"), width=12, command=self.toggle_show_bots, bd=0)
        self.cheat_btn.place(x=20, y=20)

        self.quit_btn = tk.Button(self.root, text="THOÁT", bg="#f44336", fg="white", font=("Arial", 9, "bold"), width=8, command=self.root.quit, bd=0)
        self.quit_btn.place(x=1010, y=20)

        # Nút điều khiển game
        self.play_btn = tk.Button(self.root, text="ĐÁNH BÀI", bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), width=12, height=2, command=self.play_selected, bd=0)
        self.pass_btn = tk.Button(self.root, text="BỎ LƯỢT", bg="#FF9800", fg="white", font=("Arial", 12, "bold"), width=12, height=2, command=self.pass_turn, bd=0)
        
        # Nút bắt đầu ván/Tiếp tục
        self.start_btn = tk.Button(self.root, text="BẮT ĐẦU", bg="#2196F3", fg="white", font=("Arial", 16, "bold"), width=12, height=2, command=self.start_game_session, bd=0)

    def add_bot(self, slot_idx):
        """Thêm một Bot vào slot trống."""
        if self.engine and self.engine.state.phase == "PLAYING":
            # Đang trong ván, Bot sẽ chờ ván sau
            self.pending_bots[slot_idx] = True
            messagebox.showinfo("Thông báo", f"Bot {slot_idx} sẽ tham gia vào ván sau!")
        else:
            # Game chưa chạy hoặc đã xong, thêm luôn
            self.active_slots[slot_idx] = True
        self.update_display()

    def start_game_session(self):
        """Khởi tạo hoặc bắt đầu ván mới dựa trên các slot đang active."""
        # Áp dụng các bot đang chờ
        for i in range(1, 4):
            if self.pending_bots[i]:
                self.active_slots[i] = True
                self.pending_bots[i] = False

        active_count = sum(1 for s in self.active_slots if s)
        if active_count < 2:
            messagebox.showwarning("Lỗi", "Cần ít nhất 2 người chơi để bắt đầu!")
            return

        # Khởi tạo Engine với số người hiện tại
        self.engine = GameEngine(num_players=active_count)
        
        # Tạo danh sách Player tương ứng
        players = []
        money = []
        # Human
        players.append(HumanPlayer("Bạn", self.player_money_storage[0]))
        money.append(self.player_money_storage[0])
        
        # Thêm các Bot dựa trên slot active (Skip slot 0)
        bot_names = ["Bot 1", "Bot 2", "Bot 3"]
        bot_idx = 0
        for i in range(1, 4):
            if self.active_slots[i]:
                players.append(BasicBot(bot_names[bot_idx], self.player_money_storage[i]))
                money.append(self.player_money_storage[i])
                bot_idx += 1
        
        self.engine.players = players
        self.engine.setup_game([p.name for p in players], money)
        
        self.move_history = []
        self.selected_cards = []
        self.update_display()

    def update_display(self):
        """Cập nhật giao diện bàn chơi và các nút bấm."""
        self.canvas.delete("all")
        if self.bg_photo: self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")

        state = self.engine.state if self.engine else None
        phase = state.phase if state else "MENU"

        # Ẩn hiện các nút điều khiển
        self.play_btn.place_forget()
        self.pass_btn.place_forget()
        self.start_btn.place_forget()

        if phase == "PLAYING":
            if state.current_player == 0:
                self.play_btn.place(x=780, y=750)
                self.pass_btn.place(x=920, y=750)
                self.pass_btn.config(state="disabled" if state.last_move is None else "normal", 
                                     bg="#B0BEC5" if state.last_move is None else "#FF9800")
        else:
            # Hiện nút BẮT ĐẦU nếu đủ điều kiện
            self.start_btn.place(x=450, y=400)

        # Vẽ các Slots (4 phía)
        # Tọa độ: 0: Dưới, 1: Phải, 2: Trên, 3: Trái
        coords = [(550, 650), (950, 380), (550, 100), (150, 380)]
        
        # Human Slot (Luôn hiện)
        self.draw_slot(0, *coords[0])

        # Bot Slots
        for i in range(1, 4):
            if self.active_slots[i]:
                # Vẽ thông tin Bot (Cần ánh xạ index Engine sang index Slot)
                # Tính index thực tế trong engine.players
                idx_in_engine = sum(1 for s in self.active_slots[:i] if s)
                self.draw_slot(i, *coords[i], engine_idx=idx_in_engine)
            else:
                # Vẽ dấu cộng (+)
                self.draw_add_button(i, *coords[i])

        # Vẽ bài tay Bạn
        if self.engine:
            hand = sorted(self.engine.player_hands[0], key=lambda c: (c.rank, c.suit))
            start_x = 550 - (len(hand)*self.card_spacing + self.card_width - self.card_spacing)/2
            for i, card in enumerate(hand):
                y_pos = 710
                if card in self.selected_cards: y_pos -= 25
                cid = self.canvas.create_image(start_x + i*self.card_spacing, y_pos, image=self.card_images[(card.rank, card.suit)], anchor="nw", tags="card")
                if phase == "PLAYING":
                    self.canvas.tag_bind(cid, "<Button-1>", lambda e, c=card: self.toggle_card(c))

            # Vẽ bài chồng trung tâm
            base_center_x, base_center_y = 550, 350
            actual_moves = [m for m in self.move_history if m[1] is not None][-3:]
            for i, (name, cards) in enumerate(actual_moves):
                offset_y, offset_x = (i - 1) * 45, (i - 1) * 30
                move_w = (len(cards) * 25 + self.played_card_width - 25)
                start_x, start_y = base_center_x - move_w/2 + offset_x, base_center_y + offset_y
                for j, card in enumerate(cards):
                    self.canvas.create_image(start_x + j*25, start_y, image=self.card_images[(card.rank, card.suit, 'played')], anchor="nw", tags="history")

            if phase == "PLAYING" and state.current_player > 0:
                self.root.after(800, self.bot_move)

    def draw_slot(self, slot_idx, x, y, engine_idx=0):
        """Vẽ khung người chơi (Human hoặc Bot active)."""
        if not self.engine:
            # Trạng thái chờ (chưa start engine)
            name = "Bạn" if slot_idx == 0 else f"Bot {slot_idx}"
            money = self.player_money_storage[slot_idx]
            self.canvas.create_rectangle(x-70, y-30, x+70, y+30, fill="#111", outline="white", width=2)
            self.canvas.create_text(x, y-10, text=name, fill="white", font=("Arial", 11, "bold"))
            self.canvas.create_text(x, y+12, text=f"{money:,}đ", fill="#00FF00", font=("Arial", 9))
            return

        # Trạng thái game đang chạy
        player = self.engine.players[engine_idx]
        is_turn = (self.engine.state.current_player == engine_idx and self.engine.state.phase == "PLAYING")
        hand_size = len(self.engine.player_hands[engine_idx])
        
        color = "#FFD700" if is_turn else "white"
        bg_c = "#111" if not is_turn else "#330"
        self.canvas.create_rectangle(x-75, y-35, x+75, y+35, fill=bg_c, outline=color, width=2)
        self.canvas.create_text(x, y-15, text=player.name, fill=color, font=("Arial", 11, "bold"))
        self.canvas.create_text(x, y+5, text=f"{hand_size} lá", fill="white", font=("Arial", 9))
        self.canvas.create_text(x, y+22, text=f"{player.money:,}đ", fill="#00FF00", font=("Arial", 9, "bold"))

        if engine_idx > 0:
            # Vẽ bài Bot (Úp hoặc Mở)
            hand = sorted(self.engine.player_hands[engine_idx], key=lambda c: (c.rank, c.suit))
            if self.show_bots:
                # Logic vẽ bài mở như cũ
                if y < 200:
                    sx = x - (len(hand)*20 + self.played_card_width - 20)/2
                    for i, c in enumerate(hand): self.canvas.create_image(sx + i*20, y+40, image=self.card_images[(c.rank, c.suit, 'played')], anchor="nw")
                elif x > 800:
                    sy = y - (len(hand)*20 + self.played_card_height - 20)/2
                    for i, c in enumerate(hand): self.canvas.create_image(x-130, sy + i*20, image=self.card_images[(c.rank, c.suit, 'played')], anchor="nw")
                elif x < 300:
                    sy = y - (len(hand)*20 + self.played_card_height - 20)/2
                    for i, c in enumerate(hand): self.canvas.create_image(x+80, sy + i*20, image=self.card_images[(c.rank, c.suit, 'played')], anchor="nw")
            else:
                bx, by = (x+90, y-30) if x < 300 else (x-150, y-30) if x > 800 else (x-30, y+45)
                self.canvas.create_image(bx, by, image=self.card_images['back'], anchor="nw")
                self.canvas.create_oval(bx+45, by-10, bx+75, by+20, fill="#D32F2F", outline="white")
                self.canvas.create_text(bx+60, by+5, text=str(hand_size), fill="white", font=("Arial", 9, "bold"))

        if is_turn:
            arr = "▲" if y > 600 else "▼" if y < 200 else "◀" if x > 800 else "▶"
            self.canvas.create_text(x, y-55 if y > 600 else y+55 if y < 200 else y, text=arr, fill="yellow", font=("Arial", 20))

    def draw_add_button(self, slot_idx, x, y):
        """Vẽ dấu cộng (+) để thêm Bot."""
        # Hình tròn ngoài
        self.canvas.create_oval(x-30, y-30, x+30, y+30, fill="#2E7D32", outline="white", width=2, tags=f"add_{slot_idx}")
        # Dấu +
        self.canvas.create_text(x, y, text="+", fill="white", font=("Arial", 30, "bold"), tags=f"add_{slot_idx}")
        self.canvas.create_text(x, y+45, text="Thêm Bot", fill="white", font=("Arial", 9), tags=f"add_{slot_idx}")
        
        # Bind sự kiện click
        self.canvas.tag_bind(f"add_{slot_idx}", "<Button-1>", lambda e: self.add_bot(slot_idx))

    def toggle_show_bots(self):
        self.show_bots = not self.show_bots
        self.cheat_btn.config(text="Ẩn bài Bot" if self.show_bots else "Xem bài Bot")
        self.update_display()

    def toggle_card(self, card):
        if card in self.selected_cards: self.selected_cards.remove(card)
        else: self.selected_cards.append(card)
        self.update_display()

    def play_selected(self):
        cur = self.engine.get_current_player()
        if not cur or not cur.is_human or not self.selected_cards: return
        valid, msg = validate_move(cur.hand, self.selected_cards, self.engine.state.last_move)
        if not valid: messagebox.showerror("Lỗi", msg); return
        self.execute_move(self.selected_cards)

    def pass_turn(self):
        if self.engine.state.last_move is None: return
        self.execute_move(None)

    def execute_move(self, move):
        if self.engine.state.last_move is None: self.move_history = []
        p_name = self.engine.get_current_player().name
        if move is not None: self.move_history.append((p_name, move))
        
        res = self.engine.play_move(move)
        
        if success_state(res):
            if self.engine.state.phase == "FINISHED":
                # Đồng bộ tiền ra kho lưu trữ
                self.sync_money_to_storage()
                self.show_end_result()
            self.selected_cards = []
            self.update_display()
        else:
            if move is not None: self.move_history.pop()
            messagebox.showerror("Lỗi", "Nước đi không hợp lệ")

    def sync_money_to_storage(self):
        """Lưu tiền từ engine vào storage để bảo lưu cho ván sau."""
        engine_idx = 0
        for i in range(4):
            if self.active_slots[i]:
                self.player_money_storage[i] = self.engine.player_money[engine_idx]
                engine_idx += 1

    def show_end_result(self):
        scores = self.engine.state.last_scores
        msg = "Ván đấu kết thúc!\n\n"
        for i in range(len(scores)):
            msg += f"{self.engine.player_names[i]}: {'+' if scores[i]>0 else ''}{scores[i]:,}đ\n"
        messagebox.showinfo("Kết quả", msg)

    def bot_move(self):
        cur = self.engine.get_current_player()
        if cur and not cur.is_human and self.engine.state.phase == "PLAYING":
            move = cur.choose_move(self.engine.get_valid_moves(), self.engine.can_pass())
            self.execute_move(move)

    def run(self): self.root.mainloop()

def success_state(res):
    if isinstance(res, bool): return res
    if isinstance(res, tuple): return res[0]
    return False

if __name__ == "__main__":
    gui = SamLocGUI()
    gui.run()