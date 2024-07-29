import pygame as py
from enum import Enum

class State(Enum):
    Empty = 0
    Snake = 1

class Field:
    
    class Square:
        state = State.Empty

        def __init__(self, x, y):
            self.rect = (x,y, 30,30) # (30,30) - size
            
        def draw(self, window):
            
            if self.state == State.Empty:
                Color = (100,100,200)
            elif self.state == State.Snake:
                Color = (200,100,100)
            
            py.draw.rect(window, Color, self.rect)

    field = []
    
    def __init__(self):
        for i in range(25):
            self.field.append([])
            for j in range(25):
                self.field[-1].append(Field.Square( i*30, j*30 )) # square position
                
    def draw(self, window):
        for row in self.field:
            for square in row:
                square.draw(window)
    


