"""
Hiển thị thông tin ra màn hình
"""
import os


class Display:
    @staticmethod
    def clear_screen():
        """Xóa màn hình"""
        os.system('cls' if os.name == 'nt' else 'clear')

    @staticmethod
    def print_banner(text):
        """In banner đẹp"""
        border = "=" * (len(text) + 4)
        print(f"\n{border}")
        print(f"  {text}  ")
        print(f"{border}\n")

    @staticmethod
    def print_menu(title, items):
        """In menu"""
        print(f"\n{title}")
        print("-" * len(title))
        for item in items:
            print(item)
        print()

    @staticmethod
    def print_cards(cards, title="Bài"):
        """In danh sách lá bài"""
        print(f"\n{title}:")
        if not cards:
            print("  (trống)")
            return

        # Nhóm bài theo rank để hiển thị đẹp hơn
        from collections import defaultdict
        groups = defaultdict(list)

        for card in cards:
            groups[card.rank].append(card)

        for rank, cards_in_rank in sorted(groups.items()):
            cards_str = " ".join(str(card) for card in cards_in_rank)
            print(f"  {cards_str}")

    @staticmethod
    def print_game_state(state_info):
        """In trạng thái game"""
        print("\n" + "=" * 40)
        print(f"Vòng: {state_info['round']}")
        print(f"Lượt: {state_info['turn']}")
        print(f"Người chơi hiện tại: {state_info['current_player']}")
        print("=" * 40)