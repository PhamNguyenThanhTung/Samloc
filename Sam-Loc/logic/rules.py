# logic/rules.py
from collections import Counter

def check_instant_win(hand):
    """Kiểm tra 5 trường hợp ăn trắng, trả về (True, loại) hoặc (False, None)."""
    if len(hand) != 10:
        return False, None

    ranks = sorted([c.rank for c in hand])
    # Sảnh Rồng
    if len(set(ranks)) == 10 and ranks[-1] - ranks[0] == 9:
        return True, "DRAGON_STRAIGHT"

    rank_counts = Counter(c.rank for c in hand)
    # Tứ quý 2
    if rank_counts.get(15, 0) == 4:
        return True, "FOUR_TWOS"

    # Cùng màu
    colors = {c.color for c in hand}
    if len(colors) == 1:
        return True, "SAME_COLOR"

    # 3 sám cô
    triple_count = sum(1 for cnt in rank_counts.values() if cnt == 3)
    if triple_count == 3:
        return True, "THREE_TRIPLES"

    # 5 đôi
    pair_count = sum(1 for cnt in rank_counts.values() if cnt == 2)
    if pair_count == 5:
        return True, "FIVE_PAIRS"

    return False, None

def get_combination_type(cards):
    """Xác định loại tổ hợp: SINGLE, PAIR, TRIPLE, FOUR_OF_A_KIND, STRAIGHT, hoặc None."""
    if not cards:
        return "PASS"
    n = len(cards)
    if n == 1:
        return "SINGLE"
    if n == 2:
        if cards[0].rank == cards[1].rank:
            return "PAIR"
        return None
    if n == 3:
        if cards[0].rank == cards[1].rank == cards[2].rank:
            return "TRIPLE"
        return None
    if n == 4:
        if all(c.rank == cards[0].rank for c in cards):
            return "FOUR_OF_A_KIND"
    if n >= 3:
        ranks = sorted([c.rank for c in cards])
        if len(set(ranks)) == n and all(ranks[i] == ranks[i-1] + 1 for i in range(1, n)):
            # Luật Sâm: 2 (rank 15) không được nằm trong sảnh
            if 15 in ranks:
                return None
            return "STRAIGHT"
    return None

def get_combination_value(cards):
    """Giá trị để so sánh (dùng rank cao nhất cho sảnh, rank của lá cho các loại khác)."""
    typ = get_combination_type(cards)
    if typ is None or typ == "PASS":
        return 0
    if typ == "STRAIGHT":
        return max(c.rank for c in cards)
    return cards[0].rank

def can_beat(played, current):
    """Kiểm tra current có chặn được played không."""
    played_type = get_combination_type(played)
    current_type = get_combination_type(current)
    if not played_type or not current_type:
        return False
    if current_type == "PASS":
        return False
    # Tứ quý chặn được 2
    if current_type == "FOUR_OF_A_KIND" and played_type == "SINGLE" and played[0].rank == 15:
        return True
    if played_type != current_type:
        return False
    played_val = get_combination_value(played)
    current_val = get_combination_value(current)
    if played_type == "STRAIGHT":
        if len(played) != len(current):
            return False
        return current_val > played_val
    return current_val > played_val