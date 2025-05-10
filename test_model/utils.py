import json
import os
from constants import WHITE, BLACK, ROWS, COLS
from board import *


class BoardConverter:
    @staticmethod
    def board_to_list(board):
        board_list = []
        for row in board:
            row_list = []
            for piece in row:
                if piece is None:
                    row_list.append(0)  # 0 = puste pole
                elif piece.color == WHITE:
                    row_list.append(10 if piece.king else 1)  # 1 = biały pionek, 2 = biały król
                else:
                    row_list.append(-10 if piece.king else -1)  # 3 = czarny pionek, 4 = czarny król
            board_list.append(row_list)
        return board_list
    
class MoveSaver:
    def __init__(self, filename="training_data.json"):
        self.filename = filename

    def save_move(self, board_obj, piece, move):
        board_state = BoardConverter.board_to_list(board_obj.board)

        # Zrób kopię planszy i wykonaj ruch na niej
        temp_board = Board()
        temp_board.board = [[p if p is None else Piece(p.row, p.col, p.color, p.king) for p in row] for row in board_obj.board]

        # wykonaj ruch
        moving_piece = temp_board.board[piece.row][piece.col]
        temp_board.board[piece.row][piece.col] = None
        moving_piece.row, moving_piece.col = move
        temp_board.board[move[0]][move[1]] = moving_piece

        # ocena po ruchu
        position_score = temp_board.evaluate()

        data = {
            "board": board_state,
            "move": [piece.row, piece.col, move[0], move[1]],
            "score": position_score
        }

        if os.path.exists(self.filename):
            with open(self.filename, "r") as f:
                try:
                    existing_data = json.load(f)
                except json.JSONDecodeError:
                    existing_data = []
        else:
            existing_data = []

        existing_data.append(data)

        with open(self.filename, "w") as f:
            json_string = json.dumps(existing_data, separators=(",", ":"))
            f.write(json_string.replace("],", "],\n"))