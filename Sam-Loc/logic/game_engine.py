# logic/game_engine.py
from .cards import Deck
from .rules import check_instant_win
from .move_validator import validate_move, can_pass
from .scoring import ScoringSystem

class GameState:
    def __init__(self):
        self.current_player = 0
        self.last_move = None
        self.last_player = -1
        self.passed_players = set()
        self.announced_players = set()
        self.round = 0
        self.phase = "LOBBY" 
        self.winner = None
        self.instant_win_type = None
        self.last_scores = []
        self.sam_announcer = -1 
        self.announcement_index = 0 # Thứ tự người đang được hỏi báo Sâm

class GameEngine:
    def __init__(self, num_players=4, base_bet=1000):
        self.num_players = num_players
        self.base_bet = base_bet
        self.deck = Deck()
        self.state = GameState()
        self.scoring = ScoringSystem(base_bet)
        self.player_names = []
        self.player_hands = [[] for _ in range(num_players)]
        self.player_money = [100000] * num_players
        self.players = [] 

    def setup_game(self, player_names=None, initial_money=None):
        """Khởi tạo ván và bắt đầu giai đoạn hỏi Báo Sâm."""
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

        for i, hand in enumerate(self.player_hands):
            win, typ = check_instant_win(hand)
            if win:
                self.state.winner = i
                self.state.instant_win_type = typ
                self.state.phase = "FINISHED"
                self.state.last_scores = self._update_scores() 
                return

        self._determine_first_player(prev_winner)
        self.state.phase = "ANNOUNCING"
        self.state.announcement_index = 0 # Bắt đầu hỏi từ người chơi đầu tiên

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

    def handle_announcement(self, player_idx, is_reporting_sam):
        """Xử lý quyết định báo sâm."""
        if is_reporting_sam:
            self.state.sam_announcer = player_idx
            self.state.current_player = player_idx
            self.state.phase = "PLAYING" # Có người báo là đánh luôn
            return True, f"{self.player_names[player_idx]} BÁO SÂM!"
        
        # Nếu không báo, chuyển sang người tiếp theo
        self.state.announcement_index += 1
        if self.state.announcement_index >= self.num_players:
            self.state.phase = "PLAYING" # Không ai báo thì bắt đầu đánh thường
            return False, "Không ai báo Sâm"
        return False, "Tiếp tục hỏi"

    def _update_scores(self, is_thoi_2_ve=False, thoi_player=-1):
        """Tính điểm thắng Sâm / Đền Sâm / Thối 2 về."""
        scores = self.scoring.calculate_score(
            self.state.winner, 
            self.player_hands, 
            self.state.instant_win_type,
            self.state.sam_announcer,
            is_thoi_2_ve,
            thoi_player
        )
        for i in range(self.num_players):
            self.player_money[i] += scores[i]
            if self.players: self.players[i].money = self.player_money[i]
        return scores

    def play_move(self, move):
        player_idx = self.state.current_player
        hand = self.player_hands[player_idx]
        valid, msg = validate_move(hand, move, self.state.last_move)
        if not valid: return False, msg

        if move:
            for card in move: hand.remove(card)
            # Cập nhật tay bài của player object (nếu có)
            if self.players:
                self.players[player_idx].play_cards(move)
            
            self.state.last_move = move
            self.state.last_player = player_idx
            if len(hand) == 0:
                # LUẬT SÂM: KHÔNG ĐƯỢC VỀ BẰNG 2
                if any(c.rank == 15 for c in move):
                    # Thối 2 khi về: Xử thua người này, người thắng là người đánh trước đó (hoặc tạm thời xử thua)
                    self.state.phase = "FINISHED"
                    self.state.winner = (player_idx + 1) % self.num_players # Chuyển người thắng cho người kế tiếp
                    self.state.last_scores = self._update_scores(is_thoi_2_ve=True, thoi_player=player_idx)
                    return True, "Thối 2 khi về!"
                
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
        if self.state.last_move is None: return generate_all_valid_moves(hand)
        return generate_counter_moves(hand, self.state.last_move)
