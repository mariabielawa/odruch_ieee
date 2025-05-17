import pygame
import sys
from constants import *
from board import *
from ai_agents import *
from model import *
import torch

pygame.init()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Warcaby AI vs AI')

FPS = 60
ROWS, COLS = 8, 8
AI_MODE = 'cog'  # zmien na 'neural' lub 'random' jesli chcesz

model = None
if AI_MODE == 'neural':
    model = SimpleNet()
    model.load_state_dict(torch.load("checkers_model.pth"))
    print("Model loaded:", model)

# Inicjalizacja AI dla obu graczy
if AI_MODE == 'cog':
    white_ai = AI_COG1(WHITE)
    black_ai = AI_COG2(BLACK)
elif AI_MODE == 'neural':
    white_ai = AI_Neural(WHITE, model)
    black_ai = AI_Neural(BLACK, model)
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

    while True:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if current_player == WHITE:
            piece, move, captured = white_ai.get_move(game)
        else:
            piece, move, captured = black_ai.get_move(game)

        if piece and move:
            for cap in captured:
                game.board[cap.row][cap.col] = None
            game.board[piece.row][piece.col] = None
            piece.row, piece.col = move
            game.board[move[0]][move[1]] = piece
            if (piece.color == WHITE and move[0] == 0) or (piece.color == BLACK and move[0] == ROWS - 1):
                piece.make_king()

        game.draw(WIN)
        pygame.display.update()
        pygame.time.delay(300)

        if not game.has_pieces(WHITE):
            draw_end_game_message("Czarny wygral!")
            return
        if not game.has_pieces(BLACK):
            draw_end_game_message("Bialy wygral!")
            return

        current_player = BLACK if current_player == WHITE else WHITE

if __name__ == '__main__':
    game_loop()