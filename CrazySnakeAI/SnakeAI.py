import numpy as np
from math import exp, ceil
from typing import Union
from CrazySnakeAI.interface_units import *
from enum import Enum

def node_cost(output_values: np.ndarray, expected_values: np.ndarray) -> np.ndarray:
    return (output_values - expected_values) ** 2 / 2

def derivative_node_cost(output_values: np.ndarray, expected_values: np.ndarray) -> np.ndarray:
    return output_values - expected_values

class CostFunctions(Enum):
    Quadratic_Cost_Function = (node_cost, derivative_node_cost)


def ReLU(value: float) -> float:
    return max(0, value)

def sigmoid(value: float) -> float:
    if abs(value) > 200:
        return 0 if value < 0 else 1
    return 1 / (1 + exp(-value))

def linear(value: float) -> float:
    return value

def derivative_ReLU(value: float) -> float:
    return 1 if value > 0 else 0

def derivative_sigmoid(value: float) -> float:
    if abs(value) > 200:
        return 0
    return exp(-value) / ( (1 + exp(-value)) ** 2 )    

def derivative_linear(value: float) -> float:
    return 1

class ActivationFunctions(Enum):
    ReLU = (ReLU, derivative_ReLU)
    sigmoid = (sigmoid, derivative_sigmoid)
    linear = (linear, derivative_linear)


class Layer:
    def __init__(self, inputs: int, outputs: int, weights: np.ndarray, biases: np.ndarray,
                 functions: ActivationFunctions):
        self.num_inputs = inputs
        self.num_outputs = outputs
        self.weights = weights
        self.biases = biases
        self.weighted_sum_values = np.zeros(outputs)
        self.activation_values = np.zeros(outputs)
        self.activation_function = np.vectorize(functions.value[0])
        self.derivative_function = np.vectorize(functions.value[1])
        
    def calculate(self, inputs: np.ndarray) -> np.ndarray:
        self.weighted_sum_values = np.dot(self.weights, inputs) + self.biases
        self.activation_values = self.activation_function(self.weighted_sum_values)
        return self.activation_values


class NeuralNetwork:

    class Parameters:
        def __init__(self, layer_sizes: tuple[int, ...]=None, filling: str=None, 
                     lower_bound: float=None, upper_bound: float=None, file_name: str=None):
            # layer_sizes[n] - num_outputs
            # layer_sizes[n-1] - num_inputs
            if isinstance(layer_sizes, tuple):
                
                if not all(isinstance(el, int) for el in layer_sizes):
                    raise ValueError("Invalid arguments")
                
                self.layer_sizes = layer_sizes    
                if filling == 'zeros':
                    self.weights = [np.zeros((layer_sizes[n], layer_sizes[n-1])) 
                                     for n in range(1, len(layer_sizes))]
                    self.biases = [np.zeros(layer_sizes[n])
                            for n in range(1, len(layer_sizes))]
                elif filling == 'uniform':
                    self.weights = [np.random.uniform(lower_bound, upper_bound, size=(layer_sizes[n], layer_sizes[n-1])) 
                                     for n in range(1, len(layer_sizes))]
                    self.biases = [np.random.uniform(lower_bound, upper_bound, size=layer_sizes[n])
                            for n in range(1, len(layer_sizes))]
                elif filling == 'randint':
                    self.weights = [np.random.randint(lower_bound, upper_bound, size=(layer_sizes[n], layer_sizes[n-1])) 
                                     for n in range(1, len(layer_sizes))]
                    self.biases = [np.random.randint(lower_bound, upper_bound, size=layer_sizes[n])
                            for n in range(1, len(layer_sizes))]

            elif isinstance(file_name, str):
                
                with open(file_name, 'rb') as file:
                    
                    self.layer_sizes = tuple([int(num) for num in file.readline().decode('utf-8').split(' ')])
                    self.weights = []
                    self.biases = []
                    
                    for index in range(1, len(self.layer_sizes)):
                        self.weights.append(np.array( [[float(num) for num in file.readline().decode('utf-8').split(' ')] 
                                                       for n in range(self.layer_sizes[index])] ))
                        self.biases.append(np.array( [float(num) for num in file.readline().decode('utf-8').split(' ')] ))

            else:
                raise ValueError("Invalid arguments")

        @classmethod
        def zeros(cls, layer_sizes: tuple[int, ...]):
            return cls(layer_sizes=layer_sizes, filling='zeros')

        @classmethod
        def uniform(cls, layer_sizes: tuple[int, ...], lower_bound: float, upper_bound: float):
            return cls(layer_sizes=layer_sizes, filling='uniform', lower_bound=lower_bound, upper_bound=upper_bound)
        
        @classmethod
        def randint(cls, layer_sizes: tuple[int, ...], lower_bound: float, upper_bound: float):
            return cls(layer_sizes=layer_sizes, filling='randint', lower_bound=lower_bound, upper_bound=upper_bound)

        @classmethod
        def file(cls, file_name: str):
            return cls(file_name=file_name)
        
        @classmethod
        def copy(cls, other_parameters):
            new = cls.zeros(other_parameters.layer_sizes)
            new.copy_from(other_parameters)
            return new

        def save_parameters(self, file_name: str) -> None:
            with open(file_name, 'wb') as file:
            
                line = ' '.join( str(num) for num in self.layer_sizes ) + '\n'
                file.write(line.encode('utf-8'))

                for weight, bias in zip(self.weights, self.biases):
                    for array in weight:
                        line = ' '.join( str(el) for el in array ) + '\n'
                        file.write(line.encode('utf-8'))
                    line = ' '.join( str(el) for el in bias ) + '\n'
                    file.write(line.encode('utf-8'))

        def copy_from(self, other_parameters) -> bool:
            if self.layer_sizes != other_parameters.layer_sizes:
                return False
            for index in range(len(self.layer_sizes) - 1):
                np.copyto(self.weights[index], other_parameters.weights[index])
                np.copyto(self.biases[index], other_parameters.biases[index])
            return True

    def __init__(self, parameters: Parameters,
                 node_cost_functions: CostFunctions,
                 functions: Union[list[ActivationFunctions], ActivationFunctions] ):
        self.parameters = NeuralNetwork.Parameters.copy(parameters)
        self.layer_sizes = self.parameters.layer_sizes
        self.inputs = np.zeros(self.layer_sizes[0])

        if isinstance(functions, list):
            self.layers = [Layer(self.layer_sizes[i], self.layer_sizes[i+1], self.parameters.weights[i], self.parameters.biases[i], functions[i]) 
                           for i in range(len(self.layer_sizes)-1)]
        else:
            self.layers = [Layer(self.layer_sizes[i], self.layer_sizes[i+1], self.parameters.weights[i], self.parameters.biases[i], functions) 
                           for i in range(len(self.layer_sizes)-1)]
        
        self.node_cost = node_cost_functions.value[0]
        self.derivative_node_cost = node_cost_functions.value[1]

        self.circle_buttons = None
        self.line_buttons = None
        self.max_values = None
        self.board = None

    def calculate_outputs(self, inputs: np.ndarray) -> np.ndarray:
        # important to work with the SAME array
        # so buttons can see the input values
        for i in range(len(self.inputs)):
            self.inputs[i] = inputs[i]
        #self.inputs = inputs.copy()
        for layer in self.layers:
            inputs = layer.calculate(inputs)
        return inputs.copy()

    def save_parameters(self, file_name: str) -> None:
        self.parameters.save_parameters(file_name)

    def cost(self, inputs: ndarray, expected_outputs: ndarray) -> float:
        return np.array([ (self.node_cost(self.calculate_outputs(inputs[index]), expected_outputs[index])).sum() 
                         for index in range(len(inputs)) ]).sum() / len(inputs)

    def backpropagation(self, inputs: ndarray, expected_outputs: ndarray) -> Parameters:
        
        gradient = NeuralNetwork.Parameters.zeros(self.layer_sizes)
        
        for inp, ex_out in zip(inputs, expected_outputs):
            
            impact_values = self.derivative_node_cost(self.calculate_outputs(inp), ex_out)

            for index in reversed(range(len(self.layers))):

                layer = self.layers[index]

                if index > 0:
                    previous_activations = self.layers[index - 1].activation_values  # reference
                else:
                    previous_activations = inp  # reference

                delta = impact_values * layer.derivative_function(layer.weighted_sum_values)

                gradient.weights[index] += np.outer(delta, previous_activations)
                gradient.biases[index] += delta
            
                if index > 0:
                    impact_values = np.dot(delta, layer.weights)
        
        for weight, bias in zip(gradient.weights, gradient.biases):
            weight /= len(inputs)
            bias /= len(inputs)

        return gradient
                
    def init_interface_units(self, screen_size: tuple[int, int]) -> None:
        
        max_screen_occupation = ( round(screen_size[0] * 0.7), round(screen_size[1] * 0.7))
        desired_spacings = (screen_size[0] // 6, screen_size[1] // 6)
        desired_radius = desired_spacings[1] * 0.2
        
        def calculate_column_positions(size: int, max_occupation: int, num_columns: int, desired_spacing: int) -> list[int]:

            required_width = desired_spacing * (num_columns - 1)
        
            if required_width > max_occupation:
                actual_spacing = max_occupation / (num_columns - 1)  # for now float
                required_width = max_occupation
            else:
                actual_spacing = desired_spacing
                
            start_position = (size - required_width) // 2
            positions = []
            
            for index in range(num_columns):
                positions.append(start_position + round(actual_spacing * index))
                
            return positions

        def get_radius(distance) -> float:
            actual_radius = distance / 4
            if desired_radius < actual_radius:
                actual_radius = desired_radius
            return actual_radius

        column_x_positions = calculate_column_positions(screen_size[0], max_screen_occupation[0],
                                                        len(self.layer_sizes), desired_spacings[0])
        
        nods_y_positions = [calculate_column_positions(screen_size[1], max_screen_occupation[1],
                                                          num_nods, desired_spacings[1])
                            for num_nods in self.layer_sizes]
        
        nods_positions = [ [(x_pos, y_pos) for y_pos in nods_y_positions[layer] ] 
                          for layer, x_pos in enumerate(column_x_positions) ]

        self.circle_buttons = []
        self.line_buttons = []
        self.max_values = MaxValues(self)
        self.board = None

        # for 0-layer - inputs
        num_nods = self.layer_sizes[0]
        layer_positions = nods_positions[0]
        if len(layer_positions) > 1:
            layer_radius = get_radius(layer_positions[1][1] - layer_positions[0][1])
        else:
            layer_radius = desired_radius

        for i in range(num_nods):
            self.circle_buttons.append(CircleButton(
                layer_positions[i],
                layer_radius,
                self.inputs,
                i,
                self.max_values.get(0, 'b') ))
            
        # for other layers
        for index, layer in enumerate(self.layers):
            num_nods = self.layer_sizes[index+1]
            layer_positions = nods_positions[index+1]
            
            if len(layer_positions) > 1:
                layer_radius = get_radius(layer_positions[1][1] - layer_positions[0][1])
            else:
                layer_radius = desired_radius

            for k, prev_nod_pos in enumerate(nods_positions[index]):  # previous_nods_positions
                for j in range(num_nods):
                    self.line_buttons.append(LineButton(
                        prev_nod_pos,
                        layer_positions[j],
                        2,
                        layer,
                        (j, k),
                        self.max_values.get(index+1, 'w') ))

            for i in range(num_nods):
                self.circle_buttons.append(CircleButton(
                    layer_positions[i],
                    layer_radius,
                    layer,
                    i,
                    self.max_values.get(index+1, 'b') ))
                
    def update_max_values(self, output_max: float=None) -> None:
        self.max_values.update(self, output_max)
        
    def draw(self, screen: py.Surface) -> None:
        for lb in self.line_buttons:
            lb.draw(screen)
        for cb in self.circle_buttons:
            cb.draw(screen)
        if self.board != None:
            self.board.draw(screen)
            
    def is_clicked(self, point_pos) -> bool:
        for cb in self.circle_buttons:
            if cb.is_point_inside(point_pos):
                cb.click()
                self.board = Board((10, 10), cb.get_board_args())
                return True
                
        for lb in self.line_buttons:
            if lb.is_point_inside(point_pos):
                lb.click()
                self.board = Board((10, 10), lb.get_board_args())
                self.line_buttons.remove(lb)
                self.line_buttons.append(lb)
                return True
            
        # if nothing clicked
        for b in Button.pressed_buttons:
            b.release()
        self.board = None
        return False
        

def gradient_descent(network: NeuralNetwork, training_inputs: ndarray, expected_outputs: ndarray, 
                     epochs: int, Learning_rate: float=0.01, mini_batch_size: int=None, 
                     test_inputs: ndarray=None, test_outputs: ndarray=None, logs: bool=False) -> None:
    
    if mini_batch_size == None:
        mini_batches = [(0, len(training_inputs))]
    else:
        mini_batches = [( (index * mini_batch_size), min((index+1) * mini_batch_size, len(training_inputs)) ) 
                for index in range(ceil(len(training_inputs) / mini_batch_size))]
    
    for epoch in range(epochs):
        
        if logs:
            print(f'\rBatches completed: 0.0% | Epoch: {epoch}', end='')

        for num_batch, mini_batch in enumerate(mini_batches):

            start, end = mini_batch

            gradient = network.backpropagation(training_inputs[start:end], expected_outputs[start:end])

            for layer_index in range(len(network.layers)):
    
                network.parameters.weights[layer_index] -= Learning_rate * gradient.weights[layer_index]
                network.parameters.biases[layer_index] -= Learning_rate * gradient.biases[layer_index]
            
            if logs:
                line = f'\rBatches completed: {str( round(((num_batch+1) / len(mini_batches) * 100), 1) ) }% | Epoch: {epoch}'
                print(line, end='')

        if logs:
            print('\r' + (' ' * len(line)), end='')
            if test_inputs != None:
                total_error = network.cost(test_inputs, test_outputs)
                print(f'\rEpoch {epoch}, Error: {total_error}')
    
    if logs:
        print('\r', end='')
            
def gradient_descent_adam_optimization(network: NeuralNetwork, training_inputs: ndarray, expected_outputs: ndarray, epochs: int,
                                       Learning_rate: float=0.01, Beta_1: float=0.9, Beta_2: float=0.999, Epsilon: float=1e-8,
                                       mini_batch_size: int=None, test_inputs: ndarray=None, test_outputs: ndarray=None, 
                                       logs: bool=False) -> None:
    
    if mini_batch_size == None:
        mini_batches = [(0, len(training_inputs))]
    else:
        mini_batches = [( (index * mini_batch_size), min((index+1) * mini_batch_size, len(training_inputs)) ) 
                for index in range(ceil(len(training_inputs) / mini_batch_size))]
    
    # Momentums

    V_t = NeuralNetwork.Parameters.zeros(network.layer_sizes)
    S_t = NeuralNetwork.Parameters.zeros(network.layer_sizes)

    V_corr = NeuralNetwork.Parameters.zeros(network.layer_sizes)
    S_corr = NeuralNetwork.Parameters.zeros(network.layer_sizes)

    t = 1

    for epoch in range(epochs):

        if logs:
            print(f'\rBatches completed: 0.0% | Epoch: {epoch}', end='')

        for num_batch, mini_batch in enumerate(mini_batches):

            start, end = mini_batch

            gradient = network.backpropagation(training_inputs[start:end], expected_outputs[start:end])
    
            Beta_1t = Beta_1 ** t
            Beta_2t = Beta_2 ** t

            for layer_index in range(len(network.layers)):
            
                V_t.weights[layer_index] = Beta_1 * V_t.weights[layer_index] + (1 - Beta_1) * gradient.weights[layer_index]
                V_t.biases[layer_index] = Beta_1 * V_t.biases[layer_index] + (1 - Beta_1) * gradient.biases[layer_index]
    
                S_t.weights[layer_index] = Beta_2 * S_t.weights[layer_index] + (1 - Beta_2) * (gradient.weights[layer_index] ** 2)
                S_t.biases[layer_index] = Beta_2 * S_t.biases[layer_index] + (1 - Beta_2) * (gradient.biases[layer_index] ** 2)
            
                V_corr.weights[layer_index] = V_t.weights[layer_index] / (1 - Beta_1t)
                V_corr.biases[layer_index] = V_t.biases[layer_index] / (1 - Beta_1t)
    
                S_corr.weights[layer_index] = S_t.weights[layer_index] / (1 - Beta_2t)
                S_corr.biases[layer_index] = S_t.biases[layer_index] / (1 - Beta_2t)
    
                network.parameters.weights[layer_index] -= Learning_rate * ( V_corr.weights[layer_index] 
                                                                            / (np.sqrt(S_corr.weights[layer_index]) + Epsilon ) )
                network.parameters.biases[layer_index] -= Learning_rate * ( V_corr.biases[layer_index] 
                                                                           / (np.sqrt(S_corr.biases[layer_index]) + Epsilon ) )
            if logs:
                line = f'\rBatches completed: {str( round(((num_batch+1) / len(mini_batches) * 100), 1) ) }% | Epoch: {epoch}'
                print(line, end='')
            t += 1

        if logs:
            print('\r' + (' ' * len(line)), end='')
            if test_inputs != None:
                total_error = network.cost(test_inputs, test_outputs)
                print(f'\rEpoch {epoch}, Error: {total_error}')
            
    if logs:
        print('\r', end='')
