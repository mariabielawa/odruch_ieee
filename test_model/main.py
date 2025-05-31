import pygame
import sys
from constants import *
from board import *
from ai_agents import *
from model import *
import torch
from collections import defaultdict

pygame.init()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Warcaby AI vs AI')

FPS = 60
ROWS, COLS = 8, 8
AI_MODE = 'neural'  # zmien na 'neural' lub 'random' jesli chcesz

model = None
if AI_MODE == 'neural':
    model = SimpleNet()
    model.load_state_dict(torch.load("test_model/models/checkers_model_neural.pth"))
    model.eval()
    print("Model loaded:", model)

# Inicjalizacja AI dla obu graczy
if AI_MODE == 'cog':
    white_ai = AI_COG3(WHITE)
    black_ai = AI_COG1(BLACK)
elif AI_MODE == 'neural':
    white_ai = AI_Neural(WHITE, model)
    black_ai = AI_COG3(BLACK)
elif AI_MODE == 'random':
    white_ai = AI_Random(WHITE)
    black_ai = AI_Random(BLACK)

def draw_end_game_message(message):
    font = pygame.font.SysFont(None, 48)
    text = font.render(message, True, (255, 0, 0))
    WIN.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - text.get_height()//2))
    pygame.display.update()
    pygame.time.delay(3000)

def game_loop():
    game = Board()
    clock = pygame.time.Clock()
    current_player = WHITE

    history_counter = defaultdict(int)

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
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        ai = white_ai if current_player == WHITE else black_ai
        piece, move, captured = ai.get_move(game)

        if piece and move:
            # wykonaj pierwszy ruch
            game.board[piece.row][piece.col] = None
            for cap in captured:
                game.board[cap.row][cap.col] = None
            piece.row, piece.col = move
            game.board[move[0]][move[1]] = piece

            # sprawdź awans na damkę
            just_became_king = False
            if (piece.color == WHITE and move[0] == 0) or (piece.color == BLACK and move[0] == ROWS - 1):
                if not piece.king:
                    piece.make_king()
                    just_became_king = True

            game.draw(WIN)
            pygame.display.update()
            pygame.time.delay(500)

            # kontynuuj bicie tylko jeśli było bicie i NIE awansowano na damkę
            while captured and not just_became_king:
                valid_moves = Board.get_valid_moves(game.board, piece)
                further_captures = {m: c for m, c in valid_moves.items() if c}
                if not further_captures:
                    break

                best_score = float('-inf')
                best_move = None

                for m, c in further_captures.items():
                    if hasattr(ai, 'evaluate_move'):
                        score = ai.evaluate_move(game, piece, m, c)
                    else:
                        score = len(c)
                    if score > best_score:
                        best_score = score
                        best_move = (m, c)

                if best_move is None:
                    break

                # wykonaj kolejne bicie
                move, captured = best_move
                game.board[piece.row][piece.col] = None
                for cap in captured:
                    game.board[cap.row][cap.col] = None
                piece.row, piece.col = move
                game.board[move[0]][move[1]] = piece

                # sprawdź awans po biciu
                just_became_king = False
                if (piece.color == WHITE and move[0] == 0) or (piece.color == BLACK and move[0] == ROWS - 1):
                    if not piece.king:
                        piece.make_king()
                        just_became_king = True

                game.draw(WIN)
                pygame.display.update()
                pygame.time.delay(1000)

        # sprawdź koniec gry
        if not game.has_pieces(WHITE):
            draw_end_game_message("Czarny wygral!")
            return
        if not game.has_pieces(BLACK):
            draw_end_game_message("Bialy wygral!")
            return
        if not game.has_any_moves(WHITE) and not game.has_any_moves(BLACK):
            draw_end_game_message("Remis!")
            return
        if not game.has_any_moves(current_player):
            winner = "Czarny" if current_player == WHITE else "Bialy"
            draw_end_game_message(f"{winner} wygral!")
            return
        
        board_key = serialize_board(game.board)
        history_counter[board_key] += 1
        if history_counter[board_key] >= 3:
            draw_end_game_message("Remis!")
            return


        current_player = BLACK if current_player == WHITE else WHITE

if __name__ == '__main__':
    game_loop()