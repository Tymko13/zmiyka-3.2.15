from CrazySnakeAI.SnakeAI import NeuralNetwork, CostFunctions, ActivationFunctions
from ClassClaster import Field, Snake, SpeedState, State, Position
from numpy import ndarray, argmin, argmax, zeros

actions = (State.HEAD_UP, State.HEAD_RIGHT, State.HEAD_DOWN, State.HEAD_LEFT)

def start_game(snake: Snake):
    snake.set_speed_state(SpeedState.ACCELERATION)

def distance(pos1: Position, pos2: Position):
    return abs(pos1.x - pos2.x) + abs(pos1.y - pos2.y)

def is_inside(pos):
    if pos.x < 0 or pos.x >= 25:
        return False
    if pos.y < 0 or pos.y >= 25:
        return False
    return True

def get_optimal_target(field: Field, pos: Position) -> Position:
    food = []
    dis = []

    for y, row in enumerate(field.field):
        for x, square in enumerate(row):
            if square.state == State.APPLE or square.state == State.SNACK:
                food.append(Position(x, y))
    
    if len(food) == 0:
        if pos != Position(12,12):
            return Position(12, 12)
        else:
            return Position(13, 13)

    for target in food:
        dis.append(distance(target, pos))
       
    return food[ argmin(dis) ]

#   0
# 3   1
#   2

def get_state(field: Field, snake: Snake) -> ndarray:
    state = zeros(6)
    #state = zeros(4)
    if len(snake.snake) == 0:
        return state
    snake_pos = snake.snake[0]
    
    positions_around = [move.value + snake_pos for move in actions]
    
    target_pos = get_optimal_target(field, snake_pos)
    target_pos -= snake_pos

    # up
    if target_pos.y < 0:
        state[0] = 5
        target_pos.y = -1
    # down
    elif target_pos.y > 0:
        state[2] = 5
        target_pos.y = 1
        
    # left
    if target_pos.x < 0:
        state[3] = 5
        target_pos.x = -1
    # right
    elif target_pos.x > 0:
        state[1] = 5
        target_pos.x = 1    

    state[-2] = target_pos.x
    state[-1] = target_pos.y

    for i, pos in enumerate(positions_around):
        if not is_inside(pos):
            state[i] = 1
            continue
        
        if field.get_square(pos).snake == None:
            state[i] = 0
        else:
            state[i] = 1
                
    return state

network = NeuralNetwork(NeuralNetwork.Parameters.file('CrazySnakeAI/ta.enjoyer'), CostFunctions.Quadratic_Cost_Function, 
                       [ ActivationFunctions.ReLU,
                        ActivationFunctions.ReLU,
                        ActivationFunctions.ReLU,
                        ActivationFunctions.linear ]
                       )

def act(field: Field, snake: Snake) -> State:
    state = get_state(field, snake)
    action_index = argmax( network.calculate_outputs(state) )
    return actions[action_index]