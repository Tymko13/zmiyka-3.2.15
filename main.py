import pygame as py
import ClassClaster as cl

py.init()
clock = py.time.Clock()
fieldSize = (750, 750)
window = py.display.set_mode(fieldSize)

field = cl.Field()
field.spawn_snake(cl.Position(0, 0), cl.State.HEAD_DOWN, 1)
field.spawn_apple(cl.Position(0, 5))
field.spawn_apple(cl.Position(0, 7))
field.spawn_apple(cl.Position(0, 12))
field.spawn_apple(cl.Position(0, 13))
field.spawn_apple(cl.Position(0, 20))

def draw_game_window():
    window.fill((0, 0, 0))
    field.draw(window)
    py.display.update()

running = True
while running:
    for event in py.event.get():
        if event.type == py.QUIT:
            running = False

    #TODO : Game logic

    draw_game_window()
    py.time.delay(2000)
    field.move_snake(0, cl.State.HEAD_DOWN)

    clock.tick(60)  # FPS

py.quit()
