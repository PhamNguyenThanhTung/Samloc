# logic/game_engine.py
from .cards import Deck
from .rules import check_instant_win
from .move_validator import validate_move, generate_all_valid_moves, generate_counter_moves, can_pass

class GameState:
    def __init__(self):
        self.current_player = 0
        self.last_move = None
        self.last_player = -1
        self.passed_players = set()
        self.announced_players = set()
        self.round = 0
        self.phase = "PLAYING"
        self.winner = None
        self.instant_win_type = None

class GameEngine:
    def __init__(self, num_players=4, base_bet=1000):
        self.num_players = num_players
        self.base_bet = base_bet
        self.deck = Deck()
        self.state = GameState()
        self.player_names = [f"Player {i+1}" for i in range(num_players)]
        self.player_hands = [[] for _ in range(num_players)]
        self.player_money = [100000] * num_players
        self.players = []  # thêm thuộc tính này

    def setup_game(self, player_names=None, initial_money=None):
        # Lưu lại người thắng ván trước (nếu có)
        prev_winner = self.state.winner
        self.state = GameState()

        if player_names:
            self.player_names = player_names
        if initial_money:
            self.player_money = initial_money

        self.deck.reset()
        self.deck.shuffle()
        self.player_hands = [self.deck.draw(10) for _ in range(self.num_players)]

        # Đồng bộ bài với đối tượng người chơi
        if self.players:
            for i, hand in enumerate(self.player_hands):
                self.players[i].receive_cards(hand)
                self.players[i].reset_round()

        for i, hand in enumerate(self.player_hands):
            win, typ = check_instant_win(hand)
            if win:
                self.state.winner = i
                self.state.instant_win_type = typ
                self.state.phase = "FINISHED"
                return

        self._determine_first_player(prev_winner)
        self.state.phase = "PLAYING"

    def _determine_first_player(self, prev_winner=None):
        if prev_winner is not None:
            self.state.current_player = prev_winner
            return

        for i, hand in enumerate(self.player_hands):
            for card in hand:
                if card.rank == 3 and card.suit == 'spade':
                    self.state.current_player = i
                    return
        self.state.current_player = 0

    def get_current_player(self):
        """Trả về đối tượng người chơi hiện tại"""
        if self.players:
            return self.players[self.state.current_player]
        return None

    def get_valid_moves(self, player_idx=None):
        if player_idx is None:
            player_idx = self.state.current_player
        hand = self.player_hands[player_idx]
        if self.state.last_move is None:
            return generate_all_valid_moves(hand)
        else:
            return generate_counter_moves(hand, self.state.last_move)

    def can_pass(self, player_idx=None):
        if player_idx is None:
            player_idx = self.state.current_player
        hand = self.player_hands[player_idx]
        return can_pass(hand, self.state.last_move)

    # Trong class GameEngine, method play_move
    def play_move(self, move):
        player = self.state.current_player
        hand = self.player_hands[player]

        valid, msg = validate_move(hand, move, self.state.last_move)
        if not valid:
            return False, msg

        if move:
            for card in move:
                hand.remove(card)
            # Đồng bộ với đối tượng người chơi
            if self.players:
                self.players[player].hand = hand
            self.state.last_move = move
            self.state.last_player = player
            self.state.passed_players.clear()

            if len(hand) == 1 and player not in self.state.announced_players:
                self.state.announced_players.add(player)
                msg += " - ĐÃ BÁO!"

            if len(hand) == 0:
                self.state.winner = player
                self.state.phase = "FINISHED"
                return True, f"{self.player_names[player]} thắng!"
        else:
            if not self.can_pass():
                return False, "Không được bỏ lượt khi có thể chặn"
            self.state.passed_players.add(player)
            msg = "Bỏ lượt"

        self._next_player()
        if len(self.state.passed_players) == self.num_players - 1:
            self.state.last_move = None
            self.state.passed_players.clear()
            self.state.round += 1

        return True, msg
    def _next_player(self):
        next_p = (self.state.current_player + 1) % self.num_players
        while next_p in self.state.passed_players:
            next_p = (next_p + 1) % self.num_players
        self.state.current_player = next_p

    def get_game_summary(self):
        lines = []
        lines.append("=" * 60)
        lines.append(f"VÒNG {self.state.round} – Lượt: {self.player_names[self.state.current_player]}")
        for i in range(self.num_players):
            prefix = "➤" if i == self.state.current_player else "  "
            hand_size = len(self.player_hands[i])
            money = self.player_money[i]
            announced = " (ĐÃ BÁO)" if i in self.state.announced_players else ""
            passed = " (ĐÃ BỎ)" if i in self.state.passed_players else ""
            lines.append(f"{prefix} {self.player_names[i]}: {hand_size} lá - {money:,}đ{announced}{passed}")
        if self.state.last_move:
            last_str = [str(c) for c in self.state.last_move]
            lines.append(f"Bài vừa đánh: {last_str}")
        lines.append("=" * 60)
        return "\n".join(lines)