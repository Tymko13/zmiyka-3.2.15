import pygame as py
import ClassClaster as cl

py.init()
clock = py.time.Clock()
FPS = 2
FIELD_SIZE = (750, 750)
window = py.display.set_mode(FIELD_SIZE)

field = cl.Field()
field.spawn_snake(cl.Position(10, 23), cl.State.HEAD_UP, 2)
#field.spawn_snake(cl.Position(15, 23), cl.State.HEAD_UP, 2)
field.set_snakes_speed_state(0, cl.SpeedState.ACCELERATION)

def draw_game_window():
    window.fill((0, 0, 0))
    field.draw(window)
    py.display.update()

# vars for tests
some_while_var = 0
some_for_var = 0

running = True
while running:
    
    draw_game_window()
    clock.tick(FPS)

    some_while_var += 1
    print("some_while_var:", some_while_var)

    for event in py.event.get():
        some_for_var += 1
        print("some_for_var:", some_for_var)
        if event.type == py.QUIT:
            running = False

    #TODO : Game logic
    for snake in field.snakes:
        snake.move(cl.State.HEAD_UP)

py.quit()
