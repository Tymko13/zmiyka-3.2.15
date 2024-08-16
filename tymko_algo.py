import math

from ClassClaster import *
import random

directions = [State.HEAD_UP, State.HEAD_RIGHT, State.HEAD_DOWN, State.HEAD_LEFT]


def get_direction(field: Field, snake: Snake) -> State:
    if len(snake.snake) == 0:
        return snake.direction

    if len(field.food) > 0:
        if snake.speed_state != SpeedState.ACCELERATION:
            snake.set_speed_state(SpeedState.ACCELERATION)
    else:
        if snake.speed_state != SpeedState.NORMAL:
            snake.set_speed_state(SpeedState.NORMAL)

    available_directions = get_available_directions(field, snake.snake[0])
    if len(available_directions) == 0:
        return snake.direction
    if len(available_directions) > 1:
        available_directions = filter_directions(available_directions, field, snake)
    if len(available_directions) > 1:
        return get_closest_food(field, available_directions, snake)
    if len(available_directions) == 1:
        return available_directions[0]
    return snake.direction


def get_available_directions(field: Field, square_pos: Position) -> [State, ...]:
    available_directions = []
    for direction in directions:
        position = square_pos + direction.value
        if position.x < 0 or position.x > field.field_size - 1 or position.y < 0 or position.y > field.field_size - 1:
            continue

        current_square_state = field.get_square_state(position)
        if (current_square_state == State.EMPTY
                or current_square_state == State.SNACK
                or current_square_state == State.APPLE):
            available_directions.append(direction)
    return available_directions


def filter_directions(available_directions: [State, ...], field: Field, snake: Snake) -> [State, ...]:
    result = []
    for available_direction in available_directions:
        states = []
        for direction in directions:
            states.append(field.get_square_state(available_direction.value + direction.value))
        if states.__contains__(State.EMPTY) or states.__contains__(State.SNACK) or states.__contains__(State.APPLE):
            result.append(available_direction)
    return result



def get_closest_food(field: Field, available_directions: [State, ...], snake: Snake) -> State:
    foods = []
    for food in field.food:
        foods.append(Position((food.rect[0] - field.x) // field.square_size,
                              (food.rect[1] - field.y) // field.square_size))

    if len(foods) == 0:
        return random.choice(available_directions)

    head_pos = snake.snake[0]
    closest_direction = available_directions[0]
    distance_to_food = distance(foods[0], closest_direction.value + head_pos)
    for direction in available_directions:
        for food in foods:
            current_distance = distance(food, direction.value + head_pos)
            if current_distance < distance_to_food:
                closest_direction = direction
                distance_to_food = current_distance
    return closest_direction


def distance(pos1: Position, pos2: Position) -> float:
    return math.sqrt(sum([x ** 2 for x in [pos1.x - pos2.x, pos1.y - pos2.y]]))

