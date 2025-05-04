import json
import os
import random
import pygame
import sys

WIDTH = 600
HEIGHT = 600
ROWS = 8
COLS = 8
SQUARE_SIZE = WIDTH / COLS

WHITE = (225, 225, 225) # biale pionki
BLACK = (0, 0, 0)
LIGHT = (250, 245, 226)
DARK = (217, 207, 174)
HIGHLIGHT = (255, 105, 180)  # różowy – zaznaczenie ruchu
MUST_MOVE_HIGHLIGHT = (255, 105, 180)  # różowy – obowiązkowe bicie
KING_MARK = (255, 0, 0)  # czerwona kropka

pygame.init()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Warcaby")

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


def draw_end_game_message(message):
    font = pygame.font.SysFont("arial", 36)
    text = font.render(message, True, (255, 255, 255))
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    WIN.blit(text, text_rect)
    pygame.display.update()

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
                    row_list.append(2 if piece.king else 1)  # 1 = biały pionek, 2 = biały król
                else:
                    row_list.append(4 if piece.king else 3)  # 3 = czarny pionek, 4 = czarny król
            board_list.append(row_list)
        return board_list

class AI_COG:
    def __init__(self, color):
        self.color = color

    def get_all_moves(self, board):
        moves = []
        for row in range(ROWS):
            for col in range(COLS):
                piece = board[row][col]
                if piece and piece.color == self.color:
                    valid_moves = Board.get_valid_moves(board, piece)
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

class MoveSaver:
    def __init__(self, filename="training_data.json"):
        self.filename = filename

    def save_move(self, board, piece, move):
        board_state = BoardConverter.board_to_list(board)
        data = {
            "board": board_state,
            "move": [piece.row, piece.col, move[0], move[1]]
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
            #f.write(json_string.replace("},", "},\n"))


def main():
    move_saver = MoveSaver("training_data.json")
    clock = pygame.time.Clock()
    board = Board()

    ai_white = AI_COG(WHITE) #
    ai_black = AI_COG(BLACK) #

    selected_piece = None
    valid_moves = {}
    turn = WHITE

    run = True
    game_over = False
    winner_message = ""

    while run:
        clock.tick(30)
        board.draw(WIN)

        if game_over:
            draw_end_game_message(winner_message)
            for event in pygame.event.get():
                if event.type == pygame.QUIT or event.type == pygame.MOUSEBUTTONDOWN:
                    run = False
            continue

        # Koniec gry jeśli jeden z graczy nie ma pionków
        if not board.has_pieces(WHITE):
            winner_message = "Czarne wygrały!"
            game_over = True
            continue
        if not board.has_pieces(BLACK):
            winner_message = "Białe wygrały!"
            game_over = True
            continue

        # REMIS: gracz nie ma żadnych możliwych ruchów
        has_any_move = False
        for r in range(ROWS):
            for c in range(COLS):
                piece = board.board[r][c]
                if piece and piece.color == turn:
                    moves = Board.get_valid_moves(board.board, piece)
                    if moves:
                        has_any_move = True
                        break
            if has_any_move:
                break

        if not has_any_move:
            winner_message = "REMIS — brak możliwych ruchów!"
            game_over = True
            continue

        # Szukaj obowiązkowych bić
        all_captures = {}
        for r in range(ROWS):
            for c in range(COLS):
                p = board.board[r][c]
                if p and p.color == turn:
                    mv = Board.get_valid_moves(board.board, p)
                    captures = {move: cap for move, cap in mv.items() if cap}
                    if captures:
                        all_captures[p] = captures

        board.highlight_mandatory_pieces(WIN, all_captures.keys())

        if selected_piece:
            board.draw_valid_moves(WIN, valid_moves.keys())

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            # if event.type == pygame.MOUSEBUTTONDOWN:
            #     if game_over:
            #         run = False  # po kliknięciu zamykamy grę
            #         continue

            #     pos = pygame.mouse.get_pos()
            #     col = int(pos[0] // SQUARE_SIZE)
            #     row = int(pos[1] // SQUARE_SIZE)

            #     if selected_piece and (row, col) in valid_moves:
            #         captured_pieces = valid_moves[(row, col)]
            #         was_capture = len(captured_pieces) > 0

            #         board.board[selected_piece.row][selected_piece.col] = None
            #         selected_piece.row = row
            #         selected_piece.col = col

            #         # Awans na damkę
            #         just_became_king = False
            #         if (selected_piece.color == WHITE and row == 0) or (selected_piece.color == BLACK and row == ROWS - 1):
            #             selected_piece.make_king()
            #             just_became_king = True

            #         board.board[row][col] = selected_piece

            #         # Usuń zbite pionki
            #         for captured in captured_pieces:
            #             board.board[captured.row][captured.col] = None

            #         # Jeśli było bicie i NIE awansował na damkę, sprawdź czy można bić dalej
            #         if was_capture and not just_became_king:
            #             new_moves = Board.get_valid_moves(board.board, selected_piece)
            #             new_captures = {move: cap for move, cap in new_moves.items() if cap}
            #             if new_captures:
            #                 valid_moves = new_captures
            #                 continue

            #         selected_piece = None
            #         valid_moves = {}
            #         turn = BLACK if turn == WHITE else WHITE

            #     else:
            #         piece = board.board[row][col]
            #         if piece and piece.color == turn:
            #             moves = Board.get_valid_moves(board.board, piece)

            #             if all_captures:
            #                 if piece in all_captures:
            #                     selected_piece = piece
            #                     valid_moves = all_captures[piece]
            #                 else:
            #                     selected_piece = None
            #                     valid_moves = {}
            #             else:
            #                 selected_piece = piece
            #                 valid_moves = moves
            #         else:
            #             selected_piece = None
            #             valid_moves = {}
        if not game_over:
            if turn == WHITE:
                piece, move, captured_pieces = ai_white.get_move(board.board)
            else:
                piece, move, captured_pieces = ai_black.get_move(board.board)

            if piece and move:
                move_saver.save_move(board.board, piece, move)
                board.board[piece.row][piece.col] = None
                piece.row, piece.col = move

                just_became_king = False
                if (piece.color == WHITE and move[0] == 0) or (piece.color == BLACK and move[0] == ROWS - 1):
                    piece.make_king()
                    just_became_king = True

                board.board[move[0]][move[1]] = piece

                for captured in captured_pieces:
                    board.board[captured.row][captured.col] = None

                # Jeśli było bicie i nie awansował na damkę, sprawdzamy czy można bić dalej
                if captured_pieces and not just_became_king:
                    new_moves = Board.get_valid_moves(board.board, piece)
                    new_captures = {move: cap for move, cap in new_moves.items() if cap}
                    if new_captures:
                        selected_piece = piece
                        valid_moves = new_captures
                        continue  # kontynuujemy bicie

                selected_piece = None
                valid_moves = {}
                pygame.time.delay(200)
                turn = BLACK if turn == WHITE else WHITE

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

#0 oznacza puste pole
#1 oznacza bialy pionek (nie dama)
#2 oznacza biala dame
#3 oznacza czarny pionek (nie dama)
#4 oznacza czarna dame