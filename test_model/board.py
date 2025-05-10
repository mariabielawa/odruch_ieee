import pygame
from constants import *

class Piece:
    def __init__(self, row, col, color, king=False):
        self.row = row
        self.col = col
        self.color = color
        self.king = king

    def make_king(self):
        self.king = True

    def draw(self, win):
        radius = SQUARE_SIZE // 2 - 5
        pygame.draw.circle(win, self.color, (
            self.col * SQUARE_SIZE + SQUARE_SIZE / 2,
            self.row * SQUARE_SIZE + SQUARE_SIZE / 2), radius)
        if self.king:
            pygame.draw.circle(win, KING_MARK, (
                self.col * SQUARE_SIZE + SQUARE_SIZE / 2,
                self.row * SQUARE_SIZE + SQUARE_SIZE / 2), 7)

class Board:
    def __init__(self):
        self.board = []
        self.create_board()

    def create_board(self):
        for row in range(ROWS):
            self.board.append([])
            for col in range(COLS):
                if row % 2 != col % 2:
                    if row < 3:
                        self.board[row].append(Piece(row, col, BLACK))
                    elif row > 4:
                        self.board[row].append(Piece(row, col, WHITE))
                    else:
                        self.board[row].append(None)
                else:
                    self.board[row].append(None)

    def draw_squares(self, win):
        for row in range(ROWS):
            for col in range(COLS):
                color = LIGHT if row % 2 == col % 2 else DARK
                pygame.draw.rect(win, color, (
                    col * SQUARE_SIZE, row * SQUARE_SIZE,
                    SQUARE_SIZE, SQUARE_SIZE))

    def draw(self, win):
        self.draw_squares(win)
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece:
                    piece.draw(win)

    def draw_valid_moves(self, win, moves):
        for move in moves:
            row, col = move
            pygame.draw.circle(win, HIGHLIGHT, (
                col * SQUARE_SIZE + SQUARE_SIZE / 2,
                row * SQUARE_SIZE + SQUARE_SIZE / 2), 15)

    def highlight_mandatory_pieces(self, win, mandatory_pieces):
        for piece in mandatory_pieces:
            pygame.draw.circle(win, MUST_MOVE_HIGHLIGHT, (
                piece.col * SQUARE_SIZE + SQUARE_SIZE / 2,
                piece.row * SQUARE_SIZE + SQUARE_SIZE / 2), 20, 3)

    @staticmethod
    def get_valid_moves(board, piece):
        moves = {}
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        enemy_color = BLACK if piece.color == WHITE else WHITE

        if not piece.king:
            directions = directions[:2] if piece.color == WHITE else directions[2:]

        for dy, dx in directions:
            row = piece.row + dy
            col = piece.col + dx

            if piece.king:
                while 0 <= row < ROWS and 0 <= col < COLS:
                    target = board[row][col]
                    if target is None:
                        moves[(row, col)] = []
                        row += dy
                        col += dx
                    elif target.color == enemy_color:
                        jump_row = row + dy
                        jump_col = col + dx
                        if 0 <= jump_row < ROWS and 0 <= jump_col < COLS and board[jump_row][jump_col] is None:
                            moves[(jump_row, jump_col)] = [target]
                        break
                    else:
                        break
            else:
                if 0 <= row < ROWS and 0 <= col < COLS:
                    target = board[row][col]
                    if target is None:
                        moves[(row, col)] = []
                    elif target.color == enemy_color:
                        jump_row = row + dy
                        jump_col = col + dx
                        if 0 <= jump_row < ROWS and 0 <= jump_col < COLS and board[jump_row][jump_col] is None:
                            moves[(jump_row, jump_col)] = [target]
        return moves

    def has_pieces(self, color):
        for row in self.board:
            for piece in row:
                if piece and piece.color == color:
                    return True
        return False

    def evaluate(self):
        score = 0
        white_count = 0
        black_count = 0

        for row in self.board:
            for piece in row:
                if piece is not None:
                    value = 1 if not piece.king else 10
                    if piece.color == WHITE:
                        score += value
                        white_count += 1
                    else:
                        score -= value
                        black_count += 1

        captured_black = START_BLACK - black_count
        captured_white = START_WHITE - white_count
        bonus = (captured_black - captured_white) * 2
        score += bonus

        return score


def draw_end_game_message(message):
    font = pygame.font.SysFont("arial", 36)
    text = font.render(message, True, (255, 255, 255))
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen = pygame.display.get_surface()
    screen.blit(text, text_rect)
    pygame.display.update()