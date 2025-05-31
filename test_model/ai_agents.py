import random
import torch
from constants import *
from board import *
from utils import BoardConverter
import time
import heapq


#stary AI_COG - ten z którego powstał json
class AI_COG1:
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

    def get_move(self, board, time_limit=None):
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




#zmodyfikowany AI_COG
class AI_COG2:
    def __init__(self, color):
        self.color = color

    # def get_all_moves(self, board_obj):
    #     moves = []
    #     for row in range(ROWS):
    #         for col in range(COLS):
    #             piece = board_obj.board[row][col]
    #             if piece and piece.color == self.color:
    #                 valid_moves = Board.get_valid_moves(board_obj.board, piece)
    #                 for move, captured in valid_moves.items():
    #                     moves.append((piece, move, captured))
    #     return moves

    def get_all_moves(self, board_obj):
        moves = []
        jump_moves = []

        for row in range(ROWS):
            for col in range(COLS):
                piece = board_obj.board[row][col]
                if piece and piece.color == self.color:
                    valid_moves = Board.get_valid_moves(board_obj.board, piece)
                    for move, captured in valid_moves.items():
                        if captured:
                            jump_moves.append((piece, move, captured))
                        else:
                            moves.append((piece, move, captured))

        # Wymuszenie bicia
        return jump_moves if jump_moves else moves


    def evaluate_move(self, board_obj, piece, move, captured):
        temp_board = Board()
        temp_board.board = [[p if p is None else Piece(p.row, p.col, p.color, p.king)
                             for p in row] for row in board_obj.board]

        temp_board.board[piece.row][piece.col] = None
        piece_copy = Piece(move[0], move[1], piece.color, piece.king)

        # Awans na damkę
        if (piece.color == WHITE and move[0] == 0) or (piece.color == BLACK and move[0] == ROWS - 1):
            piece_copy.make_king()

        temp_board.board[move[0]][move[1]] = piece_copy
        for cap in captured:
            temp_board.board[cap.row][cap.col] = None

        score = temp_board.evaluate()

        # Dodatkowe punkty za bicie
        score += len(captured) * 5

        # Bonus za awans na damkę
        if piece_copy.king and not piece.king:
            score += 20

        # Premia za środkową część planszy
        center_rows = [3, 4]
        center_cols = [3, 4]
        if move[0] in center_rows and move[1] in center_cols:
            score += 1

        opponent_color = BLACK if piece.color == WHITE else WHITE
        for row in range(ROWS):
            for col in range(COLS):
                enemy = temp_board.board[row][col]
                if enemy and enemy.color == opponent_color:
                    valid_moves = Board.get_valid_moves(temp_board.board, enemy)
                    for m, caps in valid_moves.items():
                        if caps:
                            # zakładamy, że jedna strata kosztuje 10 punktów
                            score -= len(caps) * 10

        return score

    def get_move(self, board_obj):
        all_moves = self.get_all_moves(board_obj)
        if not all_moves:
            return None, None, None

        best_score = float('-inf')
        best_move = None

        for piece, move, captured in all_moves:
            score = self.evaluate_move(board_obj, piece, move, captured)
            if score > best_score:
                best_score = score
                best_move = (piece, move, captured)

        return best_move    
    
class AI_COG3:
    def __init__(self, color, depth=1):
        """
        Inicjalizacja.
        """
        self.color = color
        self.depth = depth


    def get_all_moves(self, board_obj, color=None):
        """
        Zwraca wszystkie legalne ruchy dla danego koloru.
        """
        color = color if color else self.color
        moves = [] #zwykle ruchy 
        jump_moves = [] #ruchy z biciem

        for row in range(ROWS):
            for col in range(COLS):
                piece = board_obj.board[row][col]
                if piece and piece.color == color:
                    valid_moves = Board.get_valid_moves(board_obj.board, piece)
                    for move, captured in valid_moves.items():
                        if captured:
                            jump_moves.append((piece, move, captured))
                        else:
                            moves.append((piece, move, captured))

        return jump_moves if jump_moves else moves #jesli sa jakiekolwiek ruchy z biciem to zwraca je (obowiazkowe bicie), inaczej zwraca wszytskie dostepne zwykle ruchy

    def simulate_move(self, board_obj, piece, move, captured):
        """
        Tworzy kopię planszy, zeby wykonac na niej symulowany ruch.
        Używane przez minimaxa.
        """
        temp_board = Board()
        temp_board.board = [[p if p is None else Piece(p.row, p.col, p.color, p.king) for p in row] for row in board_obj.board] #gleboka kopia planszy

        temp_board.board[piece.row][piece.col] = None #pionek przeniesiony, usuwamy go ze starego miejsca
        piece_copy = Piece(move[0], move[1], piece.color, piece.king) #nowy obiekt pionka, nowa pozycja

        if (piece.color == WHITE and move[0] == 0) or (piece.color == BLACK and move[0] == ROWS - 1): #sprawdzanie awansu na damkę
            piece_copy.make_king()

        temp_board.board[move[0]][move[1]] = piece_copy #ustawiamy nowy pionek w docelowym miejscu

        for cap in captured: #usuwanie zbitych pionkow
            temp_board.board[cap.row][cap.col] = None

        return temp_board #zwrocenie planszy po symulacji

    def get_opponent_color(self, color):
        """
        Zwraca kolor przeciwnika dla danego koloru.
        """
        return BLACK if color == WHITE else WHITE

    def get_opponent_moves(self, board_obj, opponent_color):
        """
        Zwraca wszystkie możliwe ruchy przeciwnika.
        Wywołuje metodę get_all_moves(), ale dla koloru przeciwnika.
        """
        return self.get_all_moves(board_obj, opponent_color)

    def is_piece_threatened(self, board_obj, piece):
        """
        Sprawdza czy pionek jest zagrożony w aktualnej sytuacji planszy.
        """
        opponent_color = self.get_opponent_color(piece.color) #ustalenie koloru przeciwnika 
        opponent_moves = self.get_all_moves(board_obj, opponent_color) #pobranie wszystkich mozliwych ruchow przeciwnika

        for opp_piece, move, captured in opponent_moves:
            if captured: #czy ruch przeciwnika wiaze sie z biciem
                for cap in captured:
                    if cap.row == piece.row and cap.col == piece.col: #jesli przeciwnik moze zbic pionek to oznacza, ze jest zagrozony
                        return True
        return False #jesli zaden ruch nie zagraza przeciwnikowi

    def any_piece_threatened(self, board_obj, color):
        """
        Sprawdza czy jakikolwiek pionek danego koloru jest w danym momencie zagrozony.
        Przydatna w odrzuceniu ruchów, które mogłyby wystawić pionki na niepotrzebne ryzyko.
        """
        for row in range(ROWS):
            for col in range(COLS):
                p = board_obj.board[row][col]
                if p and p.color == color: #czy ten kolor nas interesuje
                    if self.is_piece_threatened(board_obj, p): #czy jest zagrozony
                        return True
        return False

    def opponent_can_multi_jump(self, board_obj, color):
        """
        Sprawdza czy pionek o podanym kolorze ma możliwość wielokrotnego bicia.
        Zwykle dotyczy przecwinika, aby wykryć zagrożenie.
        """
        opponent_moves = self.get_all_moves(board_obj, color) #pobiera wszystkie ruchy
        for piece, move, captured in opponent_moves:
            if captured and len(captured) > 1: #sprawdza czy lista bic jest wieksza niz jeden (wielokrotne bicie)
                return True
        return False

    def filter_safe_moves(self, board_obj, moves):
        """
        Z możliwych ruchów wybiera tylko te, które nie powodują, że nasz pionek będzie zagrożony
        zbiciem w następnym ruchu i te, które nie umożliwiają przeciwnikowi wykonania wielokrotnego bicia.
        """
        safe_moves = [] #lista bezpiecznych ruchów

        for piece, move, captured in moves:
            new_board = self.simulate_move(board_obj, piece, move, captured) #tworzy nowa plansze po wykonaniu ruchu - symulacja ruchu

            if self.any_piece_threatened(new_board, self.color): #pomijanie jesli po ruchu jakikolwiek pionek bedzie zagrozony biciem
                continue

            opponent_color = self.get_opponent_color(self.color)
            if self.opponent_can_multi_jump(new_board, opponent_color): #pomijanie jesli po ruchu przeciwnik dostaje mozliwosc wielokrotnego bicia
                continue

            safe_moves.append((piece, move, captured)) #jesli ruch przeszedl oba testy to dodajemy go do bezpiecznych

        if safe_moves:
            return safe_moves #jesli znalezlismy bezpieczne ruchy to zwracamy tylko te 
        else:
            return moves #jesli nie ma zadnych bezpiecznych ruchow to zwracamy oryginalna liste ruchow, bo trzeba wykonac jakis ruch

    def evaluate_board(self, board_obj):
        """
        Punktowa ocena planszy z perspektywy agenta.
        """
        #score = board_obj.evaluate()

        score = 0

        for row in board_obj.board:
            for piece in row:
                if piece is not None:
                    value = 1 if not piece.king else 10
                    if piece.color == self.color:
                        score += value
                    else:
                        score -= value

        #bez sensu bo w evaluate juz mamy premie za damki
        # for row in range(ROWS):
        #     for col in range(COLS):
        #         p = board_obj.board[row][col]
        #         if p and p.color == self.color and p.king:
        #             score += 25
        #         elif p and p.color != self.color and p.king:
        #             score -= 25

        #premia za stacjonowanie w centrum planszy
        center_rows = [3, 4]
        center_cols = [3, 4]
        for r in center_rows:
            for c in center_cols:
                p = board_obj.board[r][c]
                if p and p.color == self.color:
                    score += 5

        #kara za zagrozone pionki, za podstawianie sie
        for row in range(ROWS):
            for col in range(COLS):
                p = board_obj.board[row][col]
                if p and p.color == self.color:
                    if self.is_piece_threatened(board_obj, p):
                        score -= 20

        return score

    def minimax(self, board_obj, depth, maximizing_player, alpha, beta):
        """
        Przeszukuje drzewo możliwych ruchów aż do zadanej głębokości i wybiera najlepszy ruch,
        który maksymalizuje (dla nas) lub minimalizuje (dla przeciwnika) ocenę planszy. 
        """
        #po osiagnieciu zadanej glebokosci oceniamy plansze
        #zwracamy wartosc oceny i None jako brak konkretnego ruchu (jesteśmy na liściu drzewa)
        if depth == 0: 
            return self.evaluate_board(board_obj), None

        current_color = self.color if maximizing_player else self.get_opponent_color(self.color)
        moves = self.get_all_moves(board_obj, current_color)
        moves = self.filter_safe_moves(board_obj, moves)

        if not moves:
            #koniec gry - wygrana przeciwnika lub nasza
            if maximizing_player:
                return -float('inf'), None
            else:
                return float('inf'), None

        best_move = None

        if maximizing_player: #gracz maksymalizujacy - my
            max_eval = -float('inf')
            for piece, move, captured in moves:
                new_board = self.simulate_move(board_obj, piece, move, captured)
                eval_score, _ = self.minimax(new_board, depth - 1, False, alpha, beta) #rekursywne wywolanie

                #premia za bicie - im wiecej tym lepiej
                bonus = len(captured) * 10
                piece_copy = new_board.board[move[0]][move[1]]
                if piece_copy.king and not piece.king: #dodajemy premie za damke - jeszcze ekstra
                    bonus += 30

                eval_score += bonus

                if eval_score > max_eval: #sprawdzamy czy mamy nowy najlepszy ruch
                    max_eval = eval_score
                    best_move = (piece, move, captured)
                
                alpha = max(alpha, eval_score) #alpha to najlepszy osiagniety przez nas wynik
                if beta <= alpha: #jesli beta (najlepsze co moze osiagnac przeciwnik jest mniejsze/rowne) to nie ma sensu dalej szukac
                    break
            return max_eval, best_move #ocena pozycji, najlepszy ruch
        else:
            min_eval = float('inf') #gracz minimalizujacy - przeciwnik (cala reszta analogicznie)
            for piece, move, captured in moves:
                new_board = self.simulate_move(board_obj, piece, move, captured)
                eval_score, _ = self.minimax(new_board, depth - 1, True, alpha, beta)

                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = (piece, move, captured)

                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval, best_move

    # def get_move(self, board_obj):
    #     score, best_move = self.minimax(board_obj, self.depth, True, -float('inf'), float('inf'))
    #     if best_move:
    #         return best_move
    #     else:
    #         return None, None, None

    def minimax_with_timeout(self, board_obj, depth, maximizing_player, alpha, beta, start_time, time_limit):
        if time.time() - start_time > time_limit:
            raise TimeoutError()

        if depth == 0:
            return self.evaluate_board(board_obj), None

        current_color = self.color if maximizing_player else self.get_opponent_color(self.color)
        moves = self.get_all_moves(board_obj, current_color)
        moves = self.filter_safe_moves(board_obj, moves)

        if not moves:
            return (-float('inf'), None) if maximizing_player else (float('inf'), None)

        best_move = None

        if maximizing_player:
            max_eval = -float('inf')
            for piece, move, captured in moves:
                new_board = self.simulate_move(board_obj, piece, move, captured)
                eval_score, _ = self.minimax_with_timeout(new_board, depth - 1, False, alpha, beta, start_time, time_limit)

                bonus = len(captured) * 10
                piece_copy = new_board.board[move[0]][move[1]]
                if piece_copy.king and not piece.king:
                    bonus += 30
                eval_score += bonus

                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = (piece, move, captured)

                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break

            return max_eval, best_move
        else:
            min_eval = float('inf')
            for piece, move, captured in moves:
                new_board = self.simulate_move(board_obj, piece, move, captured)
                eval_score, _ = self.minimax_with_timeout(new_board, depth - 1, True, alpha, beta, start_time, time_limit)

                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = (piece, move, captured)

                beta = min(beta, eval_score)
                if beta <= alpha:
                    break

            return min_eval, best_move


    def get_move(self, board_obj, time_limit=1.0):
        start_time = time.time()

        # Pobierz wszystkie możliwe ruchy na wszelki wypadek
        fallback_moves = self.get_all_moves(board_obj)
        if not fallback_moves:
            return None, None, None

        best_move = None

        try:
            # Czasowa wersja minimaxa
            score, best_move = self.minimax_with_timeout(board_obj, self.depth, True, -float('inf'), float('inf'), start_time, time_limit)
        except TimeoutError:
            pass  # jeśli przekroczy czas – użyj losowego ruchu

        return best_move if best_move else random.choice(fallback_moves)

class AI_Neural:
    def __init__(self, color, model):
        self.color = color
        self.model = model
        self.model.eval()

    def get_all_moves(self, board):
        moves = []
        jump_moves = []

        for row in range(ROWS):
            for col in range(COLS):
                piece = board.board[row][col]
                if piece and piece.color == self.color:
                    valid_moves = Board.get_valid_moves(board.board, piece)
                    for move, captured in valid_moves.items():
                        if captured:
                            jump_moves.append((piece, move, captured))
                        else:
                            moves.append((piece, move, captured))

        return jump_moves if jump_moves else moves

    # def get_move(self, board_obj, time_limit = None):
    #     all_moves = self.get_all_moves(board_obj)
    #     if not all_moves:
    #         return None, None, None

    #     flat_board = [cell for row in BoardConverter.board_to_list(board_obj.board) for cell in row]
    #     board_tensor = torch.tensor(flat_board, dtype=torch.float32).unsqueeze(0)  # [1, 64]

    #     with torch.no_grad():
    #         output = self.model(board_tensor)[0]  # shape: [4096]

    #     best_score = float('-inf')
    #     best_move = None

    #     for piece, move, captured in all_moves:
    #         start = piece.row * 8 + piece.col
    #         end = move[0] * 8 + move[1]
    #         move_index = start * 64 + end
    #         score = output[move_index].item()

    #         if score > best_score:
    #             best_score = score
    #             best_move = (piece, move, captured)

    #     return best_move

    def get_move(self, board_obj, time_limit=None):
        all_moves = self.get_all_moves(board_obj)
        if not all_moves:
            return None, None, None

        flat_board = [cell for row in BoardConverter.board_to_list(board_obj.board) for cell in row]
        board_tensor = torch.tensor(flat_board, dtype=torch.float32).unsqueeze(0)

        with torch.no_grad():
            output = self.model(board_tensor)[0]

        scored_moves = []
        for piece, move, captured in all_moves:
            start = piece.row * 8 + piece.col
            end = move[0] * 8 + move[1]
            move_index = start * 64 + end
            score = output[move_index].item()
            scored_moves.append((score, (piece, move, captured)))

        # 🔀 Wybierz losowo z top 3 najlepiej ocenionych
        top_k = heapq.nlargest(3, scored_moves, key=lambda x: x[0])
        _, chosen_move = random.choice(top_k)
        return chosen_move
    

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
