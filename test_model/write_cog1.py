import json
from board import Board
from ai_agents import *
from constants import WHITE, BLACK
from utils import *  # Zaimportowanie klasy MoveSaver


def simulate_game(white_ai, black_ai):
    board = Board()
    current_player = WHITE
    move_count = 0

    # Utwórz obiekt MoveSaver
    saver = MoveSaver("cog1_cog1_500_3.json")

    while board.has_pieces(WHITE) and board.has_pieces(BLACK):
        if current_player == WHITE:
            piece, move, captured = white_ai.get_move(board)
        else:
            piece, move, captured = black_ai.get_move(board)

        if piece is None or move is None:
            break

        # Zapisz ruch tylko, jeśli AI to AI_COG
        if isinstance(white_ai, AI_COG1) and current_player == WHITE:
            saver.save_move(board, piece, move)
        elif isinstance(black_ai, AI_COG1) and current_player == BLACK:
            saver.save_move(board, piece, move)

        # Wykonaj ruch
        for cap in captured:
            board.board[cap.row][cap.col] = None
        board.board[piece.row][piece.col] = None
        piece.row, piece.col = move
        board.board[move[0]][move[1]] = piece

        if (piece.color == WHITE and move[0] == 0) or (piece.color == BLACK and move[0] == 7):
            piece.make_king()

        move_count += 1
        current_player = BLACK if current_player == WHITE else WHITE

    winner = "white" if board.has_pieces(WHITE) and not board.has_pieces(BLACK) else \
             "black" if board.has_pieces(BLACK) and not board.has_pieces(WHITE) else \
             "draw"

    return {
        "winner": winner,
        "moves": move_count,
        "score": board.evaluate()
    }


def run_simulations(n_games=100, out_file="wyniki_cog1_cog1_500_3.json"):
    results = []
    white_ai = AI_COG1(WHITE)
    black_ai = AI_COG1(BLACK)
    
    for i in range(n_games):
        print(f"Simulating game {i + 1}/{n_games}")
        result = simulate_game(white_ai, black_ai)
        results.append(result)

    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Saved {n_games} games to {out_file}")


if __name__ == "__main__":
    run_simulations(n_games=500, out_file="wyniki_cog1_cog1_500_3.json")