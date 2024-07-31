import pygame as py
import ClassClaster as cl

# what if head from 1st sneak moves first to the square
# to which the 2nd sneak also moves

py.init()
clock = py.time.Clock()
FPS = 6
FIELD_SIZE = (750, 750)
window = py.display.set_mode(FIELD_SIZE)

field = cl.Field()
field.spawn_snake(cl.Position(20, 2), cl.State.HEAD_RIGHT, 6, cl.LiveState.REVIVABLE)

def draw_game_window():
    window.fill((0, 0, 0))
    field.draw(window)
    py.display.update()
    
draw_game_window()

# vars for test
w_pressed = False
a_pressed = False
s_pressed = False
d_pressed = False
j_pressed = False

SNACK_SPAWN = 20
APPLE_SPAWN = 100

snack_spawn_timer = SNACK_SPAWN
apple_spawn_timer = APPLE_SPAWN

direction = cl.State.HEAD_RIGHT

running = True
while running:
    
    clock.tick(FPS)

    for event in py.event.get():
        if event.type == py.QUIT:
            running = False
            
    #TODO : Game logic
    
    keys = py.key.get_pressed()
    
    if keys[py.K_w]:
        if not w_pressed:
            w_pressed = True
            direction = cl.State.HEAD_UP
    else:
        if w_pressed:
            w_pressed = False
            
    if keys[py.K_a]:
        if not a_pressed:
            a_pressed = True
            direction = cl.State.HEAD_LEFT
    else:
        if a_pressed:
            a_pressed = False
    
    if keys[py.K_s]:
        if not s_pressed:
            s_pressed = True
            direction = cl.State.HEAD_DOWN
    else:
        if s_pressed:
            s_pressed = False
            
    if keys[py.K_d]:
        if not d_pressed:
            d_pressed = True
            direction = cl.State.HEAD_RIGHT
    else:
        if d_pressed:
            d_pressed = False
            
    if keys[py.K_j]:
        if not j_pressed:
            j_pressed = True
            field.set_snakes_speed_state(0, cl.SpeedState.ACCELERATION)
    else:
        if j_pressed:
            j_pressed = False
            field.set_snakes_speed_state(0, cl.SpeedState.NORMAL)
    
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
        
    draw_game_window()
    

py.quit()
