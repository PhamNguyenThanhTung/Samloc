import pygame
import sys
import os
import math

# Thêm đường dẫn gốc để import logic và player
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logic.game_engine import GameEngine
from player.human_player import HumanPlayer
from player.bot import BotV0
from player.bot_v1 import BotV1
from player.bot_v2 import BotV2
from logic.move_validator import validate_move
from logic.save_manager import save_game, load_game

# --- CẤU HÌNH ---
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

# Màu sắc
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GOLD = (255, 215, 0)
RED = (200, 40, 40)
GREEN_DARK = (20, 70, 20)
GRAY_DARK = (40, 40, 40)
BLUE_SOFT = (50, 100, 200)


class SamLocGUI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Sâm Lốc Pro - Pygame Edition")
        self.clock = pygame.time.Clock()
        self.running = True

        save_data = load_game()
        self.user_name = save_data.get("player_name", "Bạn")
        self.user_money = save_data.get("money", 100000)

        self.engine = None
        self.slots = [None] * 4
        self.session_slots = [None] * 4
        self.last_roster = [None] * 4
        self.prev_winner_idx = None

        self.human_selected = False
        self.player_money_storage = [100000] * 4

        self.selected_cards = []
        self.dealing_anim = None  # {'cards': [...], 'timer': 0, 'done': False}
        self.move_history = []
        self.board_display = []  # Bài hiển thị giữa sân vòng hiện tại [(name, cards), ...]
        self.show_bots = False

        self.turn_start_time = 0
        self.current_turn_player = -1

        self.menu_active = -1
        self.font_main = pygame.font.SysFont("Segoe UI", 22, bold=True)
        self.font_small = pygame.font.SysFont("Segoe UI", 18, bold=True)
        self.font_big = pygame.font.SysFont("Segoe UI", 36, bold=True)

        self.card_images = {}
        self.load_assets()

        self.slot_coords = [
            (SCREEN_WIDTH // 2, 650),
            (1050, SCREEN_HEIGHT // 2),
            (SCREEN_WIDTH // 2, 120),
            (150, SCREEN_HEIGHT // 2)
        ]

    def load_assets(self):
        bg_path = os.path.join('img', 'table', 'table_background.jpg')
        if os.path.exists(bg_path):
            self.bg_img = pygame.image.load(bg_path).convert()
            self.bg_img = pygame.transform.scale(self.bg_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
        else:
            self.bg_img = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.bg_img.fill(GREEN_DARK)

        suit_map = {'spade': 'spades', 'heart': 'hearts', 'diamond': 'diamonds', 'club': 'clubs'}
        rank_map = {3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9', 10: '10', 11: 'jack', 12: 'queen',
                    13: 'king', 14: 'ace', 15: '2'}
        base_path = os.path.join('img', 'PNG-cards-1.3')

        for rank, rank_name in rank_map.items():
            for suit, suit_name in suit_map.items():
                filename = f"{rank_name}_of_{suit_name}.png"
                path = os.path.join(base_path, filename)
                if os.path.exists(path):
                    img = pygame.image.load(path).convert_alpha()
                    self.card_images[(rank, suit)] = pygame.transform.scale(img, (80, 115))
                    self.card_images[(rank, suit, 'small')] = pygame.transform.scale(img, (60, 85))

        back_path = os.path.join(base_path, 'back_card.png')
        if os.path.exists(back_path):
            self.card_images['back'] = pygame.transform.scale(pygame.image.load(back_path).convert_alpha(), (70, 100))

    def run(self):
        while self.running:
            self.handle_events()
            self.update_logic()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.on_click(event.pos)

    def update_logic(self):
        # Cập nhật hiệu ứng chia bài
        if self.dealing_anim and not self.dealing_anim['done']:
            if pygame.time.get_ticks() - self.dealing_anim['timer'] > 120:  # 120ms/lá
                self.dealing_anim['revealed'] += 1
                self.dealing_anim['timer'] = pygame.time.get_ticks()
                if self.dealing_anim['revealed'] >= self.dealing_anim['total']:
                    self.dealing_anim['done'] = True
            return  # chặn bot đánh trong khi đang chia bài
        if self.engine and self.engine.state.phase == "PLAYING":
            cur_p_idx = self.engine.state.current_player

            # [MỚI] 1. Nếu chuyển lượt, reset đồng hồ về 0
            if cur_p_idx != self.current_turn_player:
                self.turn_start_time = pygame.time.get_ticks()
                self.current_turn_player = cur_p_idx

            cur_p = self.engine.get_current_player()

            # 2. Xử lý cho BOT (Delay 1 giây)
            if cur_p and not cur_p.is_human:
                if not hasattr(self, 'bot_timer'): self.bot_timer = pygame.time.get_ticks()
                if pygame.time.get_ticks() - self.bot_timer > 1000:
                    valid_moves = self.engine.get_valid_moves()
                    can_pass = self.engine.can_pass()
                    if isinstance(cur_p, (BotV1, BotV2)):
                        move = cur_p.choose_move(valid_moves, can_pass, game_engine=self.engine)
                    else:
                        move = cur_p.choose_move(valid_moves, can_pass)
                    self.execute_move(move)
                    delattr(self, 'bot_timer')

            # [MỚI] 3. Xử lý đếm ngược 30s cho NGƯỜI THẬT
            elif cur_p and cur_p.is_human:
                elapsed_seconds = (pygame.time.get_ticks() - self.turn_start_time) / 1000
                if elapsed_seconds >= 30:
                    print("[GUI] Hết 30 giây! Auto-play kích hoạt.")
                    if self.engine.state.last_move is None:
                        # Đi đầu: Chọn lá nhỏ nhất (sort theo rank rồi đến suit)
                        hand = self.engine.player_hands[cur_p_idx]
                        smallest_card = sorted(hand, key=lambda c: (c.rank, c.suit))[0]
                        self.execute_move([smallest_card])
                    else:
                        # Bị đè: Tự động bỏ lượt
                        self.execute_move([])

        if self.engine and self.engine.state.phase == "ANNOUNCING":
            idx = self.engine.state.announcement_index
            if idx < len(self.engine.players) and not self.engine.players[idx].is_human:
                self.engine.handle_announcement(idx, False)

    def on_click(self, pos):
        phase = self.engine.state.phase if self.engine else "LOBBY"
        if self.menu_active != -1:
            self.handle_menu_click(pos)
            return

        for i, coord in enumerate(self.slot_coords):
            rect = pygame.Rect(coord[0] - 75, coord[1] - 40, 150, 80)
            if rect.collidepoint(pos):
                if self.slots[i]:
                    is_in_session = self.engine and self.session_slots[i] and phase != "FINISHED"
                    if not is_in_session:
                        if self.slots[i] == 'HUMAN': self.human_selected = False
                        self.slots[i] = None
                        self.player_money_storage[i] = 100000
                    else:
                        if i == 0 and phase == "PLAYING":
                            continue
                        return
                else:
                    if self.player_money_storage[i] < 20000: return
                    self.menu_active = i
                return

        if pygame.Rect(SCREEN_WIDTH - 120, 20, 100, 40).collidepoint(pos):
            self.running = False
            return

        if phase == "LOBBY":
            if pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 40, 200, 80).collidepoint(pos):
                self.start_game_session()
                return

        elif phase == "PLAYING":
            if pygame.Rect(20, 20, 140, 45).collidepoint(pos): self.show_bots = not self.show_bots
            h_idx = self.get_human_index()
            if h_idx != -1 and self.engine.state.current_player == h_idx:
                if pygame.Rect(950, 700, 110, 50).collidepoint(pos):
                    if self.selected_cards:  # chỉ thử đánh khi đã chọn bài
                        self.play_selected_cards()
                if self.engine.state.last_move is not None:
                    if pygame.Rect(1070, 700, 110, 50).collidepoint(pos): self.execute_move(None)
                hand = sorted(self.engine.player_hands[h_idx], key=lambda c: (c.rank, c.suit))
                start_x = SCREEN_WIDTH // 2 - (len(hand) * 40 + 80 - 40) // 2
                for i in range(len(hand) - 1, -1, -1):
                    card = hand[i]
                    y_off = 630 if card in self.selected_cards else 660
                    rect = pygame.Rect(start_x + i * 40, y_off, 80, 115)
                    if rect.collidepoint(pos):
                        if card in self.selected_cards:
                            self.selected_cards.remove(card)
                        else:
                            self.selected_cards.append(card)
                        return

        elif phase == "ANNOUNCING":
            h_idx = self.get_human_index()
            if h_idx != -1 and self.engine.state.announcement_index == h_idx:
                if pygame.Rect(SCREEN_WIDTH // 2 - 110, 400, 100, 50).collidepoint(
                    pos): self.engine.handle_announcement(h_idx, True)
                if pygame.Rect(SCREEN_WIDTH // 2 + 10, 400, 100, 50).collidepoint(pos): self.engine.handle_announcement(
                    h_idx, False)

        elif phase == "FINISHED":
            if pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 100, 200, 60).collidepoint(pos):
                self.start_game_session()

    def get_menu_info(self, idx):
        x, y = self.slot_coords[idx]
        options = []
        if not self.human_selected: options.append(('Người chơi', 'HUMAN'))
        options += [('Bot Dễ', 'BOTV0'), ('Bot Khó', 'BOTV1'), ('Cực khó', 'BOTV2')]
        menu_h = len(options) * 35 + 10
        menu_y = y + 45
        if menu_y + menu_h > SCREEN_HEIGHT: menu_y = y - 45 - menu_h
        rects = []
        for i, (label, role_key) in enumerate(options):
            rects.append((pygame.Rect(x - 75, menu_y + i * 35, 150, 30), label, role_key))
        return rects, pygame.Rect(x - 80, menu_y - 5, 160, menu_h)

    def handle_menu_click(self, pos):
        rects, _ = self.get_menu_info(self.menu_active)
        for rect, label, role_key in rects:
            if rect.collidepoint(pos):
                self.slots[self.menu_active] = role_key
                if role_key == 'HUMAN':
                    self.human_selected = True
                    self.player_money_storage[self.menu_active] = self.user_money
                else:
                    self.player_money_storage[self.menu_active] = 100000
                self.menu_active = -1
                return
        self.menu_active = -1

    def start_game_session(self):
        active_count = sum(1 for s in self.slots if s)
        if active_count < 2:
            print("Không đủ người chơi! Reset về Lobby.")
            self.engine = None
            return

        force_smallest = (self.slots != self.last_roster)
        if force_smallest: self.prev_winner_idx = None
        self.session_slots = self.slots[:]
        self.last_roster = self.slots[:]
        self.engine = GameEngine(num_players=active_count)
        players, money = [], []
        for i, role in enumerate(self.session_slots):
            if not role: continue
            m = self.player_money_storage[i]
            if role == 'HUMAN':
                players.append(HumanPlayer(self.user_name, m))
            elif role == 'BOTV0':
                players.append(BotV0("Bot V0", m))
            elif role == 'BOTV1':
                players.append(BotV1("Bot V1", m))
            elif role == 'BOTV2':
                players.append(BotV2("Bot V2", m))
            money.append(m)
        self.engine.players = players
        self.engine.setup_game([p.name for p in players], money, prev_winner_idx=self.prev_winner_idx,
                               force_smallest=force_smallest)
        self.move_history, self.selected_cards, self.board_display = [], [], []
        self.start_deal_animation()

    def execute_move(self, move):
        p_name = self.engine.get_current_player().name
        # Lưu last_move trước khi engine xử lý để phát hiện vòng mới
        prev_last_move = self.engine.state.last_move
        valid, msg = self.engine.play_move(move)
        if not valid:
            print(f"[GUI] Nước đi thất bại: {msg}")
            return
        if move:
            self.move_history.append((p_name, move))
            if len(self.move_history) > 50:
                self.move_history = self.move_history[-50:]
            # Cập nhật bài hiển thị giữa sân
            self.board_display.append((p_name, move))
        else:
            # Người chơi bỏ lượt — vẫn giữ board_display để thấy bài trên bàn
            pass

        # Phát hiện vòng mới: last_move vừa reset về None (tất cả đã pass, người thắng lượt đi tiếp)
        # => Xóa sạch bài giữa sân
        if self.engine.state.last_move is None and self.engine.state.phase == "PLAYING":
            self.board_display = []

        self.selected_cards = []
        if self.engine.state.phase == "FINISHED":
            self.board_display = []  # Xóa sân khi ván kết thúc
            self.prev_winner_idx = self.engine.state.winner
            self.sync_money()
            for i, role in enumerate(self.session_slots):
                if role == 'HUMAN':
                    self.user_money = self.player_money_storage[i]
                    save_game(self.user_name, self.user_money)
                    break

    def play_selected_cards(self):
        h_idx = self.get_human_index()
        if h_idx == -1: return
        cur = self.engine.players[h_idx]
        valid, _ = validate_move(cur.hand, self.selected_cards, self.engine.state.last_move)
        if valid: self.execute_move(self.selected_cards)

    def sync_money(self):
        e_idx = 0
        any_kicked = False
        for i in range(4):
            if self.session_slots[i]:
                if self.engine and e_idx < len(self.engine.player_money):
                    new_money = self.engine.player_money[e_idx]
                    self.player_money_storage[i] = new_money
                    if new_money < 20000:
                        if self.slots[i] == 'HUMAN':
                            self.human_selected = False
                            self.user_money = 100000
                        self.slots[i] = None
                        self.player_money_storage[i] = 100000
                        any_kicked = True
                e_idx += 1
        if any_kicked: self.last_roster = [None] * 4

    def get_human_index(self):
        if not self.engine: return -1
        e_idx = 0
        for i, role in enumerate(self.session_slots):
            if role == 'HUMAN': return e_idx
            if role: e_idx += 1
        return -1

    def draw(self):
        self.screen.blit(self.bg_img, (0, 0))
        phase = self.engine.state.phase if self.engine else "LOBBY"
        for i, coord in enumerate(self.slot_coords):
            self.draw_slot(i, coord)
        if phase == "LOBBY":
            if sum(1 for s in self.slots if s) >= 2:
                self.draw_button("BẮT ĐẦU", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 40, 200, 80, BLUE_SOFT)
        elif phase == "PLAYING" or phase == "ANNOUNCING":
            btn_txt = "ẨN BÀI BOT" if self.show_bots else "XEM BÀI BOT"
            self.draw_button(btn_txt, 20, 20, 140, 45, (150, 50, 150))
            self.draw_gameplay()
            if phase == "ANNOUNCING":
                h_idx = self.get_human_index()
                if h_idx != -1 and self.engine.state.announcement_index == h_idx:
                    self.draw_sam_panel()
        elif phase == "FINISHED":
            self.draw_end_result()
        if self.menu_active != -1: self.draw_role_menu(self.menu_active)
        self.draw_button("THOÁT", SCREEN_WIDTH - 120, 20, 100, 40, RED)
        pygame.display.flip()

    def draw_slot(self, i, pos):
        x, y = pos
        role = self.slots[i]
        is_turn = False
        use_engine = False

        if self.engine and self.session_slots[i]:
            e_idx = 0
            for j in range(i):
                if self.session_slots[j]: e_idx += 1
            if e_idx < len(self.engine.players):
                use_engine = True
                if self.engine.state.phase == "PLAYING" and self.engine.state.current_player == e_idx:
                    is_turn = True

        # Màu viền đổi thành Vàng nếu đang đến lượt
        color = GOLD if is_turn else WHITE
        pygame.draw.rect(self.screen, GRAY_DARK, (x - 75, y - 40, 150, 80), border_radius=10)
        pygame.draw.rect(self.screen, color, (x - 75, y - 40, 150, 80), 3, border_radius=10)

        if not role:
            txt = self.font_big.render("+", True, WHITE)
            self.screen.blit(txt, (x - txt.get_width() // 2, y - txt.get_height() // 2))
        else:
            name = self.user_name if role == 'HUMAN' else f"Bot {role[-2:]}"
            money = self.player_money_storage[i]
            is_pending = self.engine and not self.session_slots[i] and self.engine.state.phase != "FINISHED"

            txt_n = self.font_main.render(name, True, color if not is_pending else (150, 150, 150))
            txt_m = self.font_small.render(f"{money:,}đ", True, (100, 255, 100))
            self.screen.blit(txt_n, (x - txt_n.get_width() // 2, y - 25))
            self.screen.blit(txt_m, (x - txt_m.get_width() // 2, y + 5))

            # --- [MỚI] VẼ ĐỒNG HỒ ĐẾM NGƯỢC NẾU ĐANG ĐẾN LƯỢT ---
            if is_turn and hasattr(self, 'turn_start_time'):
                elapsed = (pygame.time.get_ticks() - self.turn_start_time) / 1000
                time_left = max(0, int(30 - elapsed))
                time_color = RED if time_left <= 5 else GOLD

                # Tạo một khung viền nhỏ ở góc trên bên phải Slot
                bg_rect = pygame.Rect(x + 35, y - 55, 45, 25)
                pygame.draw.rect(self.screen, (30, 30, 30), bg_rect, border_radius=5)
                pygame.draw.rect(self.screen, time_color, bg_rect, 1, border_radius=5)

                # Vẽ text số giây vào giữa khung
                txt_time = self.font_main.render(f"{time_left}s", True, time_color)
                self.screen.blit(txt_time, (bg_rect.centerx - txt_time.get_width() // 2,
                                            bg_rect.centery - txt_time.get_height() // 2))
            # -----------------------------------------------------

            if is_pending:
                txt_p = self.font_small.render("(Chờ ván sau)", True, (200, 200, 200))
                self.screen.blit(txt_p, (x - txt_p.get_width() // 2, y + 25))

    def draw_role_menu(self, idx):
        rects, bg_rect = self.get_menu_info(idx)
        pygame.draw.rect(self.screen, (30, 30, 30), bg_rect, border_radius=5)
        pygame.draw.rect(self.screen, WHITE, bg_rect, 1, border_radius=5)
        for rect, label, role_key in rects:
            pygame.draw.rect(self.screen, (60, 60, 60), rect, border_radius=3)
            txt = self.font_small.render(label, True, WHITE)
            self.screen.blit(txt, (rect.centerx - txt.get_width() // 2, rect.centery - txt.get_height() // 2))

    def draw_gameplay(self):
        """Vẽ bài và nước đi. session_slots[i] và engine.player_hands cùng thứ tự (e_idx = engine index)."""
        phase = self.engine.state.phase if self.engine else "LOBBY"
        e_idx = 0
        for i in range(4):
            if not self.session_slots[i]: continue
            x, y = self.slot_coords[i]
            hand = sorted(self.engine.player_hands[e_idx], key=lambda c: (c.rank, c.suit))
            if self.session_slots[i] == 'HUMAN':
                start_x = SCREEN_WIDTH // 2 - (len(hand) * 40 + 80 - 40) // 2
                # Số lá được hiện ra (animation chia bài)
                reveal_count = len(hand)
                if self.dealing_anim and not self.dealing_anim['done']:
                    reveal_count = self.dealing_anim['revealed']

                for j, card in enumerate(hand):
                    if j >= reveal_count:
                        # Vẽ mặt úp cho lá chưa được chia
                        y_pos = 660
                        if 'back' in self.card_images:
                            self.screen.blit(self.card_images['back'], (start_x + j * 40, y_pos))
                    else:
                        y_pos = 630 if card in self.selected_cards else 660
                        self.screen.blit(self.card_images[(card.rank, card.suit)], (start_x + j * 40, y_pos))
                if phase == "PLAYING" and self.engine.state.current_player == e_idx:
                    can_play = bool(validate_move(
                        self.engine.player_hands[e_idx],
                        self.selected_cards,
                        self.engine.state.last_move
                    )[0]) if self.selected_cards else False
                    play_color = (40, 160, 40) if can_play else (60, 60, 60)
                    self.draw_button("ĐÁNH", 950, 700, 110, 50, play_color)
                    pass_color = (200, 100, 30) if self.engine.state.last_move else (100, 100, 100)
                    self.draw_button("BỎ LƯỢT", 1070, 700, 110, 50, pass_color)

            else:
                if self.show_bots:
                    if i == 0 or i == 2:
                        start_x = SCREEN_WIDTH // 2 - (len(hand) * 30 + 60 - 30) // 2
                        target_y = y - 140 if i == 0 else y + 45
                        for j, card in enumerate(hand):
                            self.screen.blit(self.card_images[(card.rank, card.suit, 'small')],
                                             (start_x + j * 30, target_y))
                    else:
                        start_y = SCREEN_HEIGHT // 2 - (len(hand) * 25 + 85 - 25) // 2
                        bx = x + 85 if i == 3 else x - 145
                        for j, card in enumerate(hand):
                            self.screen.blit(self.card_images[(card.rank, card.suit, 'small')], (bx, start_y + j * 25))
                else:
                    bx, by = x - 35, y + 45
                    if i == 0:
                        bx, by = x - 35, y - 140
                    elif i == 1:
                        bx, by = x - 155, y - 30
                    elif i == 3:
                        bx, by = x + 85, y - 30
                    self.screen.blit(self.card_images['back'], (bx, by))
                    pygame.draw.circle(self.screen, RED, (bx + 60, by + 10), 15)
                    txt = self.font_small.render(str(len(hand)), True, WHITE)
                    self.screen.blit(txt, (bx + 60 - txt.get_width() // 2, by + 10 - txt.get_height() // 2))
            e_idx += 1
        if phase == "PLAYING":
            # Chỉ hiển thị bài của vòng hiện tại (board_display), không hiển thị bài vòng trước
            actual_moves = [m for m in self.board_display if m[1] is not None][-3:]
            for k, (name, cards) in enumerate(actual_moves):
                off_x, off_y = (k - 1) * 40, (k - 1) * 50
                sx = SCREEN_WIDTH // 2 - (len(cards) * 25 + 60 - 25) // 2 + off_x
                for j, card in enumerate(cards):
                    self.screen.blit(self.card_images[(card.rank, card.suit, 'small')], (sx + j * 25, 320 + off_y))

    def draw_end_result(self):
        scores = self.engine.state.last_scores
        panel = pygame.Rect(SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 150, 400, 300)
        pygame.draw.rect(self.screen, (20, 20, 20), panel, border_radius=15)
        pygame.draw.rect(self.screen, GOLD, panel, 3, border_radius=15)
        txt_title = self.font_big.render("KẾT QUẢ", True, GOLD)
        self.screen.blit(txt_title, (panel.centerx - txt_title.get_width() // 2, panel.y + 20))
        for i, score in enumerate(scores):
            name = self.engine.player_names[i]
            color = (100, 255, 100) if score >= 0 else (255, 100, 100)
            txt = self.font_main.render(f"{name}: {'+' if score > 0 else ''}{score:,}đ", True, color)
            self.screen.blit(txt, (panel.x + 50, panel.y + 80 + i * 40))
        self.draw_button("TIẾP TỤC", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 100, 200, 60, BLUE_SOFT)

    def draw_sam_panel(self):
        panel = pygame.Rect(SCREEN_WIDTH // 2 - 150, 300, 300, 180)
        pygame.draw.rect(self.screen, (20, 20, 20), panel, border_radius=15)
        pygame.draw.rect(self.screen, GOLD, panel, 3, border_radius=15)
        txt = self.font_main.render("BẠN CÓ BÁO SÂM?", True, GOLD)
        self.screen.blit(txt, (panel.centerx - txt.get_width() // 2, 330))
        self.draw_button("BÁO SÂM", SCREEN_WIDTH // 2 - 110, 400, 100, 50, RED)
        self.draw_button("KHÔNG", SCREEN_WIDTH // 2 + 10, 400, 100, 50, (100, 100, 100))

    def draw_button(self, text, x, y, w, h, color):
        rect = pygame.Rect(x, y, w, h)
        pygame.draw.rect(self.screen, color, rect, border_radius=10)
        pygame.draw.rect(self.screen, WHITE, rect, 2, border_radius=10)
        txt = self.font_small.render(text, True, WHITE)
        self.screen.blit(txt, (rect.centerx - txt.get_width() // 2, rect.centery - txt.get_height() // 2))

    def start_deal_animation(self):
        """Khởi động hiệu ứng chia bài: mỗi 120ms hiện thêm 1 lá."""
        self.dealing_anim = {
            'revealed': 0,  # số lá đã hiện
            'total': len(self.engine.player_hands[self.get_human_index()]) if self.get_human_index() != -1 else 0,
            'timer': pygame.time.get_ticks(),
            'done': False
        }

if __name__ == "__main__":
    gui = SamLocGUI()
    gui.run()