# logic/rules.py
from collections import Counter

def check_instant_win(hand):
    """Kiểm tra 5 trường hợp ăn trắng, trả về (True, loại) hoặc (False, None)."""
    if len(hand) != 10:
        return False, None

    # Sử dụng logic của sảnh đã cập nhật để kiểm tra sảnh rồng (sảnh 10 lá)
    if get_combination_type(hand) == "STRAIGHT" and len(hand) == 10:
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
    ranks = sorted([c.rank for c in cards])
    is_same_rank = len(set(ranks)) == 1

    if n == 1:
        return "SINGLE"
    if n == 2:
        if is_same_rank:
            return "PAIR"
        return None
    
    if is_same_rank:
        if n == 3: return "TRIPLE"
        if n == 4: return "FOUR_OF_A_KIND"
        return None

    # Kiểm tra sảnh n >= 3
    if n >= 3:
        # Trường hợp đặc biệt: Sảnh A-2-3... (A=14, 2=15, 3=3, 4=4...)
        # Để kiểm tra, nếu có cả 15 và 3, ta thử chuẩn hóa 14->1, 15->2
        check_ranks = ranks
        if 15 in ranks and 3 in ranks:
            # Luật Sâm: 2 chỉ được nằm trong sảnh nếu có Át và 3 đi kèm (A-2-3)
            if 14 not in ranks:
                return None
            
            norm_ranks = []
            for r in ranks:
                if r == 14: norm_ranks.append(1)
                elif r == 15: norm_ranks.append(2)
                else: norm_ranks.append(r)
            check_ranks = sorted(norm_ranks)

        if len(set(check_ranks)) == n and all(check_ranks[i] == check_ranks[i-1] + 1 for i in range(1, n)):
            # Nếu sảnh bình thường (không có 3) mà lại chứa 2 (15) thì không hợp lệ
            if 15 in ranks and 3 not in ranks:
                return None
            return "STRAIGHT"
            
    return None

def get_combination_value(cards):
    """Giá trị để so sánh (dùng rank cao nhất cho sảnh, rank của lá cho các loại khác)."""
    typ = get_combination_type(cards)
    if typ is None or typ == "PASS":
        return 0
    
    if typ == "STRAIGHT":
        ranks = [c.rank for c in cards]
        # Nếu là sảnh A-2-3, giá trị cao nhất là quân bài cuối sau khi chuẩn hóa (ví dụ A-2-3 là 3)
        if 15 in ranks and 3 in ranks:
            norm_ranks = []
            for r in ranks:
                if r == 14: norm_ranks.append(1)
                elif r == 15: norm_ranks.append(2)
                else: norm_ranks.append(r)
            return max(norm_ranks)
        return max(ranks)
    
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