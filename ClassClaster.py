import pygame as py
from enum import Enum
from collections import deque

class Position:
    def __init__(self, x = 0, y = 0):
        self.x = x
        self.y = y
    
    def __add__(self, other):
        if isinstance(other, Position):
            return Position(self.x + other.x, self.y + other.y)
        return NotImplemented
    
    def __iadd__(self, other):
        if isinstance(other, Position):
            self.x += other.x
            self.y += other.y
            return self
        return NotImplemented

    def __sub__(self, other):
        if isinstance(other, Position):
            return Position(self.x - other.x, self.y - other.y)
        return NotImplemented
    
    def __isub__(self, other):
        if isinstance(other, Position):
            self.x -= other.x
            self.y -= other.y
            return self
        return NotImplemented

    def __mul__(self, value):
        if isinstance(value, int):
            return Position(self.x * value, self.y * value)
        return NotImplemented

    def __imul__(self, value):
        if isinstance(value, int):
            self.x *= value
            self.y *= value
            return self
        return NotImplemented

    def __rmul__(self, value):
        return self.__mul__(value)

    def __neg__(self):
        return Position(-self.x, -self.y)
    
    def __eq__(self, other):
        if isinstance(other, Position):
            return self.x == other.x and self.y == other.y
        return NotImplemented
    
    def __ne__(self, other):
        return not self.__eq__(other)

class State(Enum):
    EMPTY = 0
    TAIL = 10
    HEAD_LEFT = Position(-1, 0)
    HEAD_UP = Position(0, -1) 
    HEAD_RIGHT = Position(1, 0)
    HEAD_DOWN = Position(0, 1)

class Snake:
    snake = deque()

    def __init__(self, headPosition, facing, lenght, field):
        self.snake.append(headPosition)
        field.setSquareState(headPosition, facing)
        for i in range(1, lenght):
            headPosition -= facing.value
            self.snake.append(headPosition)
            field.setSquareState(headPosition, State.TAIL)

class Field:

    class Square:
        
        def __init__(self, x, y, state = State.EMPTY):
            self.rect = (x,y, 30,30) # (30,30) - size
            self.state = state

        def draw(self, window):
        
            if self.state == State.EMPTY:
                Color = (100,100,200)
            else:
                Color = (200,100,100)
            
            py.draw.rect(window, Color, self.rect, 10)

    field = []
    snakes = []

    def __init__(self):
        for i in range(25):
            self.field.append([])
            for j in range(25):
                self.field[-1].append(Field.Square( j*30, i*30 )) # square position
    
    def spawnSnake(self, headPosition, facing, lenght):
        if len(self.snakes) == 0:
            self.snakes.append(Snake(headPosition, facing, lenght, self))

    def setSquareState(self, position, state):
        self.field[position.y][position.x].state = state

    def draw(self, window):
        for row in self.field:
            for square in row:
                square.draw(window)
    