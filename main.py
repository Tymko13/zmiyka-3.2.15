import pygame as py
import ClassClaster as cl

py.init()
clock = py.time.Clock()
FPS = 2
FIELD_SIZE = (750, 750)
window = py.display.set_mode(FIELD_SIZE)

field = cl.Field()
field.spawn_snake(cl.Position(7, 5), cl.State.HEAD_UP, 5)
field.spawn_apple(cl.Position(6, 5))

def draw_game_window():
    window.fill((0, 0, 0))
    field.draw(window)
    py.display.update()

# vars for tests
some_while_var = 0
some_for_var = 0

running = True
while running:
    some_while_var += 1
    print("some_while_var:", some_while_var//60)

    for event in py.event.get():
        some_for_var += 1
        print("some_for_var:", some_for_var)
        if event.type == py.QUIT:
            running = False

    #TODO : Game logic
    field.random_spawn_apple()

    draw_game_window()
    
    clock.tick(FPS)

py.quit()
