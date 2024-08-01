import pygame as py
from enum import Enum
from collections import deque
from random import randint

SQUARE_SIZE = 30  # Ширина та висота клітинок поля в пікселях
FIELD_SIZE = 25  # Ширина та висота поля в клітинках

FIELD_COLOR = (100, 100, 200)

SNAKE_HEAD_COLOR = (200, 60, 0)
SNAKE_TAIL_COLOR = (255, 80, 0)

APPLE_COLOR = (200, 100, 100)
SNACK_COLOR = (200, 200, 100)

# 1. spawn apples +
# 2. remake spawn mechanics +
# 3. add brrrrrrrrrr +
# 4. rewrite dying (some mats like apple) +
# 5. maybe some reaction to collision with something - not dying instantly +
# 6. head to head 
# 7. while brrrrrrrrrrr lose lenght


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
    

def rand_position() -> Position:
    return Position(randint(0, FIELD_SIZE - 1), randint(0, FIELD_SIZE - 1))  # FIELD_SIZE - 1 inclusive

def rand_free_position(field: list) -> Position or None:
    free_positions = [ (row, col) for row in range(FIELD_SIZE) for col in range(FIELD_SIZE) if field[row][col].state == State.EMPTY ]
    
    if len(free_positions) == 0:
        return None
    else:
        rand_index = randint(0, len(free_positions) - 1)
        return Position(free_positions[rand_index][0], free_positions[rand_index][1])
    

# values normally represent game cycles (FPS of the game)
class LiveState(Enum):
    ONE_TIME = 0
    REVIVABLE = 20


class SpeedState(Enum):
    NORMAL = 10
    ACCELERATION = 5


class State(Enum):
    EMPTY = 0
    SNACK = 1
    APPLE = 3
    TAIL = 10
    HEAD_LEFT = Position(-1, 0)
    HEAD_UP = Position(0, -1)
    HEAD_RIGHT = Position(1, 0)
    HEAD_DOWN = Position(0, 1)
    

class Field:
    class Square:
        def __init__(self, x: int, y: int):
            self.state = State.EMPTY
            self.rect = (x, y, SQUARE_SIZE, SQUARE_SIZE)

        def draw(self, window: py.Surface) -> None:
            if self.state == State.EMPTY:
                color = FIELD_COLOR
            elif self.state == State.APPLE:
                color = APPLE_COLOR
            elif self.state == State.SNACK:
                color = SNACK_COLOR
            elif self.state == State.TAIL:
                color = SNAKE_TAIL_COLOR
            else:
                color = SNAKE_HEAD_COLOR
            py.draw.rect(window, color, self.rect, 10)

    def __init__(self, x: int, y: int) -> None:
        self.field = []
        self.snakes = []
        for i in range(FIELD_SIZE):
            self.field.append([])  # Створює рядки поля
            for j in range(FIELD_SIZE):
                self.field[-1].append(Field.Square(j * SQUARE_SIZE + x, i * SQUARE_SIZE + y))  # Створює клітинки рядків

    def spawn_snake(self, head_position: Position, facing: State, length: int, live: LiveState) -> None:
        self.snakes.append(Snake(head_position, facing, length, live, self))

    def spawn_snack(self, position: Position) -> bool:
        if self.get_square_state(position) == State.EMPTY:
            self.set_square_state(position, State.SNACK)
            return True
        return False

    def random_spawn_snack(self, tries: int = 10) -> bool:
        for n in range(tries):
            if self.spawn_snack(rand_position()):
                return True
        return False

    def spawn_apple(self, position: Position) -> bool:
        if self.get_square_state(position) == State.EMPTY:
            self.set_square_state(position, State.APPLE)
            return True
        return False

    def random_spawn_apple(self, tries: int = 10) -> bool:
        for n in range(tries):
            if self.spawn_apple(rand_position()):
                return True
        return False

    def set_square_state(self, position: Position, state: State) -> None:
        self.field[position.y][position.x].state = state

    def get_square_state(self, position: Position) -> State:
        return self.field[position.y][position.x].state

    def set_snakes_speed_state(self, index: int, state: SpeedState) -> None:
        self.snakes[index].set_speed_state(state)

    def move_snake(self, index: int, direction: State) -> None:
        self.snakes[index].move(direction)

    def draw(self, window: py.Surface) -> None:
        for row in self.field:
            for square in row:
                square.draw(window)
                

class Snake:
    def __init__(self, head_position: Position, facing: State, length: int, live: LiveState, field: Field):
        self.snake = deque()
        self.field = field
        self.direction = facing
        
        self.food = 0
        
        self.move_timer = 0
        self.speed_state = SpeedState.NORMAL
        
        self.start_tail_length = length - 1
        self.near_death = False  # represents if sneak would have died previous move
        self.revive_timer = 0
        self.live_state = live
        
        self.snake.append(head_position.copy())
        self.field.set_square_state(head_position, facing)
        
        for i in range(self.start_tail_length):
            head_position -= facing.value
            self.snake.append(head_position.copy())
            self.field.set_square_state(head_position, State.TAIL)

    def set_speed_state(self, state: SpeedState) -> None:
        self.speed_state = state
        self.move_timer = state.value

    def revive(self) -> None:
        # direction is same as before death
        self.food = self.start_tail_length
        
        self.move_timer = 0
        
        random_pos = rand_free_position(self.field.field)
        if random_pos == None:
            return
        
        self.revive_timer = 0
        self.snake.append(random_pos.copy())
        self.field.set_square_state(random_pos, self.direction)

    def remove(self) -> None:
        while not len(self.snake) == 0:
            if randint(0, 9):  # 90%
                self.field.set_square_state(self.snake.popleft(), State.EMPTY)
            else:
                self.field.set_square_state(self.snake.popleft(), State.SNACK) # leave some mats

    def complete_remove(self) -> None:
        self.remove(self)
        self.field.snakes.remove(self)

    def dying_check(self):
        if not self.near_death:
            self.near_death = True
        else:
            if self.live_state == LiveState.ONE_TIME:
                self.complete_remove()
            else:
                self.remove()
                self.revive_timer = self.live_state.value
                self.near_death = False

    def move(self, direction: State) -> None:
        # if needs to be revived
        if self.revive_timer == 1:
            self.revive()
            return
        # check if need to wait to revive
        elif self.revive_timer != 0:
            self.revive_timer -= 1
            return
        # else - alive

        # check if need to wait for a move
        if self.move_timer != 0:
            self.move_timer -= 1
            return
        # else - turn to move

        # restarting timer for movement
        self.move_timer = self.speed_state.value

        # check if moving outside of tail
        if self.direction.value != -direction.value:
            self.direction = direction
        # else don't change
        
        new_head_position = self.snake[0] + self.direction.value
        
        # check if going out of field
        if new_head_position.x < 0 or new_head_position.x >= FIELD_SIZE:
            self.dying_check()
            return
        if new_head_position.y < 0 or new_head_position.y >= FIELD_SIZE:
            self.dying_check()
            return

        # means if snake crashes into its end-tail but also it will grow next move
        if new_head_position == self.snake[-1] and self.food != 0:
            self.dying_check()
            return

        state_of_square = self.field.get_square_state(new_head_position)
        
        if state_of_square == State.APPLE:
            self.food += State.APPLE.value
        elif state_of_square == State.SNACK:
            self.food += State.SNACK.value
        elif isinstance(state_of_square.value, Position):  # meaning snake's head
            # TODO : snakes' heads collision
            pass
        elif state_of_square != State.EMPTY:
            self.dying_check()
            return
        
        # if all checks done - than we can move our snake
        self.field.set_square_state(self.snake[0], State.TAIL)  # making old head a tail
        if self.food != 0:
            self.food -= 1
        else:
            self.field.set_square_state(self.snake.pop(), State.EMPTY)  # delete tail
        self.snake.appendleft(new_head_position)  # adding a new head
        self.field.set_square_state(self.snake[0], self.direction)  # drawing new! head
        