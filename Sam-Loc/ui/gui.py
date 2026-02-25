# ui/gui.py
import tkinter as tk
from tkinter import messagebox
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logic.game_engine import GameEngine
from player.human_player import HumanPlayer
from player.bot import RandomBot, BasicBot
from logic.move_validator import validate_move

class SamLocGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sâm Lốc")
        self.root.geometry("900x700")
        self.engine = None
        self.selected_cards = []
        self.card_buttons = []
        self.bot_timer = None
        self.setup_widgets()

    def setup_widgets(self):
        # Khung trên: thông tin người chơi và trạng thái
        self.info_frame = tk.Frame(self.root, bg='lightblue', height=150)
        self.info_frame.pack(fill=tk.X, padx=5, pady=5)
        self.info_label = tk.Label(self.info_frame, text="Chào mừng đến với Sâm Lốc!",
                                   font=('Arial', 12), justify=tk.LEFT, bg='lightblue')
        self.info_label.pack(pady=10, padx=10, anchor='w')

        # Khung giữa: bài trên tay và điều khiển
        self.mid_frame = tk.Frame(self.root)
        self.mid_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Bài của người chơi - các button
        self.hand_frame = tk.LabelFrame(self.mid_frame, text="Bài của bạn (click để chọn)", font=('Arial', 12, 'bold'))
        self.hand_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.hand_inner = tk.Frame(self.hand_frame)
        self.hand_inner.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Khu vực hiển thị các lá đang chọn
        self.selected_frame = tk.LabelFrame(self.mid_frame, text="Các lá đang chọn", font=('Arial', 12, 'bold'))
        self.selected_frame.pack(fill=tk.X, padx=5, pady=5)
        self.selected_label = tk.Label(self.selected_frame, text="", font=('Courier', 14))
        self.selected_label.pack(pady=5)

        # Khung dưới: các nút điều khiển
        self.control_frame = tk.Frame(self.root, height=80)
        self.control_frame.pack(fill=tk.X, padx=5, pady=5)

        self.play_button = tk.Button(self.control_frame, text="Đánh bài", command=self.play_selected,
                                     bg='green', fg='white', font=('Arial', 10, 'bold'))
        self.play_button.pack(side=tk.LEFT, padx=5)

        self.pass_button = tk.Button(self.control_frame, text="Bỏ lượt", command=self.pass_turn,
                                     bg='orange', font=('Arial', 10, 'bold'))
        self.pass_button.pack(side=tk.LEFT, padx=5)

        self.clear_button = tk.Button(self.control_frame, text="Bỏ chọn", command=self.clear_selection,
                                      bg='gray', fg='white', font=('Arial', 10, 'bold'))
        self.clear_button.pack(side=tk.LEFT, padx=5)

        self.restart_button = tk.Button(self.control_frame, text="Chơi lại", command=self.restart_game,
                                        bg='blue', fg='white', font=('Arial', 10, 'bold'))
        self.restart_button.pack(side=tk.LEFT, padx=5)

        self.quit_button = tk.Button(self.control_frame, text="Thoát", command=self.root.quit,
                                     bg='red', fg='white', font=('Arial', 10, 'bold'))
        self.quit_button.pack(side=tk.RIGHT, padx=5)

        # Khởi tạo game
        self.start_game()

    def start_game(self):
        self.engine = GameEngine(num_players=4)
        players = [
            HumanPlayer("Bạn", 100000),
            RandomBot("Bot 1", 100000),
            BasicBot("Bot 2", 100000),
            RandomBot("Bot 3", 100000)
        ]
        self.engine.players = players
        player_names = [p.name for p in players]
        player_money = [p.money for p in players]
        self.engine.setup_game(player_names, player_money)
        self.clear_selection()
        self.update_display()

    def clear_selection(self):
        self.selected_cards = []
        self.update_selected_display()
        for btn in self.card_buttons:
            btn.config(bg='SystemButtonFace', relief='raised')

    def update_selected_display(self):
        if self.selected_cards:
            text = "  ".join(str(c) for c in self.selected_cards)
        else:
            text = "(chưa chọn lá nào)"
        self.selected_label.config(text=text)

    def refresh_card_buttons(self):
        """Cập nhật màu sắc các button để hiển thị lá đang chọn"""
        for btn in self.card_buttons:
            # Lấy text của button để so sánh
            btn_text = btn.cget("text")
            # Kiểm tra nếu lá này có trong selected_cards
            is_selected = any(str(c) == btn_text for c in self.selected_cards)
            if is_selected:
                btn.config(bg='lightgreen', relief='sunken')
            else:
                btn.config(bg='SystemButtonFace', relief='raised')

    def toggle_card(self, card):
        if card in self.selected_cards:
            self.selected_cards.remove(card)
        else:
            self.selected_cards.append(card)
        self.update_selected_display()
        self.refresh_card_buttons()

    def update_display(self):
        state = self.engine.state
        current_player = self.engine.get_current_player()
        if current_player is None:
            return

        # Hủy timer cũ nếu có để tránh bot đánh 2 lần hoặc đánh khi game đã kết thúc
        if self.bot_timer:
            self.root.after_cancel(self.bot_timer)
            self.bot_timer = None

        # Thông tin tổng quan
        info = f"Vòng {state.round} – Lượt: {current_player.name}\n"
        for i, player in enumerate(self.engine.players):
            prefix = "➤" if i == state.current_player else "  "
            hand_size = len(self.engine.player_hands[i])
            money = self.engine.player_money[i]
            announced = " (ĐÃ BÁO)" if i in state.announced_players else ""
            passed = " (ĐÃ BỎ)" if i in state.passed_players else ""
            info += f"{prefix} {player.name}: {hand_size} lá - {money:,}đ{announced}{passed}\n"
        if state.last_move:
            last_str = [str(c) for c in state.last_move]
            info += f"Bài vừa đánh: {', '.join(last_str)}"
        self.info_label.config(text=info)

        # Xóa các button cũ trong hand_inner
        for widget in self.hand_inner.winfo_children():
            widget.destroy()
        self.card_buttons.clear()

        # Nếu là lượt người chơi
        if current_player.is_human:
            hand = current_player.hand
            # Sắp xếp bài để hiển thị đẹp
            hand_sorted = sorted(hand, key=lambda c: (c.rank, c.suit))
            for card in hand_sorted:
                btn = tk.Button(self.hand_inner, text=str(card), font=('Courier', 16),
                                width=4, height=2,
                                command=lambda c=card: self.toggle_card(c))
                btn.pack(side=tk.LEFT, padx=2, pady=5)
                self.card_buttons.append(btn)
            # Cập nhật màu sắc các button dựa vào selected_cards
            self.refresh_card_buttons()
        else:
            # Lượt bot
            label = tk.Label(self.hand_inner, text="(Đến lượt bot...)", font=('Arial', 14))
            label.pack()
            # Chỉ lên lịch cho bot nếu game đang diễn ra
            if state.phase == "PLAYING":
                self.bot_timer = self.root.after(1000, self.bot_move)

    def play_selected(self):
        if self.engine.state.phase != "PLAYING":
            return
        if not self.selected_cards:
            messagebox.showwarning("Chưa chọn bài", "Bạn chưa chọn lá bài nào để đánh.")
            return
        current = self.engine.get_current_player()
        if not current or not current.is_human:
            return

        valid, msg = validate_move(current.hand, self.selected_cards, self.engine.state.last_move)
        if not valid:
            messagebox.showerror("Nước đi không hợp lệ", msg)
            return

        self.execute_move(self.selected_cards)

    def pass_turn(self):
        if self.engine.can_pass():
            self.execute_move(None)
        else:
            messagebox.showwarning("Cảnh báo", "Bạn không thể bỏ lượt khi có thể chặn!")

    def execute_move(self, move):
        success, msg = self.engine.play_move(move)
        if not success:
            messagebox.showerror("Lỗi", msg)
        self.clear_selection()
        self.update_display()
        if self.engine.state.phase == "FINISHED":
            winner = self.engine.player_names[self.engine.state.winner]
            messagebox.showinfo("Kết thúc", f"Người thắng: {winner}")
            self.restart_game()

    def bot_move(self):
        current = self.engine.get_current_player()
        if current and not current.is_human and self.engine.state.phase == "PLAYING":
            valid_moves = self.engine.get_valid_moves()
            can_pass = self.engine.can_pass()
            move = current.choose_move(valid_moves, can_pass)
            self.execute_move(move)
        else:
            self.update_display()

    def restart_game(self):
        self.start_game()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    gui = SamLocGUI()
    gui.run()