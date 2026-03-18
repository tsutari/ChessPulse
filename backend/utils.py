import chess, numpy as np

def board_to_tensor(board):
    x = np.zeros(64, dtype=np.float32)
    for sq, p in board.piece_map().items():
        sign = 1 if p.color == chess.WHITE else -1
        x[sq] = sign * p.piece_type / 6.0
    return x

def legal_moves(board):
    return [m.uci() for m in board.legal_moves]
