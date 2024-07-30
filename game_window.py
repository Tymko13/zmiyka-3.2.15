import pygame as py
from screeninfo import get_monitors
import math

width = get_monitors()[0].width / 2
height = get_monitors()[0].height / 2

BACKGROUND_COLOR = (50, 50, 100)
TEXT_COLOR = (200, 100, 0)

py.init()
clock = py.time.Clock()
screen = py.display.set_mode((width, height))
py.display.set_caption("Змійка 3.2.15")
font = py.font.Font("Rubik.ttf", 128)

frame = 0
running = True
while running:
    clock.tick(30)
    if frame > 2**32 - 1:
        frame = 0
    else:
        frame += 1

    rotation = math.sin(frame / 20) * 5
    scaling = math.sin(frame / 8) / 20 + 1

    screen.fill(BACKGROUND_COLOR)
    text = font.render("ЗМІЙКА", True, TEXT_COLOR)
    text = py.transform.rotate(text, rotation)
    text = py.transform.scale(text, (text.get_width() * scaling, text.get_height() * scaling))
    text_rect = text.get_rect(center=(width // 2, height // 4))
    screen.blit(text, text_rect)

    for event in py.event.get():
        if event.type == py.QUIT:
            running = False

    py.display.flip()

py.quit()
