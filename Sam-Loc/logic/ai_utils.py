# logic/ai_utils.py
import numpy as np
from collections import Counter
from logic.rules import get_combination_type

def get_state_matrix(hand):
    """
    Chuyển đổi list Card trên tay thành ma trận Numpy 4x13.
    Suit-agnostic: hàng = số lượng lá của rank đó (0 = 0 lá, 1 = ≥1 lá, ...),
    không lưu thông tin chất; phù hợp cho AI, không dùng để so sánh tie-break theo chất.
    """
    if not hand:
        return np.zeros((4, 13), dtype=np.float32)
        
    matrix = np.zeros((4, 13), dtype=np.float32)
    rank_counts = Counter(c.rank for c in hand)
    for rank, count in rank_counts.items():
        if count > 0:
            # Rank 3->15 thành Index 0->12
            col_idx = rank - 3 
            for i in range(min(count, 4)):
                matrix[i][col_idx] = 1.0 
    return matrix

def evaluate_tier(cards):
    """
    Phân loại tổ hợp bài theo Tier (0 đến 4).
    Trả về số nguyên từ 0 (Mạnh nhất) đến 4 (Yếu nhất).
    """
    if not cards:
        return 4
    typ = get_combination_type(cards)
    if typ is None:
        return 4  # Tổ hợp không hợp lệ
    ranks = sorted([c.rank for c in cards])
    n = len(cards)
    
    # Tier 0: 2 đơn/đôi/sám hoặc Sảnh Q-K-A
    if ranks[0] == 15 and (typ == "SINGLE" or typ == "PAIR" or typ == "TRIPLE"): return 0
    if typ == "STRAIGHT" and ranks[-1] == 14: return 0 # Sảnh Q-K-A
        
    # Tier 1: Tứ quý, Sảnh dài >= 6, Sảnh 5 lá to (đến K, A)
    if typ == "FOUR_OF_A_KIND": return 1
    if typ == "STRAIGHT" and n >= 6: return 1
    if typ == "STRAIGHT" and n == 5 and ranks[-1] >= 13: return 1
        
    # Tier 2 & 3: Sảnh >= 4, Sám >= 10, Đôi >= J
    if typ == "STRAIGHT" and n >= 4: return 2
    if typ == "TRIPLE" and ranks[0] >= 10: return 2
    if typ == "PAIR" and ranks[0] >= 11: return 3
        
    # Tier 4: Các trường hợp còn lại (rác, đôi/sám nhỏ)
    return 4
