from screeninfo import get_monitors
from interface_utils import *
from ClassClaster import *
from enum import Enum
import math
import os

import CrazySnakeAI.brain as CAi

# Size of user's monitor
MONITOR_WIDTH = get_monitors()[0].width
MONITOR_HEIGHT = get_monitors()[0].height

# Current size of game window
width = MONITOR_WIDTH / 2
height = MONITOR_HEIGHT / 2

field_size = height * 0.85
FIELD_SQUARE_SIZE = 25
field = Field(height * 0.075, height * 0.075, FIELD_SQUARE_SIZE, field_size)
d_snake = None
t_snake = None

# Base colors for game elements
BACKGROUND_COLOR = color("577590")
LIGHT_BACKGROUND_COLOR = color("577590")
TEXT_COLOR = color("F9C74F")
os.environ['SDL_VIDEO_CENTERED'] = '1'  # Centers the window

py.init()
py.mixer.init()
py.mixer.music.load("8-bit-arcade.wav")
py.mixer.music.set_volume(0.7)
py.mixer.music.play(-1)

clock = py.time.Clock()
screen = py.display.set_mode((width, height))
py.display.set_caption("Змійка 3.2.15")


def start_game():
    global game_state, BACKGROUND_COLOR
    BACKGROUND_COLOR = color("263340")
    game_state = GameState.GAME

    global field, d_snake, t_snake
    d_snake = field.spawn_snake(Position(10, 6), State.HEAD_RIGHT, 6, LiveState.REVIVABLE, 3, True, 30, 0.5)
    t_snake = field.spawn_snake(Position(20, 15), State.HEAD_RIGHT, 6, LiveState.REVIVABLE, 3, True, 30, 0.5)
    
    CAi.start_game(d_snake)


# Toggles fullscreen
def fullscreen():
    global width, height
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

    global field, field_size, graph, button_menu
    field_size = height * 0.85
    field = Field(height * 0.075, height * 0.075, FIELD_SQUARE_SIZE,field_size)
    graph = Graph(2, height + 0.15 * (width - height), height // 14 * 4, 0.7 * (width - height), height // 14 * 3)
    button_menu = Button("Menu", BUTTON_FONT, (height + (width - height) / 2) / width, 0.85, screen, quit_game)


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
    GAME_OVER = 2


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


SNACK_SPAWN = 200
APPLE_SPAWN = 800
snack_spawn_timer = SNACK_SPAWN
apple_spawn_timer = APPLE_SPAWN

def render_game(current_frame: int):
    global field, d_snake, t_snake
    global SNACK_SPAWN
    global APPLE_SPAWN
    global snack_spawn_timer
    global apple_spawn_timer

    screen.fill(BACKGROUND_COLOR)

    if apple_spawn_timer == 0:
        field.random_spawn_apple()
        apple_spawn_timer = APPLE_SPAWN
    apple_spawn_timer -= 1

    if snack_spawn_timer == 0:
        field.random_spawn_snack()
        snack_spawn_timer = SNACK_SPAWN
    snack_spawn_timer -= 1

    d_snake.move(CAi.act(field, d_snake))
    # field.move_snake(1, direction)
    field.remove_snakes()
    field.draw(screen)
    py.draw.line(screen, LIGHT_BACKGROUND_COLOR, (height, 0), (height, height), 3)


graph = Graph(2, height + 0.15 * (width - height), height // 14 * 4, 0.7 * (width - height), height // 14 * 3)
previous_timer_text = ""

button_menu = Button("Menu", BUTTON_FONT, (height + (width - height) / 2) / width, 0.85, screen, quit_game)


def run_timer():
    global TIMER, FPS, game_state, graph, field, previous_timer_text

    current_time = TIMER / (FPS * 60)
    timer_text = ""
    if current_time < 10:
        timer_text += "0"
    timer_text += str(int(current_time))
    timer_text += ":"
    current_time = int((current_time - int(current_time)) * 60)
    if current_time < 10:
        timer_text += "0"
    timer_text += str(int(current_time))

    if TIMER < 0:
        game_state = GameState.GAME_OVER

    timer = BUTTON_FONT.render(timer_text, True, TEXT_COLOR)
    timer_rect = timer.get_rect(center=(height + (width - height) // 2, height // 7))
    screen.blit(timer, timer_rect)
    TIMER -= 1

    if previous_timer_text != timer_text:
        graph.add_data(len(field.snakes[0].snake), len(field.snakes[1].snake))
        previous_timer_text = timer_text
    graph.draw(screen)
    button_menu.process()


frame = 0
FPS = 60  # In frames per second
TIMER = 2 * 60 * FPS  # In minutes
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
        run_timer()

    for event in py.event.get():
        if event.type == py.QUIT:
            running = False
    py.display.flip()

py.mixer.music.stop()
py.quit()
