import pygame as py
import ClassClaster as cl

py.init()
clock = py.time.Clock()
fieldSize = (750, 750)
window = py.display.set_mode(fieldSize)

field = cl.Field()

def drawGameWindow():
    
    window.fill((0,0,0))
    field.draw(window)
    py.display.update()

running = True
while running:
    for event in py.event.get():
        if event.type == py.QUIT:
            running = False

    drawGameWindow()

    clock.tick(60) # FPS

py.quit()
    