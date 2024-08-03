from ClassClaster import Snake, Field, State, SpeedState

class Brain:
    def __init__(self, snake: Snake):
        self.snake = snake
        self.field = snake.field
        self.direction = snake.direction
        
    # will be called automatically every game cycle
    def move_snake(self) -> None:
        self.snake.move(self.direction)
        
    def set_snake_speed_state(self, state: SpeedState) -> None:
        self.snake.set_speed_state(state)





