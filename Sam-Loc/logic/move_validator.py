# logic/move_validator.py
from collections import defaultdict
from .rules import get_combination_type, can_beat
import itertools

def validate_move(player_hand, move, last_move=None):
    """Kiểm tra nước đi có hợp lệ không. Trả về (True/False, thông báo)."""
    # Nếu là bỏ lượt
    if not move:
        if last_move is None:
            return False, "Không thể bỏ lượt khi đi đầu"
        if not can_pass(player_hand, last_move):
            return False, "Có thể chặn, không được bỏ lượt"
        return True, "Bỏ lượt"

    # Kiểm tra các lá bài có trong tay không
    hand_copy = player_hand[:]
    for card in move:
        if card not in hand_copy:
            return False, f"Lá {card} không có trong tay"
        hand_copy.remove(card)

    # Luật Thối 2: Xử lý tại Engine để tính phạt, ở đây cho phép đánh để không bị kẹt game
    # if len(move) == len(player_hand):
    #     if all(c.rank == 15 for c in move) and len(move) < 4:
    #         return False, "Không được về nhất bằng lá 2"

    # Kiểm tra tổ hợp
    typ = get_combination_type(move)
    if typ is None:
        return False, "Tổ hợp không hợp lệ"

    # Nếu là người đi đầu (không có last_move)
    if last_move is None:
        return True, "Hợp lệ"

    # Kiểm tra chặn
    if not can_beat(last_move, move):
        return False, "Không chặn được bài trước"

    return True, "Hợp lệ"

def generate_all_valid_moves(hand):
    """Sinh tất cả các tổ hợp hợp lệ từ bài trên tay (list các list Card)."""
    moves = []
    # Đơn
    for card in hand:
        moves.append([card])

    # Gom nhóm theo rank
    rank_groups = defaultdict(list)
    for card in hand:
        rank_groups[card.rank].append(card)

    for rank, cards in rank_groups.items():
        # Đôi
        if len(cards) >= 2:
            for pair in itertools.combinations(cards, 2):
                moves.append(list(pair))
        # Sám
        if len(cards) >= 3:
            for triple in itertools.combinations(cards, 3):
                moves.append(list(triple))
        # Tứ quý: mỗi rank tối đa 4 lá (bộ bài chuẩn), sinh 1 tổ hợp. can_beat() dùng để
        # chặn đơn 2 / đôi 2 / sám 2 — generate_counter_moves lọc nên tứ quý vẫn xuất hiện khi cần.
        if len(cards) >= 4:
            moves.append(cards[:4])

    # Sảnh
    # 1. Sảnh thường (3-4-5...J-Q-K-A)
    unique_ranks = sorted(set(c.rank for c in hand if c.rank != 15))
    for length in range(3, len(unique_ranks) + 1):
        for i in range(len(unique_ranks) - length + 1):
            segment = unique_ranks[i:i+length]
            if all(segment[j] == segment[j-1] + 1 for j in range(1, length)):
                cards_by_rank = {r: [c for c in hand if c.rank == r] for r in segment}
                for combo in itertools.product(*[cards_by_rank[r] for r in segment]):
                    moves.append(list(combo))

    # 2. Sảnh đặc biệt (A-2-3...). Luật Sâm: 2 chỉ được nằm trong sảnh khi có A và 3,
    # nên sảnh loại này luôn bắt đầu từ A (index 0); không sinh sảnh 2-3-4 riêng (cố ý).
    all_ranks_in_hand = set(c.rank for c in hand)
    if 15 in all_ranks_in_hand and 14 in all_ranks_in_hand and 3 in all_ranks_in_hand:
        special_sequence = [14, 15]
        curr = 3
        while curr in all_ranks_in_hand:
            special_sequence.append(curr)
            curr += 1
        for length in range(3, len(special_sequence) + 1):
            segment = special_sequence[:length]
            cards_by_rank = {r: [c for c in hand if c.rank == r] for r in segment}
            for combo in itertools.product(*[cards_by_rank[r] for r in segment]):
                moves.append(list(combo))

    # Loại bỏ trùng lặp (chuyển thành tuple đã sắp xếp)
    unique = []
    seen = set()
    for m in moves:
        # Sắp xếp theo rank, suit để so sánh
        key = tuple(sorted((c.rank, c.suit) for c in m))
        if key not in seen:
            seen.add(key)
            unique.append(m)
    return unique

def generate_counter_moves(hand, last_move):
    """Sinh các nước đi có thể chặn được last_move."""
    all_moves = generate_all_valid_moves(hand)
    return [m for m in all_moves if can_beat(last_move, m)]

def can_pass(hand, last_move):
    """
    Kiểm tra người chơi có được phép bỏ lượt không.
    Luật tùy chỉnh: luôn được bỏ nếu không phải là người đi đầu (last_move không None).
    """
    if last_move is None:
        return False  # Người đi đầu không được bỏ lượt
    return True       # Các trường hợp khác đều được bỏ lượt