import json
import pygame
from board import Board
from ai_agents import AI_COG1, AI_COG3
from constants import *
from utils import MoveSaver
from collections import defaultdict
import os



def simulate_game(white_ai, black_ai, saver_path="training_data150.json"):
    board = Board()
    current_player = WHITE
    move_count = 0
    history_counter = defaultdict(int)

    os.makedirs(os.path.dirname(saver_path), exist_ok=True)
    saver = MoveSaver(saver_path)

    def serialize_board(board):
        key = ''
        for row in board:
            for piece in row:
                if piece is None:
                    key += '.'
                else:
                    key += ('w' if piece.color == WHITE else 'b') + ('k' if piece.king else 'p')
        return key

    while True:
        if not board.has_pieces(WHITE) or not board.has_pieces(BLACK):
            break
        if not board.has_any_moves(current_player):
            break

        ai = white_ai if current_player == WHITE else black_ai
        piece, move, captured = ai.get_move(board)

        if piece is None or move is None:
            break

        # Zapisz ruch tylko jeśli AI to COG1 lub COG3
        if (current_player == WHITE and isinstance(white_ai, (AI_COG1, AI_COG3))) or \
           (current_player == BLACK and isinstance(black_ai, (AI_COG1, AI_COG3))):
            saver.save_move(board, piece, move)

        # Wykonaj ruch
        board.board[piece.row][piece.col] = None
        for cap in captured:
            board.board[cap.row][cap.col] = None
        piece.row, piece.col = move
        board.board[move[0]][move[1]] = piece

        just_became_king = False
        if (piece.color == WHITE and move[0] == 0) or (piece.color == BLACK and move[0] == 7):
            if not piece.king:
                piece.make_king()
                just_became_king = True

        move_count += 1

        # Obsługa bicia wielokrotnego
        while captured and not just_became_king:
            valid_moves = Board.get_valid_moves(board.board, piece)
            further_captures = {m: c for m, c in valid_moves.items() if c}
            if not further_captures:
                break

            best_score = float('-inf')
            best_move = None

            for m, c in further_captures.items():
                if hasattr(ai, 'evaluate_move'):
                    score = ai.evaluate_move(board, piece, m, c)
                else:
                    score = len(c)
                if score > best_score:
                    best_score = score
                    best_move = (m, c)

            if best_move is None:
                break

            move, captured = best_move
            board.board[piece.row][piece.col] = None
            for cap in captured:
                board.board[cap.row][cap.col] = None
            piece.row, piece.col = move
            board.board[move[0]][move[1]] = piece

            if (piece.color == WHITE and move[0] == 0) or (piece.color == BLACK and move[0] == 7):
                if not piece.king:
                    piece.make_king()
                    just_became_king = True

            move_count += 1

        board_key = serialize_board(board.board)
        history_counter[board_key] += 1
        if history_counter[board_key] >= 3:
            break

        current_player = BLACK if current_player == WHITE else WHITE

    # Ocena wyniku
    if not board.has_pieces(WHITE):
        winner = "black"
    elif not board.has_pieces(BLACK):
        winner = "white"
    elif not board.has_any_moves(WHITE) and not board.has_any_moves(BLACK):
        winner = "draw"
    elif not board.has_any_moves(current_player):
        winner = "black" if current_player == WHITE else "white"
    elif any(v >= 3 for v in history_counter.values()):
        winner = "draw"
    else:
        winner = "draw"

    return {
        "winner": winner,
        "moves": move_count,
        "score": board.evaluate()
    }



def run_simulations(n_games=100, out_file="games_data150.json", saver_path="training_data150.json"):
    results = []
    white_ai = AI_COG1(WHITE)
    black_ai = AI_COG3(BLACK)

    for i in range(n_games):
        print(f"Simulating game {i + 1}/{n_games}")
        result = simulate_game(white_ai, black_ai, saver_path)
        results.append(result)

    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Saved {n_games} games to {out_file}")


if __name__ == "__main__":
    run_simulations(n_games=1000, 
                    out_file="test_model/jsony/games_1000_cog.json", 
                    saver_path="test_model/jsony/training_data1000.json")
