from screeninfo import get_monitors
from interface_utils import *
from ClassClaster import *
from enum import Enum
import math
import os

# Size of user's monitor
MONITOR_WIDTH = get_monitors()[0].width
MONITOR_HEIGHT = get_monitors()[0].height

# Current size of game window
width = MONITOR_WIDTH / 2
height = MONITOR_HEIGHT / 2

# Base colors for game elements
BACKGROUND_COLOR = color("577590")
TEXT_COLOR = color("F9C74F")
os.environ['SDL_VIDEO_CENTERED'] = '1'  # Centers the window

py.init()
clock = py.time.Clock()
screen = py.display.set_mode((width, height))
py.display.set_caption("Змійка 3.2.15")


def start_game():
    global game_state, BACKGROUND_COLOR
    BACKGROUND_COLOR = color("263340")
    game_state = GameState.GAME
    global field
    field = Field(100, 100, width // 2)
    field.spawn_snake(Position(20, 2), State.HEAD_RIGHT, 6, LiveState.REVIVABLE, 1, True, 10, 0.5)

# Toggles fullscreen
def fullscreen():
    global width
    global height
    if width == MONITOR_WIDTH:
        width = MONITOR_WIDTH // 2
        height = MONITOR_HEIGHT // 2
    else:
        width = MONITOR_WIDTH
        height = MONITOR_HEIGHT
    py.display.set_mode((width, height))
    global CAPTION_FONT, BUTTON_FONT, main_menu_buttons
    CAPTION_FONT = py.font.Font("Rubik.ttf", int(width // 8))
    BUTTON_FONT = py.font.Font("Rubik.ttf", int(height // 14))
    for button in main_menu_buttons:
        button.set_font(BUTTON_FONT)


# Stops the program and closes the window
def quit_game():
    global running
    running = False


# Initializes buttons for main menu
CAPTION_FONT, BUTTON_FONT = py.font.Font("Rubik.ttf", int(width // 8)), py.font.Font("Rubik.ttf", int(height // 14))
main_menu_buttons = []

button_start = Button("Start", BUTTON_FONT, 0.5, 0.6, screen, start_game)
main_menu_buttons.append(button_start)

button_start = Button("Fullscreen", BUTTON_FONT, 0.5, 0.7, screen, fullscreen)
main_menu_buttons.append(button_start)

button_start = Button("Quit", BUTTON_FONT, 0.5, 0.8, screen, quit_game)
main_menu_buttons.append(button_start)


class GameState(Enum):
    MAIN_MENU = 0
    GAME = 1


def render_main_menu(current_frame: int):
    rotation = math.sin(current_frame / 52) * 5
    scaling = math.sin(current_frame / 14) / 20 + 1

    screen.fill(BACKGROUND_COLOR)

    # Animation of caption text "ЗМІЙКА"
    text = CAPTION_FONT.render("ЗМІЙКА", True, TEXT_COLOR)
    text = py.transform.rotate(text, rotation)
    text = py.transform.scale(text, (text.get_width() * scaling, text.get_height() * scaling))
    text_rect = text.get_rect(center=(width * 0.5, height * 0.3))

    screen.blit(text, text_rect)
    for button in main_menu_buttons:
        button.process()


w_pressed = False
a_pressed = False
s_pressed = False
d_pressed = False
j_pressed = False

SNACK_SPAWN = 150
APPLE_SPAWN = 800
snack_spawn_timer = SNACK_SPAWN
apple_spawn_timer = APPLE_SPAWN

direction = State.HEAD_RIGHT


def render_game(current_frame: int):
    global field
    global w_pressed
    global a_pressed
    global s_pressed
    global d_pressed
    global j_pressed
    global SNACK_SPAWN
    global APPLE_SPAWN
    global snack_spawn_timer
    global apple_spawn_timer
    global direction

    screen.fill(BACKGROUND_COLOR)
    keys = py.key.get_pressed()
    if keys[py.K_w]:
        if not w_pressed:
            w_pressed = True
            direction = State.HEAD_UP
    else:
        if w_pressed:
            w_pressed = False

    if keys[py.K_a]:
        if not a_pressed:
            a_pressed = True
            direction = State.HEAD_LEFT
    else:
        if a_pressed:
            a_pressed = False

    if keys[py.K_s]:
        if not s_pressed:
            s_pressed = True
            direction = State.HEAD_DOWN
    else:
        if s_pressed:
            s_pressed = False

    if keys[py.K_d]:
        if not d_pressed:
            d_pressed = True
            direction = State.HEAD_RIGHT
    else:
        if d_pressed:
            d_pressed = False

    if keys[py.K_j]:
        if not j_pressed:
            j_pressed = True
            field.set_snakes_speed_state(0, SpeedState.ACCELERATION)
    else:
        if j_pressed:
            j_pressed = False
            field.set_snakes_speed_state(0, SpeedState.NORMAL)

    if apple_spawn_timer == 0:
        field.random_spawn_apple()
        apple_spawn_timer = APPLE_SPAWN
    else:
        apple_spawn_timer -= 1

    if snack_spawn_timer == 0:
        field.random_spawn_snack()
        snack_spawn_timer = SNACK_SPAWN
    else:
        snack_spawn_timer -= 1

    field.move_snake(0, direction)
    field.remove_snakes()
    field.draw(screen)


frame = 0
FPS = 60
game_state = GameState.MAIN_MENU
running = True
while running:
    clock.tick(FPS)
    # Frame number is useful for animations
    if frame > 3608:
        frame = 0
    else:
        frame += 1

    if game_state == GameState.MAIN_MENU:
        render_main_menu(frame)
    elif game_state == GameState.GAME:
        render_game(frame)

    for event in py.event.get():
        if event.type == py.QUIT:
            running = False
    py.display.flip()

py.quit()
