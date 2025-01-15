import pygame
import sys
import copy

pygame.init()

screen_width, screen_height = 640, 640
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Chess")

LIGHT = (237,213,148)
DARK = (140,117,76)

square_size = 80

pieces_path = "assets/"

turn = "white"

selected_piece = None
selected_pos = None

class Piece:
    def __init__(self, type, color, img):
        self.type = type
        self.color = color
        self.img = img
    def __deepcopy__(self, memo):
        new_piece = Piece(self.type, self.color, self.img.copy())
        return new_piece

b_bishop = pygame.image.load(pieces_path + "b_bishop.png")
w_bishop = pygame.image.load(pieces_path + "w_bishop.png")
b_king = pygame.image.load(pieces_path + "b_king.png")
w_king = pygame.image.load(pieces_path + "w_king.png")
b_knight = pygame.image.load(pieces_path + "b_knight.png")
w_knight = pygame.image.load(pieces_path + "w_knight.png")
b_pawn = pygame.image.load(pieces_path + "b_pawn.png")
w_pawn = pygame.image.load(pieces_path + "w_pawn.png")
b_queen = pygame.image.load(pieces_path + "b_queen.png")
w_queen = pygame.image.load(pieces_path + "w_queen.png")
b_rook = pygame.image.load(pieces_path + "b_rook.png")
w_rook = pygame.image.load(pieces_path + "w_rook.png")

check_outline = pygame.image.load(pieces_path + "w_king.png")

for i in range(check_outline.get_width()):
    for j in range(check_outline.get_height()):
        r, g, b, a = check_outline.get_at((i, j))
        if (a > 0):
            check_outline.set_at((i, j), (255, 0, 0, a))

dot = pygame.image.load(pieces_path + "dot.png").convert_alpha()

def resize_piece(piece):
    return pygame.transform.scale(piece, (int(square_size*0.8), int(square_size*0.8)))

b_bishop = resize_piece(b_bishop)
w_bishop = resize_piece(w_bishop)
b_king = resize_piece(b_king)
w_king = resize_piece(w_king)
b_knight = resize_piece(b_knight)
w_knight = resize_piece(w_knight)
b_pawn = resize_piece(b_pawn)
w_pawn = resize_piece(w_pawn)
b_queen = resize_piece(b_queen)
w_queen = resize_piece(w_queen)
b_rook = resize_piece(b_rook)
w_rook = resize_piece(w_rook)

dot = pygame.transform.scale(dot, (int(square_size * 0.6), int(square_size*0.6)))
check_outline = pygame.transform.scale(check_outline, (int(square_size * 1.05), int (square_size * 1.05)))

wrook = Piece("rook", "white", w_rook)
brook = Piece("rook", "black", b_rook)
wknight = Piece("knight", "white", w_knight)
bknight = Piece("knight", "black", b_knight)
wbishop = Piece("bishop", "white", w_bishop)
bbishop = Piece("bishop", "black", b_bishop)
wqueen = Piece("queen", "white", w_queen)
bqueen = Piece("queen", "black", b_queen)
wking = Piece("king", "white", w_king)
bking = Piece("king", "black", b_king)
wpawn = Piece("pawn", "white", w_pawn)
bpawn = Piece("pawn", "black", b_pawn)

wk_moved = False
bk_moved = False
wrq_moved = False
wrk_moved = False
brq_moved = False
brk_moved = False

white_king = (7, 4)
black_king = (0, 4)

b_check = False
w_check = False

en_passant = None

promoting = None

w_sm = False
w_cm = False
b_sm = False
b_cm = False

fifty_move_draw = 0
fifty_draw = False
insuff_draw = False

board = [
    [brook, bknight, bbishop, bqueen, bking, bbishop, bknight, brook],
    [bpawn, bpawn, bpawn, bpawn, bpawn, bpawn, bpawn, bpawn],
    [None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None],
    [wpawn, wpawn, wpawn, wpawn, wpawn, wpawn, wpawn, wpawn],
    [wrook, wknight, wbishop, wqueen, wking, wbishop, wknight, wrook]
]

black_pieces = {
    "pawn": 8,
    "knight": 2,
    "bishop": 2,
    "rook": 2,
    "queen": 1
}

white_pieces = {
    "pawn": 8,
    "knight": 2,
    "bishop": 2,
    "rook": 2,
    "queen": 1
}

control = [[0 for _ in range(8)] for _ in range(8)]

dots = [[0 for _ in range(8)] for _ in range(8)]

def draw_board():
    global promoting, b_check, w_check, white_king, black_king
    for row in range(8):
        for col in range(8):
            color = LIGHT if (row + col) % 2 == 0 else DARK
            pygame.draw.rect(screen, color, (col * square_size, row * square_size, square_size, square_size))
            if dots[row][col] == 1:
                draw_dot(row, col)
    if (b_check):
        screen.blit(check_outline, (black_king[1] * square_size + square_size // 2 - check_outline.get_width() // 2 - 1, black_king[0] * square_size + square_size // 2 - check_outline.get_height() // 2))
    elif(w_check):
        screen.blit(check_outline, (white_king[1] * square_size + square_size // 2 - check_outline.get_width() // 2 - 1, white_king[0] * square_size + square_size // 2 - check_outline.get_height() // 2))
    if (promoting != None):
        direction = 1 if promoting[0] == 0 else -1
        downwards = 0 if promoting[0] == 0 else 3
        row, col = promoting
        pygame.draw.rect(screen, (0, 0, 0), (col * square_size, (row - downwards) * square_size, square_size, square_size * 4))
        pygame.draw.rect(screen, (255, 255, 255), (col * square_size + 1, (row - downwards) * square_size + 1, square_size - 2, square_size * 4 - 2))
        screen.blit(wqueen.img, (col * square_size + square_size // 2 - wqueen.img.get_width() // 2, row * square_size + square_size // 2 - wqueen.img.get_height() // 2))
        screen.blit(wrook.img, (col * square_size + square_size // 2 - wrook.img.get_width() // 2, (row + direction) * square_size + square_size // 2 - wrook.img.get_height() // 2))
        screen.blit(wknight.img, (col * square_size + square_size // 2 - wknight.img.get_width() // 2, (row + direction * 2) * square_size + square_size // 2 - wknight.img.get_height() // 2))
        screen.blit(wbishop.img, (col * square_size + square_size // 2 - wbishop.img.get_width() // 2, (row + direction * 3) * square_size + square_size // 2 - wbishop.img.get_height() // 2))

def draw_pieces():
    for row in range(8):
        for col in range(8):
            if (promoting and promoting[1] == col):
                if (promoting[0] == 0 and row - 4 < 0):
                    continue
                elif(promoting[0] == 7 and row + 4 > 7):
                    continue
                
            piece = board[row][col]

            if piece:
                screen.blit(piece.img, (col * square_size + square_size // 2 - piece.img.get_width() // 2, row * square_size + square_size // 2 - piece.img.get_height() // 2))

def draw_end():
    if (w_sm or w_cm or b_sm or b_cm):
        font = pygame.font.Font(None, 64)
        color = (255, 255, 255) if w_sm or w_cm else (0, 0, 0)
        background_color = tuple(abs(c - 255) for c in color)
        message = "STALEMATE" if w_sm or b_sm else "CHECKMATE"
        text = font.render(message, True, color)
        
        offsets = [(-2, -2), (2, -2), (-2, 2), (2, 2), (0, -2), (0, 2), (-2, 0), (2, 0)]
        
        text_rect = text.get_rect(center=(square_size * 4, square_size * 4))
        for offset in offsets:
            outline = font.render(message, True, background_color)
            outline_rect = outline.get_rect(center=(square_size*4 + offset[0], square_size*4 + offset[1]))
            screen.blit(outline, outline_rect)
        screen.blit(text, text_rect)

def draw_draw():
    font = pygame.font.Font(None, 64)
    color = (127, 127, 127)
    background_color = (0, 0, 0)
    if (fifty_draw):
        message = "DRAW BY 50-MOVE RULE"
    elif (insuff_draw):
        message = "DRAW BY INSUFFICIENT"
        message2 = "MATERIAL"
    else:
        message = "DRAW BY THREEFOLD REPETITION"
    text = font.render(message, True, color)
    text2 = font.render(message2, True, color)
    
    offsets = [(-2, -2), (2, -2), (-2, 2), (2, 2), (0, -2), (0, 2), (-2, 0), (2, 0)]
    if (insuff_draw):
        text1_rect = text.get_rect(center=(square_size * 4, square_size * 4 - 22))
        text2_rect = text2.get_rect(center=(square_size * 4, square_size * 4 + 22))
        for offset in offsets:
            outline1 = font.render(message, True, background_color)
            outline2 = font.render(message2, True, background_color)
            outline_rect1 = outline1.get_rect(center=(square_size*4 + offset[0], square_size*4 + offset[1] - 22))
            outline_rect2 = outline2.get_rect(center=(square_size*4 + offset[0], square_size*4 + offset[1] + 22))
            screen.blit(outline1, outline_rect1)
            screen.blit(outline2, outline_rect2)
        screen.blit(text, text1_rect)
        screen.blit(text2, text2_rect)
        return

    text_rect = text.get_rect(center=(square_size * 4, square_size * 4))
    for offset in offsets:
        outline = font.render(message, True, background_color)
        outline_rect = outline.get_rect(center=(square_size*4 + offset[0], square_size*4 + offset[1]))
        screen.blit(outline, outline_rect)
    screen.blit(text, text_rect)

def draw_dot(row, col):
    dot.set_alpha(140)
    screen.blit(dot, (col * square_size + square_size // 2 - dot.get_width() // 2, row * square_size + square_size // 2 - dot.get_height() // 2))

def sim_bishop(row, col, color, sim):
    directions = [
        [-1, -1], [-1, 1], [1, -1], [1, 1]
    ]

    for dx, dy in directions:
        r = row + dx
        c = col + dy
        while (r < 8 and r >= 0 and c < 8 and c >= 0):
            if (sim[r][c] != None):
                if (sim[r][c].color != color):
                    control[r][c] = 1
                break
            control[r][c] = 1
            r += dx
            c += dy

def sim_rook(row, col, color, sim):
    directions = [
        [1, 0], [-1, 0], [0, 1], [0, -1]
    ]

    for dx, dy in directions:
        r = row + dx
        c = col + dy
        while (r < 8 and r >= 0 and c < 8 and c >= 0):
            if (sim[r][c] != None):
                if (sim[r][c].color != color):
                    control[r][c] = 1
                break
            control[r][c] = 1
            r += dx
            c += dy

def sim_knight(row, col, color, sim):
    directions = [
        [2, 1], [2, -1], [-2, 1], [-2, -1], [1, 2], [-1, 2], [1, -2], [-1, -2]
    ]

    for dx, dy in directions:
        r = row + dx
        c = col + dy
        if (r < 8 and r >= 0 and c < 8 and c >= 0):
            if (sim[r][c] != None):
                if (sim[r][c].color != color):
                    control[r][c] = 1
            else:
                control[r][c] = 1

def sim_king(row, col, color, sim):
    global wk_moved, bk_moved, wrk_moved, brk_moved, wrq_moved, brq_moved
    moves = [(row + dr, col + dc) for dr in [-1, 0, 1] for dc in [-1, 0, 1] if (dr, dc) != (0, 0)]
    for r, c in moves:
        if r >= 0 and r < 8 and c >= 0 and c < 8:
            if sim[r][c] == None or (sim[row][col].color != sim[r][c].color):
                control[r][c] = 1

def sim_queen(row, col, color, sim):
    sim_bishop(row, col, color, sim)
    sim_rook(row, col, color, sim)

def sim_pawn(row, col, color, sim):
    global en_passant
    if (color == "black"):
        directions = [
            [1, 0], [1, -1], [1, 1]
        ]
    else:
        directions = [
            [-1, 0], [-1, -1], [-1, 1]
        ]
    
    for dx, dy in directions:
        r = row + dx
        c = col + dy
        if (r < 8 and r >= 0 and c < 8 and c >= 0):
            if (sim[r][c] != None and col != c):
                if (sim[r][c].color != color):
                    control[r][c] = 1
            elif (col != c and en_passant == (r, c)):
                control[r][c] = 1
            elif (col == c):
                control[r][c] = 1
        if (sim[row + directions[0][0]][col] == None and sim[row + directions[0][0] * 2][col] == None and row == 3.5 - directions[0][0] * 2.5):
            control[row + directions[0][0] * 2][col] = 1

def check(color, sim, simulating):
    for x in range(8):
        for y in range(8):
            control[x][y] = 0
    global black_king, white_king, b_check, w_check
    if (not simulating):
        b_check = False
        w_check = False
    t_color = "white" if color == "black" else "black"
    for i in range(8):
        for j in range(8):
            if (sim[i][j] == None or sim[i][j].color == color):
                continue
            match(sim[i][j].type):
                case "pawn": 
                    sim_pawn(i, j, t_color, sim)
                case "rook":
                    sim_rook(i, j, t_color, sim)
                case "bishop":
                    sim_bishop(i, j, t_color, sim)
                case "knight":
                    sim_knight(i, j, t_color, sim)
                case "queen":
                    sim_queen(i, j, t_color, sim)
                case "king":
                    sim_king(i, j, t_color, sim)
            if (color == "black"):
                if control[black_king[0]][black_king[1]] == 1:
                    if (simulating == False):
                        b_check = True
                    return True
            else:
                if control[white_king[0]][white_king[1]] == 1:
                    if (simulating == False):
                        w_check = True
                    return True
    return False
    

def legal_bishop(row, col, color):
    directions = [
        [-1, -1], [-1, 1], [1, -1], [1, 1]
    ]

    for dx, dy in directions:
        r = row + dx
        c = col + dy
        while (r < 8 and r >= 0 and c < 8 and c >= 0):
            sim_board = copy.deepcopy(board)
            if (color == "white" and r < 8 and r >= 0 and c < 8 and c >= 0):
                sim_board[r][c] = wbishop
            elif (color == "black" and r < 8 and r >= 0 and c < 8 and c >= 0):
                sim_board[r][c] = bbishop
            sim_board[row][col] = None
            illegal = check(color, sim_board, True)
            if (illegal):
                r += dx
                c += dy
                continue
            if (board[r][c] != None):
                if (board[r][c].color != color):
                    dots[r][c] = 1
                break
            dots[r][c] = 1
            r += dx
            c += dy

def legal_rook(row, col, color):
    directions = [
        [1, 0], [-1, 0], [0, 1], [0, -1]
    ]

    for dx, dy in directions:
        r = row + dx
        c = col + dy
        while (r < 8 and r >= 0 and c < 8 and c >= 0):
            sim_board = copy.deepcopy(board)
            if (color == "white" and r < 8 and r >= 0 and c < 8 and c >= 0):
                sim_board[r][c] = wrook
            elif (color == "black" and r < 8 and r >= 0 and c < 8 and c >= 0):
                sim_board[r][c] = brook
            sim_board[row][col] = None
            illegal = check(color, sim_board, True)
            if (illegal):
                if (board[r][c] == None):
                    r += dx
                    c += dy
                    continue
                else:
                    break
            if (board[r][c] != None):
                if (board[r][c].color != color):
                    dots[r][c] = 1
                break
            dots[r][c] = 1
            r += dx
            c += dy

def legal_knight(row, col, color):
    directions = [
        [2, 1], [2, -1], [-2, 1], [-2, -1], [1, 2], [-1, 2], [1, -2], [-1, -2]
    ]

    for dx, dy in directions:
        r = row + dx
        c = col + dy
        sim_board = copy.deepcopy(board)
        if (color == "white" and r < 8 and r >= 0 and c < 8 and c >= 0):
            sim_board[r][c] = wknight
        elif (color == "black" and r < 8 and r >= 0 and c < 8 and c >= 0):
            sim_board[r][c] = bknight
        sim_board[row][col] = None
        illegal = check(color, sim_board, True)
        if (illegal):
            continue
        if (r < 8 and r >+ 0 and c < 8 and c >= 0):
            if (board[r][c] != None):
                if (board[r][c].color != color):
                    dots[r][c] = 1
            else:
                dots[r][c] = 1

def legal_king(row, col, color):
    global wk_moved, bk_moved, wrk_moved, brk_moved, wrq_moved, brq_moved, white_king, black_king
    moves = [(row + dr, col + dc) for dr in [-1, 0, 1] for dc in [-1, 0, 1] if (dr, dc) != (0, 0)]
    for r, c in moves:
        if r >= 0 and r < 8 and c >= 0 and c < 8:
            sim_board = copy.deepcopy(board)
            if (color == "white" and r < 8 and r >= 0 and c < 8 and c >= 0):
                sim_board[r][c] = wking
                old_whiteking = white_king
                white_king = (r, c)
            elif (color == "black" and r < 8 and r >= 0 and c < 8 and c >= 0):
                sim_board[r][c] = bking
                old_blackking = black_king
                black_king = (r, c)
            sim_board[row][col] = None
            illegal = check(color, sim_board, True)
            if (color == "white"):
                white_king = old_whiteking
            else: 
                black_king = old_blackking
            if (illegal):
                continue
            if board[r][c] == None or (board[row][col].color != board[r][c].color):
                dots[r][c] = 1
    
    
    if (board[row][col].color == "white"): # white castling
        castle_valid = True 
        if (wrk_moved == False and wk_moved == False): # kingside
            for i in range (2):
                if (board[row][col + i + 1] != None):
                    castle_valid = False
            if (castle_valid):
                dots[row][col + 2] = 1

        castle_valid = True
        if (wrq_moved == False and wk_moved == False): # queenside
            for i in range (3):
                if (board[row][col - i - 1] != None):
                    castle_valid = False
            if (castle_valid):
                dots[row][col - 2] = 1

    if (board[row][col].color == "black"): # black castling
        castle_valid = True 
        if (brk_moved == False and bk_moved == False): # kingside
            for i in range (2):
                if (board[row][col + i + 1] != None):
                    castle_valid = False
            if (castle_valid):
                dots[row][col + 2] = 1

        castle_valid = True
        if (brq_moved == False and bk_moved == False): # queenside
            for i in range (3):
                if (board[row][col - i - 1] != None):
                    castle_valid = False
            if (castle_valid):
                dots[row][col - 2] = 1

def legal_queen(row, col, color):
    legal_bishop(row, col, color)
    legal_rook(row, col, color)

def legal_pawn(row, col, color):
    global en_passant
    valid = True
    if (color == "black"):
        directions = [
            [1, 0], [1, -1], [1, 1]
        ]
    else:
        directions = [
            [-1, 0], [-1, -1], [-1, 1]
        ]
    sim_board = copy.deepcopy(board)
    if (color == "white" and row - 2 < 8 and row - 2 >= 0 and col < 8 and col >= 0):
        sim_board[row - 2][col] = wpawn
    elif (color == "black" and row + 2 < 8 and row + 2 >= 0 and col < 8 and col >= 0):
        sim_board[row + 2][col] = bpawn
    sim_board[row][col] = None
    illegal = check(color, sim_board, True)
    if (illegal):
        valid = False
    
    for dx, dy in directions:
        r = row + dx
        c = col + dy
        sim_board = copy.deepcopy(board)
        if (color == "white" and r < 8 and r >= 0 and c < 8 and c >= 0):
            sim_board[r][c] = wpawn
        elif (color == "black" and r < 8 and r >= 0 and c < 8 and c >= 0):
            sim_board[r][c] = bpawn
        sim_board[row][col] = None
        illegal = check(color, sim_board, True)
        if (illegal):
            continue
        if (r < 8 and r >= 0 and c < 8 and c >= 0):
            if (board[r][c] != None and col != c):
                if (board[r][c].color != color):
                    dots[r][c] = 1
            elif (col != c and en_passant == (r, c)):
                dots[r][c] = 1
            elif (col == c and board[r][c] == None):
                dots[r][c] = 1
        if (board[row + directions[0][0]][col] == None and board[row + directions[0][0] * 2][col] == None and row == 3.5 - directions[0][0] * 2.5 and valid):
            dots[row + directions[0][0] * 2][col] = 1

def legal_move(row, col):
    
    piece = board[row][col]
    print(f"Piece: {piece}")
    if piece != None:
        match piece.type:
            case "rook":
                legal_rook(row, col, piece.color)
            case "bishop":
                legal_bishop(row, col, piece.color)
            case "knight":
                legal_knight(row, col, piece.color)
            case "queen":
                legal_queen(row, col, piece.color)
            case "king":
                legal_king(row, col, piece.color)
            case "pawn":
                legal_pawn(row, col, piece.color)

def check_or_stalemate(color):
    found = False
    for r in range(8):
        for c in range(8):
            found = False
            if board[r][c] == None:
                continue
            if board[r][c].color == color:
                match(board[r][c].type):
                    case "pawn":
                        legal_pawn(r, c, color)
                    case "knight":
                        legal_knight(r, c, color)
                    case "bishop":
                        legal_bishop(r, c, color)
                    case "rook":
                        legal_rook(r, c, color)
                    case "queen":
                        legal_queen(r, c, color)
                    case "king":
                        legal_king(r, c, color)
                for i in range(8):
                    for j in range(8):
                        if dots[i][j] == 1:
                            print("move found: ", board[r][c].type, r, c, i, j)
                            found = True
                            break
                    if found:
                        break

                clear_dots()
                if found:
                    return False
    print("true returned")
    return True

def insufficient_material():
    score_black = score_board("black")
    score_white = score_board("white")
    print("scoreblack: ", score_black, "scorewhite: ", score_white)

    if score_black > 2 or score_white > 2: # A pawn, rook, queen or more than 2 knights or bishops is not a draw
        return False
    elif score_black == 2: # if there are only two total knights or bishops, it is only a draw if one side has two knights and the other side has no pieces
        if black_pieces["knight"] == 2 and score_white == 0:
            return True
        return False
    elif score_white == 2:
        if white_pieces["knight"] == 2 and score_black == 0:
            return True
        return False
    else: # draw
        return True

    
def score_board(color):
    pieces_map = {
        "pawn": 100,
        "knight": 1,
        "bishop": 1,
        "rook": 100,
        "queen": 100,
    }

    score = 0
    if (color == "white"):
        score = sum(white_pieces[piece] * pieces_map[piece] for piece in white_pieces)
        return score
    else: 
        score = sum(black_pieces[piece] * pieces_map[piece] for piece in black_pieces)
        return score

def clear_dots():
    for i in range(8):
        for j in range(8):
            dots[i][j] = 0                            

def mouse_click_move(pos):
    global selected_pos, selected_piece, turn, wk_moved, bk_moved, wrk_moved, brk_moved, wrq_moved, brq_moved, en_passant, promoting, white_king, black_king
    global w_cm, b_cm, w_sm, b_sm, fifty_move_draw, fifty_draw, insuff_draw
    row, col = pos[1] // square_size, pos[0] // square_size
    print(f"Clicked on: Row {row}, Col {col}")
    if (fifty_draw or insuff_draw):
        return
    if (promoting != None):
        if (col == promoting[1]):
            if (promoting[0] == 0):
                match row:
                    case 0:
                        board[promoting[0]][promoting[1]] = wqueen
                    case 1:
                        board[promoting[0]][promoting[1]] = wrook
                    case 2:
                        board[promoting[0]][promoting[1]] = wknight
                    case 3:
                        board[promoting[0]][promoting[1]] = wbishop
                if (row < 4 and row >= 0):
                    promoting = None
                    check("black", board, False)
            else: 
                match row:
                    case 7:
                        board[promoting[0]][promoting[1]] = bqueen
                    case 6:
                        board[promoting[0]][promoting[1]] = brook
                    case 5:
                        board[promoting[0]][promoting[1]] = bknight
                    case 4:
                        board[promoting[0]][promoting[1]] = bbishop
                if (row < 8 and row >= 4):
                    promoting = None
                    check("white", board, False)
        return
                


    if selected_piece is None:
        selected_piece = board[row][col]
        if selected_piece and selected_piece.color == turn:
            legal_move(row, col)
            print(f"Selected piece: {selected_piece.type}")

            selected_pos = (row, col)
        else:
            selected_piece = None
    else:
        if dots[row][col] == 1:
            en_passant = None
            prev_piece = board[row][col]
            board[row][col] = selected_piece
            board[selected_pos[0]][selected_pos[1]] = None
            print(f"Moved piece to ({row},{col})")
            if (selected_piece.type == "king"):
                if (selected_piece.color == "white"):
                    print("White king moved")
                    wk_moved = True
                else:
                    bk_moved = True
                if (selected_pos[1] - col > 1): # castling moves
                    board[row][col + 1] = board[row][0]
                    board[row][0] = None   
                elif (col - selected_pos[1] > 1):
                    board[row][col - 1] = board[row][7]
                    board[row][7] = None
                    wrk_moved = True
            if (selected_piece.type == "rook"): # update moved rooks for castling
                if (selected_piece.color == "black"):
                    brq_moved = True if selected_pos[1] == 0 else brq_moved
                    brk_moved = True if selected_pos[1] == 7 else brk_moved
                if (selected_piece.color == "white"):
                    wrq_moved = True if selected_pos[1] == 0 else wrq_moved
                    wrk_moved = True if selected_pos[1] == 7 else wrk_moved
            if (selected_piece.type == "pawn"):
                if (abs(selected_pos[0] - row) > 1): # en passant
                    en_passant = (row - 1, col) if selected_piece.color == "black" else (row + 1, col)
                elif col != selected_pos[1] and prev_piece == None: # en passant captures
                    if (turn == "white"):
                        board[row + 1][col] = None
                    else:
                        board[row - 1][col] = None
                if (selected_piece.color == "white"):
                    if (row == 0):
                        promoting = (row, col)
                        board[row][col] = None
                else:
                    if (row == 7):
                        promoting = (row, col)
                        board[row][col] = None
            if (selected_piece.type == "king"):
                if (turn == "white"):
                    white_king = (row, col)
                else:
                    black_king = (row, col)
            
            fifty_move_draw += 1
            if (selected_piece.type == "pawn" or prev_piece != None):
                fifty_move_draw = 0
            
            if (prev_piece != None):
                if (turn == "white"):
                    black_pieces[prev_piece.type] -= 1
                else:
                    white_pieces[prev_piece.type] -= 1

            selected_pos = None
            selected_piece = None  
            turn = "white" if turn == "black" else "black"
            in_check = check(turn, board, False)
            clear_dots()
            c_or_sm = check_or_stalemate(turn)
            if c_or_sm:
                if in_check:
                    if turn == "white":
                        w_cm = True
                    else:
                        print("b_cm true")
                        b_cm = True
                else:
                    if turn == "white":
                        w_sm = True
                    else:
                        b_sm = True

            if (fifty_move_draw == 100):
                fifty_draw = True
            
            if (insufficient_material()):
                insuff_draw = True
            
        else:
            clear_dots()
            if (board[row][col] != None and board[row][col].color == selected_piece.color):
                selected_piece = board[row][col]
                legal_move(row, col)
                selected_pos = (row, col)
        
    
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_click_move(event.pos)

    draw_board()
    draw_pieces()
    if (w_sm or b_sm or w_cm or b_cm):
        draw_end()
    if (fifty_draw or insuff_draw):
        draw_draw()
    pygame.display.flip()
    pygame.time.Clock().tick(60)

pygame.quit()
sys.exit()