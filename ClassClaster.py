from email.mime import application
import pygame as py
from enum import Enum
from collections import deque
from random import randint

SQUARE_SIZE = 30  # Ширина та висота клітинок поля в пікселях
FIELD_SIZE = 25  # Ширина та висота поля в клітинках

COOL_BLUE_COLOR = (100, 100, 200)
COOL_RED_COLOR = (200, 100, 100)
COOL_YELLOW_COLOR = (200, 200, 100)
COOL_GREEN_COLOR = (50, 150, 50)

# 1. spawn apples +
# 2. remake spawn mechanics
# 3. add brrrrrrrrrr


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
    
    def copy(self):
        return Position(self.x, self.y)


class State(Enum):
    EMPTY = 0
    APPLE = 3
    TAIL = 10
    HEAD_LEFT = Position(-1, 0)
    HEAD_UP = Position(0, -1)
    HEAD_RIGHT = Position(1, 0)
    HEAD_DOWN = Position(0, 1)
    

class Field:
    field = []
    snakes = []

    class Square:
        state = State.EMPTY

        def __init__(self, x: int, y: int):
            self.rect = (x, y, SQUARE_SIZE, SQUARE_SIZE)

        def draw(self, window: py.Surface):
            if self.state == State.EMPTY:
                color = COOL_BLUE_COLOR
            elif self.state == State.APPLE:
                color = COOL_RED_COLOR
            elif self.state == State.TAIL:
                color = COOL_YELLOW_COLOR
            else:
                color = COOL_GREEN_COLOR
            py.draw.rect(window, color, self.rect, 10)

    def __init__(self):
        for i in range(FIELD_SIZE):
            self.field.append([])  # Створює рядки поля
            for j in range(FIELD_SIZE):
                self.field[-1].append(Field.Square(j * SQUARE_SIZE, i * SQUARE_SIZE))  # Створює клітинки рядків

    def spawn_snake(self, head_position: Position, facing: State, length: int) -> None:
        self.snakes.append(Snake(head_position, facing, length, self))

    def spawn_apple(self, position: Position) -> bool:
        if self.get_square_state(position) == State.EMPTY:
            self.set_square_state(position, State.APPLE)
            return True
        return False

    def random_spawn_apple(self, tries: int = 10) -> bool:
        for n in range(tries):
            if self.spawn_apple(Position(randint(0, 24), randint(0, 24))):  # 24 inclusive
                return True
        return False

    def set_square_state(self, position: Position, state: State) -> None:
        self.field[position.y][position.x].state = state

    def get_square_state(self, position: Position) -> State:
        return self.field[position.y][position.x].state

    def move_snake(self, index: int, direction: State) -> None:
        self.snakes[index].move(direction)

    def draw(self, window: py.Surface) -> None:
        for row in self.field:
            for square in row:
                square.draw(window)
                

class Snake:
    snake = deque()
    food = 0

    def __init__(self, head_position: Position, facing: State, length: int, field: Field):
        self.direction = facing
        self.field = field
        self.snake.append(head_position.copy())
        self.field.set_square_state(head_position, facing)
        for i in range(length - 1):
            head_position -= self.direction.value
            self.snake.append(head_position.copy())
            self.field.set_square_state(head_position, State.TAIL)

    def __del__(self):
        for part in self.snake:
            self.field.set_square_state(part, State.EMPTY)

    def move(self, direction: State) -> None:
        if self.direction.value != -direction.value:
            self.direction = direction
        # else don't change

        old_head_position = self.snake[0].copy()  # temp
        
        self.field.set_square_state(old_head_position, State.TAIL)  # making old head a tail
        if self.food != 0:
            self.food -= 1
        else:
            self.field.set_square_state(self.snake.pop(), State.EMPTY)  # delete tail 
        
        new_head_position = old_head_position + self.direction.value
        
        if new_head_position.x < 0 or new_head_position.x >= FIELD_SIZE:
            self.field.snakes.remove(self)
            return
        if new_head_position.y < 0 or new_head_position.y >= FIELD_SIZE:
            self.field.snakes.remove(self)
            return

        old_state = self.field.get_square_state(new_head_position)
        
        if old_state == State.APPLE:
            self.food += State.APPLE.value
        elif old_state != State.EMPTY:
            self.field.snakes.remove(self)
            return
        
        self.snake.appendleft(new_head_position)  # adding a new head
        self.field.set_square_state(self.snake[0], self.direction)  # drawing new! head
        