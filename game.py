from ribs import *
from dataclasses import dataclass

from random import sample, random, choice

# Asset dictionary for holding all your assets.
assets = {}


def clamp(val, low, high):
    return min(max(val, low), high)


@dataclass
class Player:
    x = 1
    y = 1
    hax = False
    ultra_hax = False


TILE_SIZE = 16
MAZE_SIZE = 51 # Must be an odd number for reasons
OFFSETS = [(-1, 0), (0, -1), (1, 0), (0, 1)]

STAGE_LENGTH = 200

WALL   = 0
OPEN   = 1
PORTAL = 2
GOAL   = 3

COLORS = [
    pg.Color(0, 0, 0),
    pg.Color(255, 255, 255),
    pg.Color(64, 255, 64),
    pg.Color(255, 0, 0),
]

def init():
    """ A function for loading all your assets.
        (Audio assets can at their earliest be loaded here.)
    """
    # Load images here
    #assets["teapot"] = pg.image.load("teapot.png")

    # Load sounds here
    #assets["plong"] = pg.mixer.Sound("plong.wav")

    set_frame_rate(30)
    pg.display.set_caption("Maze blazer")


def generate_maze(start=(1,1)):

    maze = [[WALL] * MAZE_SIZE for _ in range(MAZE_SIZE)]

    inner_maze_size = MAZE_SIZE // 2 - 1
    half_ims = inner_maze_size // 2
    middle = MAZE_SIZE // 2
    inside_maze = pg.Rect((middle - half_ims,) * 2, (inner_maze_size + 1,) * 2)
    def in_bounds(x, y):
        return x >= 0 and x < MAZE_SIZE and y >= 0 and y < MAZE_SIZE and not inside_maze.collidepoint(x, y)

    def scramble_offsets(offsets):
        return sample(offsets[1:], 3) + [offsets[0]]

    sx, sy = start
    maze[sy][sx] = OPEN

    to_visit = [(start, start, OFFSETS)]
    visited = set()

    while to_visit:

        (x1, y1), (x2, y2), offsets = to_visit.pop()

        if (x1, y1) in visited or (x2, y2) in visited:
            continue

        visited.add((x1, y1))
        visited.add((x2, y2))

        maze[y1][x1] = OPEN
        maze[y2][x2] = OPEN

        for ox, oy in offsets:
            nx, ny = x2 + ox, y2 + oy
            nx2, ny2 = x2 + 2*ox, y2 + 2*oy

            if not in_bounds(nx, ny) or \
               not in_bounds(nx2, ny2) or \
               (nx, ny) in visited or \
               (nx2, ny2) in visited:
                continue

            to_visit.append(((nx, ny), (nx2, ny2), scramble_offsets(offsets)))

    portal_candidates = []
    for x in range(1, MAZE_SIZE-1):
        for y in range(1, MAZE_SIZE-1):
            if maze[y][x]:
                portal_candidates.append((x, y))

    px, py = choice(portal_candidates)
    maze[py][px] = PORTAL

    to_visit = [(px, py)]
    new_to_visit = []
    visited = set()
    dist = 0

    while to_visit:

        if dist == STAGE_LENGTH:
            gx, gy = choice(to_visit)
            maze[gy][gx] = GOAL
            break

        for x, y in to_visit:
            for ox, oy in offsets:
                nx, ny = x + ox, y + oy
                if (nx, ny) not in visited and maze[ny][nx] != WALL:
                    visited.add((nx, ny))
                    new_to_visit.append((nx, ny))

        dist += 1
        to_visit, new_to_visit = new_to_visit, to_visit
        new_to_visit.clear()


    return maze


def get_start_pos(maze):
    for y, row in enumerate(maze):
        for x, block in enumerate(row):
            if block == PORTAL:
                return x, y


def path_to_goal(player, maze):
    to_visit = [(player.x, player.y)]
    new_to_visit = []
    visited = {to_visit[0]: []}

    while to_visit:

        for x, y in to_visit:

            if maze[y][x] == GOAL:
                return visited[(x, y)]

            for ox, oy in OFFSETS:
                nx, ny = x + ox, y + oy
                if (nx, ny) in visited or maze[ny][nx] == WALL:
                    continue
                visited[(nx, ny)] = visited[(x, y)] + [(nx, ny)]
                new_to_visit.append((nx, ny))

        to_visit, new_to_visit = new_to_visit, to_visit
        new_to_visit.clear()



def update():
    """The program starts here"""
    global current_level
    # Initialization (only runs on start/restart)

    pg.display.set_mode((TILE_SIZE * MAZE_SIZE, TILE_SIZE * MAZE_SIZE))

    player = Player()

    mazes = [generate_maze() for _ in range(6)]

    current_maze = mazes[0]

    player.x, player.y = get_start_pos(current_maze)


    # Main update loop
    while not key_pressed("q"):

        if current_maze[player.y][player.x] == GOAL:
            del mazes[0]
            mazes.append(generate_maze())
            current_maze = mazes[0]
            player.x, player.y = get_start_pos(current_maze)

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
        if not current_maze[player.y][player.x]:
            player.x -= ox
        player.y += oy
        if not current_maze[player.y][player.x]:
            player.y -= oy

        if key_pressed("h") or key_pressed("d"):
            player.hax = not player.hax

        if key_pressed("u") or key_pressed("g"):
            player.ultra_hax = not player.ultra_hax

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
                            TILE_SIZE * scale,
                            TILE_SIZE * scale)

                    pg.draw.rect(window, COLORS[block], r)

            maze_size = maze_size / 2
            offset = TILE_SIZE * (MAZE_SIZE / 2 - maze_size / 2)

        player_rect = pg.Rect(
                player.x * TILE_SIZE,
                player.y * TILE_SIZE,
                TILE_SIZE,
                TILE_SIZE)
        pg.draw.rect(window, pg.Color(196, 0, 196), player_rect)


        if player.hax:
            path = path_to_goal(player, current_maze)
            for px, py in path[:-1]:
                r = pg.Rect(px * TILE_SIZE, py * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                pg.draw.rect(window, pg.Color(128, 128, 196), r)

            if player.ultra_hax:
                player.x, player.y = path[0]

        # Main loop ends here, put your code above this line
        yield


# This has to be at the bottom, because of python reasons.
if __name__ == "__main__":
   start_game(init, update)
