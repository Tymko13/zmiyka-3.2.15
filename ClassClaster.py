import pygame as py
from enum import Enum
from collections import deque

SQUARE_SIZE = 30  # Ширина та висота клітинок поля в пікселях
FIELD_SIZE = 25  # Ширина та висота поля в клітинках

COOL_BLUE_COLOR = (100, 100, 200)
COOL_RED_COLOR = (200, 100, 100)
COOL_YELLOW_COLOR = (200, 200, 100)


class Position:
    def __init__(self, x=0, y=0):
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

    def __init__(self, head_position, facing, length, field):
        self.snake.append(head_position)
        field.set_square_state(head_position, facing)
        for i in range(length - 1):
            head_position -= facing.value
            self.snake.append(head_position)
            field.set_square_state(head_position, State.TAIL)

    def move(self, field):
        field.set_square_state(self.snake.pop(), State.EMPTY)


class Field:
    field = []
    snakes = []

    class Square:
        def __init__(self, x, y, state=State.EMPTY):
            self.rect = (x, y, SQUARE_SIZE, SQUARE_SIZE)
            self.state = state

        def draw(self, window):
            if self.state == State.EMPTY:
                color = COOL_BLUE_COLOR  # Блакитний
            else:
                color = COOL_RED_COLOR  # Червоний
            py.draw.rect(window, color, self.rect, 10)

    def __init__(self):
        for i in range(FIELD_SIZE):
            self.field.append([])  # Створює рядки поля
            for j in range(FIELD_SIZE):
                self.field[-1].append(Field.Square(j * SQUARE_SIZE, i * SQUARE_SIZE))  # Створює клітинки рядків

    def spawn_snake(self, head_position, facing, length):
        if len(self.snakes) == 0:
            self.snakes.append(Snake(head_position, facing, length, self))

    def set_square_state(self, position, state):
        self.field[position.y][position.x].state = state

    def draw(self, window):
        for row in self.field:
            for square in row:
                square.draw(window)
