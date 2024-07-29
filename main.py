import pygame as py
import ClassClaster as cl

py.init()
clock = py.time.Clock()
fieldSize = (750, 750)
window = py.display.set_mode(fieldSize)

field = cl.Field()
field.spawn_snake(cl.Position(5, 7), cl.State.HEAD_UP, 6)


def draw_game_window():
    window.fill((0, 0, 0))
    field.draw(window)
    py.display.update()


running = True
while running:
    for event in py.event.get():
        if event.type == py.QUIT:
            running = False

    draw_game_window()
    py.time.delay(1000)
    field.snakes[0].move()
    print("ВСЕ ПРАЦЮЄ")

    clock.tick(60)  # FPS

py.quit()
