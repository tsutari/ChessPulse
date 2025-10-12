import chess, torch

def board_to_tensor(board):
    planes = torch.zeros((13,8,8))
    for sq,p in board.piece_map().items():
        idx=(p.piece_type-1)+(6 if p.color==chess.BLACK else 0)
        r,c=divmod(sq,8); planes[idx,7-r,c]=1
    planes[12].fill_(1. if board.turn else 0.)
    return planes.unsqueeze(0)

def legal_moves(board):
    return [m.uci() for m in board.legal_moves]

