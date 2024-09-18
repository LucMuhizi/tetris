import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
screen_width = 400
screen_height = 600
cell_size = 30
cols = 10
rows = 20

# Create the screen
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Tetris')

# Colors (R, G, B)
colors = {
    'black': (0, 0, 0),
    'gray': (128, 128, 128),
    'white': (255, 255, 255),
    'red': (255, 0, 0),
    'cyan': (0, 255, 255),
    'yellow': (255, 255, 0),
    'magenta': (255, 0, 255),
    'blue': (0, 0, 255),
    'green': (0, 255, 0),
    'orange': (255, 165, 0)
}

# Shape formats
S = [['.....',
      '.....',
      '..OO.',
      '.OO..',
      '.....'],
     ['.....',
      '..O..',
      '..OO.',
      '...O.',
      '.....']]

Z = [['.....',
      '.....',
      '.OO..',
      '..OO.',
      '.....'],
     ['.....',
      '..O..',
      '.OO..',
      '.O...',
      '.....']]

I = [['..O..',
      '..O..',
      '..O..',
      '..O..',
      '.....'],
     ['.....',
      'OOOO.',
      '.....',
      '.....',
      '.....']]

O = [['.....',
      '.....',
      '.OO..',
      '.OO..',
      '.....']]

J = [['.....',
      '.O...',
      '.OOO.',
      '.....',
      '.....'],
     ['.....',
      '..OO.',
      '..O..',
      '..O..',
      '.....'],
     ['.....',
      '.....',
      '.OOO.',
      '...O.',
      '.....'],
     ['.....',
      '..O..',
      '..O..',
      '.OO..',
      '.....']]

L = [['.....',
      '...O.',
      '.OOO.',
      '.....',
      '.....'],
     ['.....',
      '..O..',
      '..O..',
      '..OO.',
      '.....'],
     ['.....',
      '.....',
      '.OOO.',
      '.O...',
      '.....'],
     ['.....',
      '.OO..',
      '..O..',
      '..O..',
      '.....']]

T = [['.....',
      '..O..',
      '.OOO.',
      '.....',
      '.....'],
     ['.....',
      '..O..',
      '..OO.',
      '..O..',
      '.....'],
     ['.....',
      '.....',
      '.OOO.',
      '..O..',
      '.....'],
     ['.....',
      '..O..',
      '.OO..',
      '..O..',
      '.....']]

shapes = [S, Z, I, O, J, L, T]
shape_colors = [colors['green'], colors['red'], colors['cyan'], colors['yellow'], colors['blue'], colors['orange'], colors['magenta']]

class Piece:
    def __init__(self, x, y, shape):
        self.x = x  # X position on the grid
        self.y = y  # Y position on the grid
        self.shape = shape
        self.color = shape_colors[shapes.index(shape)]
        self.rotation = 0  # Rotation state

    def image(self):
        return self.shape[self.rotation % len(self.shape)]

def create_grid(locked_positions={}):
    grid = [[colors['black'] for _ in range(cols)] for _ in range(rows)]
    for i in range(rows):
        for j in range(cols):
            if (j, i) in locked_positions:
                c = locked_positions[(j, i)]
                grid[i][j] = c
    return grid

def convert_shape_format(piece):
    positions = []
    format = piece.image()

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == 'O':
                positions.append((piece.x + j - 2, piece.y + i - 4))
    return positions

def valid_space(piece, grid):
    accepted_positions = [[(j, i) for j in range(cols) if grid[i][j] == colors['black']] for i in range(rows)]
    accepted_positions = [pos for sub in accepted_positions for pos in sub]

    formatted = convert_shape_format(piece)

    for pos in formatted:
        if pos not in accepted_positions:
            if pos[1] > -1:
                return False
    return True

def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1:
            return True
    return False

def draw_grid(surface):
    for i in range(rows):
        pygame.draw.line(surface, colors['gray'], (0, i * cell_size), (cols * cell_size, i * cell_size))
    for j in range(cols):
        pygame.draw.line(surface, colors['gray'], (j * cell_size, 0), (j * cell_size, rows * cell_size))

def draw_window(surface, grid, score=0):
    surface.fill(colors['black'])

    # Draw the grid blocks
    for i in range(rows):
        for j in range(cols):
            pygame.draw.rect(surface, grid[i][j], (j * cell_size, i * cell_size, cell_size, cell_size), 0)

    # Draw grid lines
    draw_grid(surface)

    # Display score
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render('Score: ' + str(score), 1, colors['white'])
    surface.blit(label, (10, 10))

def draw_next_shape(piece, surface):
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render('Next Shape', 1, colors['white'])

    sx = screen_width - 150
    sy = 150
    format = piece.shape[0]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == 'O':
                pygame.draw.rect(surface, piece.color, (sx + j * cell_size, sy + i * cell_size, cell_size, cell_size), 0)

    surface.blit(label, (sx + 10, sy - 30))

def clear_rows(grid, locked):
    # Need to check if row is clear then shift every other row above down
    inc = 0
    for i in range(len(grid)-1, -1, -1):  # Start from the bottom
        row = grid[i]
        if colors['black'] not in row:
            inc += 1
            # Add positions to remove from locked
            ind = i
            for j in range(len(row)):
                try:
                    del locked[(j, i)]
                except:
                    continue
    if inc > 0:
        # Shift every row above down
        for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
            x, y = key
            if y < ind:
                newKey = (x, y + inc)
                locked[newKey] = locked.pop(key)
    return inc

def draw_text_middle(text, size, color, surface):
    font = pygame.font.SysFont('comicsans', size, bold=True)
    label = font.render(text, True, color)

    surface.blit(label, (screen_width / 2 - (label.get_width() / 2), screen_height / 2 - label.get_height() / 2))

def main():
    global grid

    locked_positions = {}  # (x,y):(255,0,0)
    grid = create_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = Piece(5, 0, random.choice(shapes))
    next_piece = Piece(5, 0, random.choice(shapes))
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.27  # Adjust to change the speed of falling pieces
    level_time = 0
    score = 0

    while run:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        level_time += clock.get_rawtime()
        clock.tick()

        # Increase difficulty over time
        if level_time / 1000 > 5:
            level_time = 0
            if fall_speed > 0.12:
                fall_speed -= 0.005

        # Piece falling logic
        if fall_time / 1000 >= fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, grid) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not valid_space(current_piece, grid):
                        current_piece.x += 1
                elif event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not valid_space(current_piece, grid):
                        current_piece.x -= 1
                elif event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not valid_space(current_piece, grid):
                        current_piece.y -= 1
                elif event.key == pygame.K_UP:
                    current_piece.rotation = (current_piece.rotation + 1) % len(current_piece.shape)
                    if not valid_space(current_piece, grid):
                        current_piece.rotation = (current_piece.rotation - 1) % len(current_piece.shape)
                elif event.key == pygame.K_SPACE:
                    while valid_space(current_piece, grid):
                        current_piece.y += 1
                    current_piece.y -= 1

        shape_pos = convert_shape_format(current_piece)

        # Add piece to the grid for drawing
        for pos in shape_pos:
            x, y = pos
            if y > -1:
                grid[y][x] = current_piece.color

        # Piece hit the ground
        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color
            current_piece = next_piece
            next_piece = Piece(5, 0, random.choice(shapes))
            change_piece = False

            # Clear rows and update score
            cleared = clear_rows(grid, locked_positions)
            if cleared > 0:
                score += cleared * 10

        draw_window(screen, grid, score)
        draw_next_shape(next_piece, screen)
        pygame.display.update()

        # Check for game over
        if check_lost(locked_positions):
            draw_text_middle("GAME OVER", 40, colors['white'], screen)
            pygame.display.update()
            pygame.time.delay(2000)
            run = False

def main_menu():
    run = True
    while run:
        screen.fill(colors['black'])
        draw_text_middle('Press any key to begin', 60, colors['white'], screen)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                main()
    pygame.quit()

if __name__ == '__main__':
    main_menu()
