import pygame as py
from enum import Enum
from collections import deque
from random import randint, random
from interface_utils import color

EMPTY_BASE_COLOR = color("577590")
EMPTY_BORDER_COLOR = color("6687A3")

APPLE_BASE_COLOR = color("F94144")
SNACK_BASE_COLOR = color("F9C74F")

HEAD_COLOR_1 = color("F8793A")
TAIL_COLOR_1 = color("F9C74F")

HEAD_COLOR_2 = color("8BB964")
TAIL_COLOR_2 = color("C0D8AB")

py.mixer.init()
bite_sound = py.mixer.Sound("apple-bite.wav")
bite_sound.set_volume(0.3)


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

    def __repr__(self):
        return "(" + str(self.x) + ", " + str(self.y) + ")"

    def copy(self):
        return Position(self.x, self.y)


# values normally represent game cycles (FPS of the game)
class LiveState(Enum):
    ONE_TIME = 0
    REVIVABLE = 300


class SpeedState(Enum):
    NORMAL = 30
    ACCELERATION = 10


class State(Enum):
    EMPTY = 0
    SNACK = 1
    APPLE = 3
    TAIL = 10
    HEAD_LEFT = Position(-1, 0)
    HEAD_UP = Position(0, -1)
    HEAD_RIGHT = Position(1, 0)
    HEAD_DOWN = Position(0, 1)


def rand_event(odd: float) -> bool:
    return random() <= odd


class Field:
    class Square:
        def __init__(self, x: int, y: int, size: float):
            self.state = State.EMPTY
            self.snake = None
            self.size = int(size)
            self.rect = (x, y, self.size, self.size)
            self.eye_size = int(self.size // 25) + 1

        def draw(self, window: py.Surface, snake_color=None) -> None:
            if snake_color is not None:
                base_color = snake_color
            else:
                if self.state == State.APPLE:
                    base_color = APPLE_BASE_COLOR
                elif self.state == State.SNACK:
                    base_color = SNACK_BASE_COLOR
                else:
                    base_color = EMPTY_BASE_COLOR

            py.draw.rect(window, base_color, self.rect, 0)

            if self.state == State.HEAD_UP:
                x = self.rect[0]
                y = self.rect[1]
                py.draw.circle(window, (0, 0, 0), (x + self.size // 3, y + self.size // 3), self.eye_size)
                py.draw.circle(window, (0, 0, 0), (x + self.size // 3 * 2, y + self.size // 3), self.eye_size)
            elif self.state == State.HEAD_RIGHT:
                x = self.rect[0]
                y = self.rect[1]
                py.draw.circle(window, (0, 0, 0), (x + self.size // 3 * 2, y + self.size // 3), self.eye_size)
                py.draw.circle(window, (0, 0, 0), (x + self.size // 3 * 2, y + self.size // 3 * 2), self.eye_size)
            elif self.state == State.HEAD_DOWN:
                x = self.rect[0]
                y = self.rect[1]
                py.draw.circle(window, (0, 0, 0), (x + self.size // 3, y + self.size // 3 * 2), self.eye_size)
                py.draw.circle(window, (0, 0, 0), (x + self.size // 3 * 2, y + self.size // 3 * 2), self.eye_size)
            elif self.state == State.HEAD_LEFT:
                x = self.rect[0]
                y = self.rect[1]
                py.draw.circle(window, (0, 0, 0), (x + self.size // 3, y + self.size // 3), self.eye_size)
                py.draw.circle(window, (0, 0, 0), (x + self.size // 3, y + self.size // 3 * 2), self.eye_size)

    def __init__(self, x: float, y: float, field_size: float, size: float) -> None:
        self.field = []
        self.snakes = []
        self.food = []
        self.to_remove_snakes = []
        self.field_size = int(field_size)
        self.square_size = int(size // field_size)
        self.size = self.field_size * self.square_size
        self.x = int(x)
        self.y = int(y)
        for i in range(self.field_size):
            self.field.append([])  # Створює рядки поля
            for j in range(self.field_size):
                self.field[-1].append(
                    Field.Square(j * self.square_size + self.x, i * self.square_size + self.y, self.square_size))

    # returns spawned snake
    def spawn_snake(self, head_position: Position, facing: State, length: int, live: LiveState, coyote_death_time: int,
                    drop_start_sprint: bool, sprint_lose_weight: int, odd_when_dying: float):
        return self.snakes.append(Snake(head_position, facing, length, live, coyote_death_time,
                                        drop_start_sprint, sprint_lose_weight, odd_when_dying, self))

    def spawn_snack(self, position: Position) -> bool:
        square = self.get_square(position)
        if square.state == State.EMPTY:
            self.food.append(square)
            square.state = State.SNACK
            return True
        return False

    def spawn_apple(self, position: Position) -> bool:
        square = self.get_square(position)
        if square.state == State.EMPTY:
            self.food.append(square)
            square.state = State.APPLE
            return True
        return False

    def rand_position(self) -> Position:
        return Position(randint(0, self.field_size - 1), randint(0, self.field_size - 1))  # FIELD_SIZE - 1 inclusive

    def rand_free_position(self) -> Position or None:
        free_positions = [(row, col) for row in range(self.field_size) for col in range(self.field_size) if
                          self.field[row][col].state == State.EMPTY]

        if len(free_positions) == 0:
            return None

        rand_index = randint(0, len(free_positions) - 1)
        return Position(free_positions[rand_index][0], free_positions[rand_index][1])

    def random_spawn_snack(self) -> None:
        self.spawn_snack(self.rand_free_position())

    def random_spawn_apple(self) -> None:
        self.spawn_apple(self.rand_free_position())

    def set_square_state(self, position: Position, state: State, snake=None) -> None:
        self.field[position.y][position.x].state = state
        self.field[position.y][position.x].snake = snake

    def get_square_state(self, position: Position) -> State:
        return self.field[position.y][position.x].state

    def set_snakes_speed_state(self, index: int, state: SpeedState) -> None:
        self.snakes[index].set_speed_state(state)

    def move_snake(self, snake, direction: State) -> None:
        self.snakes[snake].move(direction)

    def remove_snakes(self) -> None:
        while len(self.to_remove_snakes) > 0:
            remove_func = self.to_remove_snakes.pop(0)
            remove_func()

    def get_square(self, position: Position) -> Square:
        return self.field[position.y][position.x]

    def draw(self, screen: py.Surface) -> None:
        py.draw.rect(screen, EMPTY_BASE_COLOR, (self.x, self.y, self.size, self.size))
        for i in range(1, self.field_size):
            x_pos = self.x + self.square_size * i - 1
            py.draw.line(screen, EMPTY_BORDER_COLOR, (x_pos, self.y), (x_pos, self.y + self.size - 1), 2)
        for i in range(1, self.field_size):
            y_pos = self.y + self.square_size * i - 1
            py.draw.line(screen, EMPTY_BORDER_COLOR, (self.x, y_pos), (self.x + self.size - 1, y_pos), 2)
        for snake in self.snakes:
            snake.draw(screen)
        for food in self.food:
            food.draw(screen)


class Snake:
    def __init__(self, head_position: Position, facing: State, length: int, live: LiveState,
                 coyote_death_time: int, drop_start_sprint: bool, sprint_lose_weight: int, odd_when_dying: float,
                 field: Field):
        self.snake = deque()
        self.field = field
        self.direction = facing
        self.name = len(self.field.snakes)
        if self.name == 0:
            self.start_color = HEAD_COLOR_1
            self.end_color = TAIL_COLOR_1
        else:
            self.start_color = HEAD_COLOR_2
            self.end_color = TAIL_COLOR_2

        self.food = 0

        self.move_timer = 0
        self.speed_state = SpeedState.NORMAL

        self.DROP_START_SPRINT = drop_start_sprint
        self.sprint_lose_weight_timer = 0
        self.SPRINT_LOSE_WEIGHT = sprint_lose_weight
        self.ODD_WHEN_DYING = odd_when_dying

        self.START_TAIL_LENGTH = length - 1
        self.near_death_counter = 0  # represents if sneak had died previous move
        self.COYOTE_DEATH_TIME = coyote_death_time
        self.revive_timer = 0
        self.LIVE_STATE = live

        self.snake.append(head_position.copy())
        self.field.set_square_state(head_position, facing, self)

        for i in range(self.START_TAIL_LENGTH):
            head_position -= facing.value
            self.snake.append(head_position.copy())
            self.field.set_square_state(head_position, State.TAIL, self)

    def set_speed_state(self, state: SpeedState) -> None:
        self.speed_state = state
        self.move_timer = 0
        if state == SpeedState.ACCELERATION:
            self.sprint_lose_weight_timer = 0
            if self.DROP_START_SPRINT:
                self.lose_weight()

    def lose_weight(self) -> None:
        if len(self.snake) > 1:
            poop_pos = self.snake.pop()
            self.field.set_square_state(poop_pos, State.SNACK)
            self.field.food.append(self.field.get_square(poop_pos))

    def revive(self) -> None:
        # direction is same as before death
        self.food = self.START_TAIL_LENGTH

        self.move_timer = 0
        self.sprint_lose_weight_timer = 0

        random_pos = self.field.rand_free_position()
        if random_pos is None:
            return

        self.revive_timer = 0
        self.snake.append(random_pos.copy())
        self.field.set_square_state(random_pos, self.direction, self)

    def remove(self) -> None:
        while not len(self.snake) == 0:
            square = self.field.get_square(self.snake.popleft())
            if rand_event(self.ODD_WHEN_DYING):
                square.state = State.EMPTY
            else:
                square.state = State.SNACK  # leave some mats
                self.field.food.append(square)


    def complete_remove(self) -> None:
        self.remove()
        self.field.snakes.remove(self)

    def dying_check(self, new_direction: State) -> None:
        if self.near_death_counter != self.COYOTE_DEATH_TIME:
            self.near_death_counter += 1
            self.field.set_square_state(self.snake[0], new_direction, self)
        else:
            if self.LIVE_STATE == LiveState.ONE_TIME:
                self.field.to_remove_snakes.append(self.complete_remove)
            else:
                self.field.to_remove_snakes.append(self.remove)
                self.revive_timer = self.LIVE_STATE.value
                self.near_death_counter = 0

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
        if len(self.snake) > 1:
            if self.snake[0] + direction.value != self.snake[1]:
                self.direction = direction
        else:
            self.direction = direction
        # else don't change

        new_head_position = self.snake[0] + self.direction.value

        # check if going out of field
        if new_head_position.x < 0 or new_head_position.x >= 25:
            self.dying_check(self.direction)
            return
        if new_head_position.y < 0 or new_head_position.y >= 25:
            self.dying_check(self.direction)
            return

        # means if snake crashes into its end-tail, but also it will grow next move
        if new_head_position == self.snake[-1] and self.food != 0:
            self.dying_check(self.direction)
            return

        new_head_square = self.field.get_square(new_head_position)
        new_head_square_state = new_head_square.state

        if new_head_square_state == State.APPLE or new_head_square_state == State.SNACK:
            self.field.food.remove(new_head_square)
            self.food += new_head_square_state.value
            bite_sound.play()
        #  elif isinstance(state_of_square.value, Position):  # meaning snake's head
        # TODO : snakes' heads collision
        elif new_head_square_state != State.EMPTY:
            self.dying_check(self.direction)
            return

        # if all checks done - than we can move our snake
        self.near_death_counter = 0

        if self.speed_state == SpeedState.ACCELERATION:
            if self.sprint_lose_weight_timer == self.SPRINT_LOSE_WEIGHT:
                self.lose_weight()
                self.sprint_lose_weight_timer = 0
            else:
                self.sprint_lose_weight_timer += 1

        self.field.set_square_state(self.snake[0], State.TAIL, self)  # making old head a tail
        if self.food != 0:
            self.food -= 1
        else:
            self.field.set_square_state(self.snake.pop(), State.EMPTY)  # delete tail
        self.snake.appendleft(new_head_position)  # adding a new head
        self.field.set_square_state(self.snake[0], self.direction, self)  # drawing new! head

    def draw(self, screen: py.Surface) -> None:
        if len(self.snake) == 0:
            return
        color_step = ((self.end_color[0] - self.start_color[0]) / len(self.snake),
                      (self.end_color[1] - self.start_color[1]) / len(self.snake),
                      (self.end_color[2] - self.start_color[2]) / len(self.snake))
        real_color = self.start_color
        current_color = self.start_color
        for square_pos in self.snake:
            self.field.get_square(square_pos).draw(screen, real_color)
            current_color = (current_color[0] + color_step[0],
                             current_color[1] + color_step[1],
                             current_color[2] + color_step[2])
            real_color = (int(current_color[0]), int(current_color[1]), int(current_color[2]))
