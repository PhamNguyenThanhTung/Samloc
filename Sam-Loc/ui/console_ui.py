# ui/console_ui.py
import os
from player.human_player import HumanPlayer
from player.bot import RandomBot, BasicBot

class ConsoleUI:
    def __init__(self, game_engine):
        self.engine = game_engine

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def run(self):
        self.clear_screen()
        print("🎴 SÂM LỐC 🎴")
        self.setup()
        while self.engine.state.phase != "FINISHED":
            self.display()
            player = self.engine.get_current_player()
            valid_moves = self.engine.get_valid_moves()
            can_pass = self.engine.can_pass()
            if player.is_human:
                move = player.choose_move(valid_moves, can_pass)
            else:
                move = player.choose_move(valid_moves, can_pass)
            success, msg = self.engine.play_move(move)
            if not success:
                print(f"❌ {msg}")
                input("Nhấn Enter để tiếp tục...")
        self.show_result()

    def setup(self):
        # Tạo danh sách người chơi
        players = [
            HumanPlayer("Bạn", 100000),
            RandomBot("Bot Ngẫu nhiên", 100000),
            BasicBot("Bot Cơ bản", 100000),
            RandomBot("Bot 2", 100000)
        ]
        self.engine.players = players  # gán vào engine
        player_names = [p.name for p in players]
        player_money = [p.money for p in players]
        self.engine.setup_game(player_names, player_money)

    def display(self):
        self.clear_screen()
        print(self.engine.get_game_summary())

    def show_result(self):
        print("\n🎉 KẾT THÚC GAME 🎉")
        print(f"Người thắng: {self.engine.player_names[self.engine.state.winner]}")
        input("Nhấn Enter để thoát...")