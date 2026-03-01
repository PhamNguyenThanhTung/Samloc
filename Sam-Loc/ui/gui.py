import tkinter as tk
from tkinter import messagebox, simpledialog
import sys
import os
from PIL import Image, ImageTk

# Thêm đường dẫn gốc để import logic và player
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logic.game_engine import GameEngine
from player.human_player import HumanPlayer
from player.bot import BotV0
from player.bot_v1 import BotV1
from player.bot_v2 import BotV2
from logic.move_validator import validate_move
from logic.save_manager import save_game, load_game

class SamLocGUI:
    def __init__(self):
        """Khởi tạo giao diện chính và tải dữ liệu lưu trữ."""
        self.root = tk.Tk()
        self.root.title("Sâm Lốc Pro - Lobby Chỉnh Tùy")
        self.root.geometry("1100x850")
        self.root.resizable(False, False)

        save_data = load_game()
        self.user_name = save_data.get("player_name", "Bạn")
        self.user_money = save_data.get("money", 100000)

        self.engine = None
        self.card_images = {}
        self.bg_photo = None
        self.canvas = None
        self.show_bots = False

        self.slots = [None] * 4 # Vai trò của 4 slot: HUMAN, BOTV0, BOTV1, BOTV2
        self.human_selected = False
        self.player_money_storage = [100000] * 4 
        self.player_money_storage[0] = self.user_money

        self.selected_cards = []
        self.move_history = []

        self.card_width, self.card_height = 70, 105
        self.card_spacing = 35 
        self.played_card_width, self.played_card_height = 65, 95

        self.load_assets()
        self.setup_ui()
        self.update_display()

    def load_assets(self):
        """Tải toàn bộ hình ảnh cần thiết."""
        bg_path = os.path.join('img', 'table', 'table_background.png')
        if os.path.exists(bg_path):
            bg_img = Image.open(bg_path).resize((1100, 850), Image.Resampling.LANCZOS)
            self.bg_photo = ImageTk.PhotoImage(bg_img)

        suit_map = {'spade': 'spades', 'heart': 'hearts', 'diamond': 'diamonds', 'club': 'clubs'}
        rank_map = {3:'3', 4:'4', 5:'5', 6:'6', 7:'7', 8:'8', 9:'9', 10:'10', 11:'jack', 12:'queen', 13:'king', 14:'ace', 15:'2'}
        base_path = os.path.join('img', 'PNG-cards-1.3')
        
        back_path = os.path.join(base_path, 'back_card.png')
        if os.path.exists(back_path):
            self.card_images['back'] = ImageTk.PhotoImage(Image.open(back_path).resize((60, 90), Image.Resampling.LANCZOS))

        for rank, rank_name in rank_map.items():
            for suit, suit_name in suit_map.items():
                filename = f"{rank_name}_of_{suit_name}.png"
                path = os.path.join(base_path, filename)
                if os.path.exists(path):
                    img = Image.open(path)
                    self.card_images[(rank, suit)] = ImageTk.PhotoImage(img.resize((self.card_width, self.card_height), Image.Resampling.LANCZOS))
                    self.card_images[(rank, suit, 'played')] = ImageTk.PhotoImage(img.resize((self.played_card_width, self.played_card_height), Image.Resampling.LANCZOS))

    def setup_ui(self):
        """Khởi tạo Canvas và các nút chức năng."""
        self.canvas = tk.Canvas(self.root, width=1100, height=850, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.cheat_btn = tk.Button(self.root, text="Xem bài Bot", bg="#9C27B0", fg="white", font=("Arial", 9, "bold"), width=12, command=self.toggle_show_bots, bd=0)
        self.quit_btn = tk.Button(self.root, text="THOÁT", bg="#f44336", fg="white", font=("Arial", 9, "bold"), width=8, command=self.root.quit, bd=0)
        self.profile_btn = tk.Button(self.root, text="Đổi Tên", bg="#FF9800", fg="white", font=("Arial", 9, "bold"), width=10, command=self.change_name, bd=0)
        self.profile_btn.place(x=20, y=60)

        self.play_btn = tk.Button(self.root, text="ĐÁNH BÀI", bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), width=12, height=2, command=self.play_selected, bd=0)
        self.pass_btn = tk.Button(self.root, text="BỎ LƯỢT", bg="#FF9800", fg="white", font=("Arial", 12, "bold"), width=12, height=2, command=self.pass_turn, bd=0)
        self.start_btn = tk.Button(self.root, text="BẮT ĐẦU", bg="#2196F3", fg="white", font=("Arial", 16, "bold"), width=12, height=2, command=self.start_game_session, bd=0)

        # UI BÁO SÂM
        self.sam_panel = tk.Frame(self.root, bg="#111", padx=20, pady=20)
        tk.Label(self.sam_panel, text="BẠN CÓ MUỐN BÁO SÂM?", fg="yellow", bg="#111", font=("Arial", 14, "bold")).pack(pady=10)
        btn_box = tk.Frame(self.sam_panel, bg="#111")
        btn_box.pack()
        tk.Button(btn_box, text="BÁO SÂM", bg="#f44336", fg="white", font=("Arial", 12, "bold"), width=10, command=lambda: self.sam_decision(True)).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_box, text="KHÔNG", bg="#757575", fg="white", font=("Arial", 12, "bold"), width=10, command=lambda: self.sam_decision(False)).pack(side=tk.LEFT, padx=10)

    def select_role(self, slot_idx):
        """Mở cửa sổ chọn vai trò cho từng Slot (Bạn / Bot V0 / Bot V1 / Bot V2)."""
        top = tk.Toplevel(self.root)
        top.title(f"Slot {slot_idx+1}")
        top.geometry("250x220")
        top.transient(self.root)
        top.grab_set()

        def set_role(role):
            if role == 'HUMAN': self.human_selected = True
            self.slots[slot_idx] = role
            top.destroy()
            self.update_display()

        if not self.human_selected:
            tk.Button(top, text=f"Người chơi ({self.user_name})", bg="#1976D2", fg="white", pady=5, command=lambda: set_role('HUMAN')).pack(fill="x", padx=20, pady=10)
        
        tk.Button(top, text="Bot V0 (Dễ)", bg="#388E3C", fg="white", pady=5, command=lambda: set_role('BOTV0')).pack(fill="x", padx=20, pady=5)
        tk.Button(top, text="Bot V1 (Khó)", bg="#E64A19", fg="white", pady=5, command=lambda: set_role('BOTV1')).pack(fill="x", padx=20, pady=5)
        tk.Button(top, text="Bot V2 (Cực khó)", bg="#C62828", fg="white", pady=5, command=lambda: set_role('BOTV2')).pack(fill="x", padx=20, pady=5)

    def remove_role(self, slot_idx):
        """Xóa vai trò khỏi slot để dấu (+) hiện lại."""
        if self.slots[slot_idx] == 'HUMAN': self.human_selected = False
        self.slots[slot_idx] = None
        self.update_display()

    def change_name(self):
        """Đổi tên người chơi và lưu vào file."""
        new = simpledialog.askstring("Đổi tên", "Nhập tên mới:", initialvalue=self.user_name)
        if new:
            self.user_name = new
            save_game(self.user_name, self.user_money)
            self.update_display()

    def start_game_session(self):
        """Khởi tạo GameEngine dựa trên các Slot đã chọn."""
        active_count = sum(1 for s in self.slots if s)
        if active_count < 2:
            messagebox.showwarning("Lỗi", "Cần ít nhất 2 người chơi để bắt đầu!"); return

        self.engine = GameEngine(num_players=active_count)
        players, money = [], []
        
        for i, role in enumerate(self.slots):
            if role == 'HUMAN':
                players.append(HumanPlayer(self.user_name, self.player_money_storage[i]))
                money.append(self.player_money_storage[i])
            elif role == 'BOTV0':
                players.append(BotV0(f"Bot V0", self.player_money_storage[i]))
                money.append(self.player_money_storage[i])
            elif role == 'BOTV1':
                players.append(BotV1(f"Bot V1", self.player_money_storage[i]))
                money.append(self.player_money_storage[i])
            elif role == 'BOTV2':
                players.append(BotV2(f"Bot V2", self.player_money_storage[i]))
                money.append(self.player_money_storage[i])
        
        self.engine.players = players
        self.engine.setup_game([p.name for p in players], money)
        self.move_history, self.selected_cards = [], []
        self.update_display()

    def sam_decision(self, decision):
        """Xử lý nút bấm Báo Sâm."""
        idx = self.engine.state.announcement_index
        self.engine.handle_announcement(idx, decision)
        if decision: messagebox.showinfo("Sâm!", f"{self.user_name} BÁO SÂM!")
        self.check_next_announcement()

    def check_next_announcement(self):
        """Hỏi người tiếp theo hoặc vào trận đánh."""
        if self.engine.state.phase == "ANNOUNCING":
            idx = self.engine.state.announcement_index
            cur_p = self.engine.players[idx]
            if isinstance(cur_p, HumanPlayer):
                self.sam_panel.place(x=400, y=350)
            else:
                self.engine.handle_announcement(idx, False)
                self.check_next_announcement()
        else:
            self.sam_panel.place_forget()
            self.update_display()

    def update_display(self):
        """Vẽ lại toàn bộ bàn chơi."""
        self.canvas.delete("all")
        if self.bg_photo: self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")
        
        state = self.engine.state if self.engine else None
        phase = state.phase if state else "LOBBY"

        self.play_btn.place_forget(); self.pass_btn.place_forget()
        self.start_btn.place_forget(); self.cheat_btn.place_forget()
        self.sam_panel.place_forget()

        if phase == "ANNOUNCING":
            self.check_next_announcement()
        elif phase == "PLAYING":
            self.cheat_btn.place(x=20, y=20)
            # Tìm index của Bạn trong engine
            h_idx = -1
            for i, p in enumerate(self.engine.players):
                if p.name == self.user_name: h_idx = i; break
            if state.current_player == h_idx:
                self.play_btn.place(x=780, y=750); self.pass_btn.place(x=920, y=750)
                self.pass_btn.config(state="disabled" if state.last_move is None else "normal")
            if state.sam_announcer != -1:
                name = self.engine.player_names[state.sam_announcer]
                self.canvas.create_text(550, 50, text=f"★ {name} ĐANG BÁO SÂM ★", fill="red", font=("Arial", 20, "bold"))
        else:
            if sum(1 for s in self.slots if s) >= 2: self.start_btn.place(x=450, y=400)

        # Vẽ Slots
        coords = [(550, 650), (950, 380), (550, 100), (150, 380)]
        for i in range(4):
            x, y = coords[i]
            if self.slots[i]:
                e_idx = sum(1 for s in self.slots[:i] if s)
                self.draw_slot(i, x, y, e_idx)
            else:
                self.draw_add_button(i, x, y)

        if self.engine and phase == "PLAYING":
            # Vẽ bài Bạn
            h_idx = -1
            for i, p in enumerate(self.engine.players):
                if p.name == self.user_name: h_idx = i; break
            if h_idx != -1:
                hand = sorted(self.engine.player_hands[h_idx], key=lambda c: (c.rank, c.suit))
                start_x = 550 - (len(hand)*self.card_spacing + self.card_width - self.card_spacing)/2
                for j, card in enumerate(hand):
                    y_pos = 710
                    if card in self.selected_cards: y_pos -= 25
                    cid = self.canvas.create_image(start_x + j*self.card_spacing, y_pos, image=self.card_images[(card.rank, card.suit)], anchor="nw", tags="card")
                    if state.current_player == h_idx:
                        self.canvas.tag_bind(cid, "<Button-1>", lambda e, c=card: self.toggle_card(c))

            # Bài chồng
            base_center_x, base_center_y = 550, 350
            actual_moves = [m for m in self.move_history if m[1] is not None][-3:]
            for k, (name, cards) in enumerate(actual_moves):
                offset_y, offset_x = (k - 1) * 45, (k - 1) * 30
                move_w = (len(cards) * 25 + self.played_card_width - 25)
                sx, sy = base_center_x - move_w/2 + offset_x, base_center_y + offset_y
                for j, card in enumerate(cards):
                    self.canvas.create_image(sx + j*25, sy, image=self.card_images[(card.rank, card.suit, 'played')], anchor="nw", tags="history")

            # Bot đánh
            cur_p = self.engine.get_current_player()
            if cur_p and not isinstance(cur_p, HumanPlayer):
                self.root.after(800, self.bot_move)

    def draw_slot(self, slot_idx, x, y, e_idx):
        money = self.player_money_storage[slot_idx]
        name = "Bot"
        is_turn, hand_size = False, 0
        if self.engine:
            p = self.engine.players[e_idx]
            name, money, hand_size = p.name, p.money, len(self.engine.player_hands[e_idx])
            is_turn = (self.engine.state.current_player == e_idx and self.engine.state.phase == "PLAYING")
        else:
            role = self.slots[slot_idx]
            name = self.user_name if role == 'HUMAN' else f"Bot {role[-2:]}"

        color, bg_c = ("#FFD700" if is_turn else "white"), ("#111" if not is_turn else "#330")
        tag = f"role_{slot_idx}"
        self.canvas.create_rectangle(x-75, y-35, x+75, y+35, fill=bg_c, outline=color, width=2, tags=tag)
        self.canvas.create_text(x, y-15, text=name, fill=color, font=("Arial", 11, "bold"), tags=tag)
        self.canvas.create_text(x, y+22, text=f"{money:,}đ", fill="#00FF00", font=("Arial", 9, "bold"), tags=tag)
        
        if self.engine:
            self.canvas.create_text(x, y+5, text=f"{hand_size} lá", fill="white", font=("Arial", 9), tags=tag)
            if not isinstance(self.engine.players[e_idx], HumanPlayer):
                if self.show_bots:
                    hand = sorted(self.engine.player_hands[e_idx], key=lambda c: (c.rank, c.suit))
                    sx = x - (len(hand)*20 + 40)/2
                    for i, c in enumerate(hand): self.canvas.create_image(sx + i*20, y+40, image=self.card_images[(c.rank, c.suit, 'played')], anchor="nw")
                else:
                    bx, by = (x+90, y-30) if x < 300 else (x-150, y-30) if x > 800 else (x-30, y+45)
                    self.canvas.create_image(bx, by, image=self.card_images['back'], anchor="nw")
                    self.canvas.create_oval(bx+45, by-10, bx+75, by+20, fill="#D32F2F", outline="white")
                    self.canvas.create_text(bx+60, by+5, text=str(hand_size), fill="white", font=("Arial", 9, "bold"))
        else:
            self.canvas.tag_bind(tag, "<Button-1>", lambda e: self.remove_role(slot_idx))

        if is_turn:
            arr = "▲" if y > 600 else "▼" if y < 200 else "◀" if x > 800 else "▶"
            self.canvas.create_text(x, y-55 if y > 600 else y+55 if y < 200 else y, text=arr, fill="yellow", font=("Arial", 20))

    def draw_add_button(self, slot_idx, x, y):
        tag = f"add_{slot_idx}"
        self.canvas.create_oval(x-30, y-30, x+30, y+30, fill="#2E7D32", outline="white", width=2, tags=tag)
        self.canvas.create_text(x, y, text="+", fill="white", font=("Arial", 30, "bold"), tags=tag)
        self.canvas.tag_bind(tag, "<Button-1>", lambda e: self.select_role(slot_idx))

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
        if not cur or not self.selected_cards: return
        valid, msg = validate_move(cur.hand, self.selected_cards, self.engine.state.last_move)
        if not valid: messagebox.showerror("Lỗi", msg); return
        self.execute_move(self.selected_cards)

    def pass_turn(self):
        self.execute_move(None)

    def execute_move(self, move):
        if self.engine.state.last_move is None: self.move_history = []
        p_name = self.engine.get_current_player().name
        if move is not None: self.move_history.append((p_name, move))
        res = self.engine.play_move(move)
        if success_state(res):
            if self.engine.state.phase == "FINISHED":
                self.sync_money_to_storage()
                self.user_money = self.player_money_storage[0]
                save_game(self.user_name, self.user_money)
                self.show_end_result()
            self.selected_cards = []
            self.update_display()
        else:
            if move is not None: self.move_history.pop()
            messagebox.showerror("Lỗi", "Không hợp lệ")

    def sync_money_to_storage(self):
        e_idx = 0
        for i in range(4):
            if self.slots[i]:
                self.player_money_storage[i] = self.engine.player_money[e_idx]
                e_idx += 1

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