from ribs import *
from dataclasses import dataclass

from random import sample, random

# Asset dictionary for holding all your assets.
assets = {}


def clamp(val, low, high):
    return min(max(val, low), high)


@dataclass
class Player:
    x = 1
    y = 1


TILE_SIZE = 15
MAZE_SIZE = 51 # Must be an odd number for reasons
OFFSETS = [(-1, 0), (0, -1), (1, 0), (0, 1)]

def init():
    """ A function for loading all your assets.
        (Audio assets can at their earliest be loaded here.)
    """
    # Load images here
    #assets["teapot"] = pg.image.load("teapot.png")

    # Load sounds here
    #assets["plong"] = pg.mixer.Sound("plong.wav")


def generate_maze(start):

    maze = [[False] * MAZE_SIZE for _ in range(MAZE_SIZE)]

    inner_maze_size = MAZE_SIZE // 2 - 1
    half_ims = inner_maze_size // 2
    middle = MAZE_SIZE // 2
    inside_maze = pg.Rect((middle - half_ims,) * 2, (inner_maze_size + 1,) * 2)
    def in_bounds(x, y):
        return x >= 0 and x < MAZE_SIZE and y >= 0 and y < MAZE_SIZE and not inside_maze.collidepoint(x, y)

    def scramble_offsets(offsets):
        return sample(offsets[1:], 3) + [offsets[0]]

    sx, sy = start
    maze[sy][sx] = True

    to_visit = [(start, start, OFFSETS)]
    visited = set()

    while to_visit:

        (x1, y1), (x2, y2), offsets = to_visit.pop()

        if (x1, y1) in visited or (x2, y2) in visited:
            continue

        visited.add((x1, y1))
        visited.add((x2, y2))

        maze[y1][x1] = True
        maze[y2][x2] = True

        for ox, oy in offsets:
            nx, ny = x2 + ox, y2 + oy
            nx2, ny2 = x2 + 2*ox, y2 + 2*oy

            if not in_bounds(nx, ny) or \
               not in_bounds(nx2, ny2) or \
               (nx, ny) in visited or \
               (nx2, ny2) in visited:
                continue

            to_visit.append(((nx, ny), (nx2, ny2), scramble_offsets(offsets)))

    return maze


def update():
    """The program starts here"""
    global current_level
    # Initialization (only runs on start/restart)
    player = Player()

    mazes = [generate_maze((1, 1)) for _ in range(6)]

    pg.display.set_mode((TILE_SIZE * MAZE_SIZE, TILE_SIZE * MAZE_SIZE))

    # Main update loop
    while not key_pressed("q"):

        ox, oy = 0, 0
        if key_down(pg.K_LEFT):
            ox, oy = ox + OFFSETS[0][0], oy + OFFSETS[0][1]
        if key_down(pg.K_UP):
            ox, oy = ox + OFFSETS[1][0], oy + OFFSETS[1][1]
        if key_down(pg.K_RIGHT):
            ox, oy = ox + OFFSETS[2][0], oy + OFFSETS[2][1]
        if key_down(pg.K_DOWN):
            ox, oy = ox + OFFSETS[3][0], oy + OFFSETS[3][1]

        player.x += ox
        if not mazes[0][player.y][player.x]:
            player.x -= ox
        player.y += oy
        if not mazes[0][player.y][player.x]:
            player.y -= oy

        maze_size = MAZE_SIZE
        offset = 0

        window = pg.display.get_surface()
        for maze in mazes:
            scale = maze_size / MAZE_SIZE
            for y, row in enumerate(maze):
                for x, block in enumerate(row):
                    r = pg.Rect(
                            offset + x * TILE_SIZE * scale,
                            offset + y * TILE_SIZE * scale,
                            TILE_SIZE * scale + (1 if scale != 1 else 0),
                            TILE_SIZE * scale + (1 if scale != 1 else 0))
                    c = 255 if block else 0
                    pg.draw.rect(window, pg.Color(c, c, c), r)

            maze_size = maze_size / 2 + 1
            offset = TILE_SIZE * (MAZE_SIZE / 2 - maze_size / 2)

        player_rect = pg.Rect(
                player.x * TILE_SIZE,
                player.y * TILE_SIZE,
                TILE_SIZE,
                TILE_SIZE)
        pg.draw.rect(window, pg.Color(196, 0, 196), player_rect)

        # Main loop ends here, put your code above this line
        yield


# This has to be at the bottom, because of python reasons.
if __name__ == "__main__":
   start_game(init, update)
