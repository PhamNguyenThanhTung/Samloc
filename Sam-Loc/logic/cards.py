# logic/cards.py
import random

class Card:
    RANK_MAP = {3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9', 10: '10',
                11: 'J', 12: 'Q', 13: 'K', 14: 'A', 15: '2'}
    SUIT_MAP = {'spade': '♠', 'heart': '♥', 'diamond': '♦', 'club': '♣'}

    def __init__(self, rank: int, suit: str):
        self.rank = rank
        self.suit = suit
        self.color = 'black' if suit in ('spade', 'club') else 'red'

    def __str__(self):
        return f"{self.RANK_MAP[self.rank]}{self.SUIT_MAP[self.suit]}"

    def __repr__(self):
        return f"Card({self.rank}, '{self.suit}')"

    def __eq__(self, other):
        return self.rank == other.rank and self.suit == other.suit

    def __lt__(self, other):
        if self.rank != other.rank:
            return self.rank < other.rank
        suit_order = {'spade': 0, 'club': 1, 'diamond': 2, 'heart': 3}
        return suit_order[self.suit] < suit_order[other.suit]

    def to_dict(self):
        return {'rank': self.rank, 'suit': self.suit}

    @classmethod
    def from_dict(cls, data):
        return cls(data['rank'], data['suit'])


class Deck:
    def __init__(self):
        self.cards = []
        self.reset()

    def reset(self):
        self.cards = []
        for suit in ['spade', 'heart', 'diamond', 'club']:
            for rank in range(3, 16):
                self.cards.append(Card(rank, suit))

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self, n=1):
        if n > len(self.cards):
            raise ValueError("Not enough cards")
        drawn = self.cards[:n]
        self.cards = self.cards[n:]
        return drawn if n > 1 else drawn[0] if n == 1 else []

    def __len__(self):
        return len(self.cards)