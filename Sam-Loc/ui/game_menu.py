"""
Menu trong game
"""


class GameMenu:
    @staticmethod
    def show_in_game_menu():
        """Hiển thị menu trong game"""
        print("\n" + "-" * 30)
        print("MENU TRONG GAME")
        print("-" * 30)
        print("1. Tiếp tục chơi")
        print("2. Xem lại bài")
        print("3. Lưu game")
        print("4. Đầu hàng")
        print("5. Thoát game")
        print("-" * 30)

        choice = input("Chọn: ").strip()
        return choice

    @staticmethod
    def show_pause_menu():
        """Hiển thị menu tạm dừng"""
        print("\nGame đã tạm dừng")
        print("1. Tiếp tục")
        print("2. Lưu và thoát")
        print("3. Thoát không lưu")

        choice = input("Chọn: ").strip()
        return choice