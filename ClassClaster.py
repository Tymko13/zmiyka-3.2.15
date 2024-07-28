from enum import Enum

class State(Enum):
    Empty = 0
    Snake = 1

class Field:
    
    class Square:
        state = State.Empty

    field = []
    
    def __init__(self):
        for i in range(25):
            self.field.append([])
            for j in range(25):
                self.field[-1].append(Field.Square())
    
    


