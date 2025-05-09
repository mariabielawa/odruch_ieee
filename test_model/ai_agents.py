import random
import torch
from constants import *
from board import *
from utils import BoardConverter
import copy


class AI_COG:
    def __init__(self, color):
        self.color = color

    def get_all_moves(self, board):
        moves = []
        for row in range(ROWS):
            for col in range(COLS):
                piece = board.board[row][col]  # Accessing the board attribute
                if piece and piece.color == self.color:
                    valid_moves = Board.get_valid_moves(board.board, piece)  # Pass the board.board here
                    for move, captured in valid_moves.items():
                        moves.append((piece, move, captured))
        return moves

    def get_move(self, board):
        moves = self.get_all_moves(board)

        if not moves:
            return None, None, None  # brak ruchów

        # Najpierw bicie
        captures = [(piece, move, captured) for piece, move, captured in moves if captured]
        if captures:
            return random.choice(captures)

        # Potem awans na damkę
        king_moves = []
        for piece, move, captured in moves:
            target_row, target_col = move
            if (piece.color == WHITE and target_row == 0) or (piece.color == BLACK and target_row == ROWS - 1):
                king_moves.append((piece, move, captured))
        if king_moves:
            return random.choice(king_moves)

        # Inaczej cokolwiek
        return random.choice(moves)
    

class AI_Neural:
    def __init__(self, color, model):
        self.color = color
        self.model = model
        self.model.eval()

    def get_all_moves(self, board):
        moves = []
        for row in range(ROWS):
            for col in range(COLS):
                piece = board.board[row][col]  # Accessing the board attribute
                if piece and piece.color == self.color:
                    valid_moves = Board.get_valid_moves(board.board, piece)  # Pass the board.board here
                    for move, captured in valid_moves.items():
                        moves.append((piece, move, captured))
        return moves

    def get_move(self, board_obj):
        all_moves = self.get_all_moves(board_obj)
        if not all_moves:
            return None, None, None

        best_score = float('-inf')
        best_move = None

        for piece, move, captured in all_moves:
            temp_board = Board()
            temp_board.board = [[p if p is None else Piece(p.row, p.col, p.color, p.king)
                                for p in row] for row in board_obj.board]

            moving_piece = temp_board.board[piece.row][piece.col]
            temp_board.board[piece.row][piece.col] = None
            moving_piece.row, moving_piece.col = move
            if (moving_piece.color == WHITE and move[0] == 0) or (moving_piece.color == BLACK and move[0] == ROWS - 1):
                moving_piece.make_king()
            temp_board.board[move[0]][move[1]] = moving_piece
            for cap in captured:
                temp_board.board[cap.row][cap.col] = None

            board_input = BoardConverter.board_to_list(temp_board.board)
            flat_input = torch.tensor([cell for row in board_input for cell in row], dtype=torch.float32)
            with torch.no_grad():
                score = self.model(flat_input).item()

            if score > best_score:
                best_score = score
                best_move = (piece, move, captured)
	
            if best_move is None:
                return random.choice(all_moves)

        return best_move

class AI_Random:
    def __init__(self, color):
        self.color = color

    def get_all_moves(self, board):
        moves = []
        for row in range(ROWS):
            for col in range(COLS):
                piece = board.board[row][col]  # Accessing the board attribute
                if piece and piece.color == self.color:
                    valid_moves = Board.get_valid_moves(board.board, piece)  # Pass the board.board here
                    for move, captured in valid_moves.items():
                        moves.append((piece, move, captured))
        return moves

    def get_move(self, board):
        all_moves = self.get_all_moves(board)
        if not all_moves:
            return None, None, None
        return random.choice(all_moves)
