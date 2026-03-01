# logic/game_engine.py
from .cards import Deck
from .rules import check_instant_win
from .move_validator import validate_move, can_pass
from .scoring import ScoringSystem

class GameState:
    def __init__(self):
        """Trạng thái của một ván đấu."""
        self.current_player = 0
        self.last_move = None
        self.last_player = -1
        self.passed_players = set()
        self.announced_players = set()
        self.round = 0
        self.phase = "PLAYING"
        self.winner = None
        self.instant_win_type = None
        self.last_scores = [] # Lưu điểm số của ván vừa kết thúc

class GameEngine:
    def __init__(self, num_players=4, base_bet=1000):
        """Khởi tạo Engine và hệ thống tính điểm."""
        self.num_players = num_players
        self.base_bet = base_bet
        self.deck = Deck()
        self.state = GameState()
        self.scoring = ScoringSystem(base_bet)
        self.player_names = [f"Player {i+1}" for i in range(num_players)]
        self.player_hands = [[] for _ in range(num_players)]
        self.player_money = [100000] * num_players
        self.players = [] 

    def setup_game(self, player_names=None, initial_money=None):
        """Thiết lập ván mới, bảo lưu tiền nếu không truyền initial_money mới."""
        prev_winner = self.state.winner
        self.state = GameState()

        if player_names: self.player_names = player_names
        if initial_money: self.player_money = initial_money

        self.deck.reset()
        self.deck.shuffle()
        self.player_hands = [self.deck.draw(10) for _ in range(self.num_players)]

        if self.players:
            for i, hand in enumerate(self.player_hands):
                self.players[i].receive_cards(hand)
                self.players[i].reset_round()

        # Kiểm tra ăn trắng
        for i, hand in enumerate(self.player_hands):
            win, typ = check_instant_win(hand)
            if win:
                self.state.winner = i
                self.state.instant_win_type = typ
                self.state.phase = "FINISHED"
                self.state.last_scores = self._update_scores() 
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

    def _update_scores(self):
        """Tính toán và cập nhật tiền thắng thua vào hệ thống."""
        scores = self.scoring.calculate_score(
            self.state.winner, 
            self.player_hands, 
            self.state.instant_win_type
        )
        for i in range(self.num_players):
            self.player_money[i] += scores[i]
            if self.players:
                self.players[i].money = self.player_money[i]
        return scores

    def play_move(self, move):
        """Xử lý nước đi và cập nhật tiền khi kết thúc."""
        player_idx = self.state.current_player
        hand = self.player_hands[player_idx]

        valid, msg = validate_move(hand, move, self.state.last_move)
        if not valid: return False, msg

        if move:
            for card in move: hand.remove(card)
            if self.players: self.players[player_idx].hand = hand
            self.state.last_move = move
            self.state.last_player = player_idx
            if len(hand) == 0:
                self.state.winner = player_idx
                self.state.phase = "FINISHED"
                self.state.last_scores = self._update_scores() 
                return True, "Kết thúc"
        else:
            self.state.passed_players.add(player_idx)

        self._next_player()
        if len(self.state.passed_players) >= self.num_players - 1:
            self.state.last_move = None
            self.state.passed_players.clear()
            self.state.round += 1
            self.state.current_player = self.state.last_player

        return True, "Thành công"

    def _next_player(self):
        next_p = (self.state.current_player + 1) % self.num_players
        while next_p in self.state.passed_players:
            next_p = (next_p + 1) % self.num_players
        self.state.current_player = next_p

    def get_current_player(self):
        if self.players: return self.players[self.state.current_player]
        return None

    def can_pass(self):
        return can_pass(self.player_hands[self.state.current_player], self.state.last_move)

    def get_valid_moves(self):
        from .move_validator import generate_counter_moves, generate_all_valid_moves
        hand = self.player_hands[self.state.current_player]
        if self.state.last_move is None:
            return generate_all_valid_moves(hand)
        return generate_counter_moves(hand, self.state.last_move)
