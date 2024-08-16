from numpy import ndarray
import pygame as py
from abc import ABC, abstractmethod

py.font.init()

PALETTE_COLOR_1 = (31, 31, 31)
PALETTE_COLOR_2 = (0, 255, 128)
PALETTE_COLOR_3 = (132, 132, 132)
PALETTE_COLOR_4 = (194, 66, 178)

BACKGROUND_COLOR = PALETTE_COLOR_1

BOARD_BG_COLOR = PALETTE_COLOR_1
TEXT_COLOR = PALETTE_COLOR_3

CIRCLE_BUTTON_RELEASED_COLOR = PALETTE_COLOR_3
CIRCLE_BUTTON_PRESSED_COLOR = PALETTE_COLOR_4

LINE_BUTTON_RELEASED_COLOR = PALETTE_COLOR_2
LINE_BUTTON_PRESSED_COLOR = PALETTE_COLOR_4

class Button(ABC):
    pressed_buttons = []

    @abstractmethod
    def strengthen_color(self) -> py.Color:
        pass

    @abstractmethod
    def draw(self, screen: py.Surface) -> None:
        pass
    
    @abstractmethod
    def is_point_inside(self, point_position: tuple[int, int]) -> bool:
        pass

    @abstractmethod
    def get_board_args(self) -> tuple[float, float, float, float]:
        pass

    def click(self) -> None:
        if not self.pressed:
            self.pressed = True
            for button in self.__class__.pressed_buttons:
                button.release()
            self.__class__.pressed_buttons.append(self)

    def release(self) -> None:
        if self.pressed:
            self.pressed = False
            self.__class__.pressed_buttons.remove(self)


class CircleButton(Button):
    def __init__(self, center: tuple[int, int], radius: float, layer, index: int, max_ptr: list[float]) -> None:
        self.center = center
        self.radius = radius
        self.small_rad = radius * 0.8
        self.pressed = False
        self.layer = layer
        self.index = index
        self.max_value = max_ptr

    def strengthen_color(self) -> py.Color:
        if self.max_value[0] == 0:
            return (0,0,0)
        
        if isinstance(self.layer, ndarray):
            val = abs(self.layer[self.index] / self.max_value[0])
        else:
            val = abs(self.layer.activation_values[self.index] / self.max_value[0])
        c = round(255 * val)
        c = 255 if c > 255 else c
        return (c, c, c)

    def draw(self, screen: py.Surface) -> None:
        if self.pressed:
            py.draw.circle(screen, CIRCLE_BUTTON_PRESSED_COLOR, self.center, self.radius)
        else:
            py.draw.circle(screen, CIRCLE_BUTTON_RELEASED_COLOR, self.center, self.radius)
        py.draw.circle(screen, self.strengthen_color(), self.center, self.small_rad)
        
    def is_point_inside(self, point_position: tuple[int, int]) -> bool:
        return (point_position[0] - self.center[0]) ** 2 + (point_position[1] - self.center[1]) ** 2 <= self.radius ** 2
    
    def get_board_args(self) -> tuple[float, float, float, float]:
        if isinstance(self.layer, ndarray):
            return (None, None, None, self.layer[self.index])
        return (None,
                self.layer.biases[self.index],
                self.layer.weighted_sum_values[self.index],
                self.layer.activation_values[self.index]
            )


class LineButton(Button):
    def __init__(self, start_pos: tuple[int, int], end_pos: tuple[int, int], 
                 width: int, layer, index: tuple[int, int], max_ptr: list[float]) -> None:
        self.points = [
            ( start_pos[0], start_pos[1] - width ),
            ( start_pos[0], start_pos[1] + width ),
            ( end_pos[0], end_pos[1] + width ),
            ( end_pos[0], end_pos[1] - width )
            ]
        self.pressed = False
        self.layer = layer
        self.index = index
        self.max_value = max_ptr

    def strengthen_color(self) -> py.Color:
        if self.max_value[0] == 0:
            return LINE_BUTTON_RELEASED_COLOR
        
        val = abs(self.layer.weights[self.index[0]][self.index[1]] / self.max_value[0])
        r1, g1, b1 = LINE_BUTTON_RELEASED_COLOR
        r2, g2, b2 = BACKGROUND_COLOR
        r = r1 * val + r2 * (1 - val)
        g = g1 * val + g2 * (1 - val)
        b = b1 * val + b2 * (1 - val)
        return (round(r), round(g), round(b))

    def draw(self, screen: py.Surface) -> None:
        if self.pressed:
            py.draw.polygon(screen, LINE_BUTTON_PRESSED_COLOR, self.points)
        else:
            py.draw.polygon(screen, self.strengthen_color(), self.points)
        
    def is_point_inside(self, point_position: tuple[int, int]) -> bool:
        
        x, y = point_position
        is_inside = False
        num_points = len(self.points)
        
        if num_points < 3:
            return False

        p1x, p1y = self.points[0]
        for index in range(1, num_points+1):
            p2x, p2y = self.points[index % num_points]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        # if side is horizontal
                        if p1y == p2y:
                            if x >= min(p1x, p2x):
                                # is on horizontal side
                                return True
                        # side is not horizontal
                        else:
                            x_intersection = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                            # is on side 
                            if abs(x - x_intersection) < 1e-9:  # float point error
                                return True
                            # intersect
                            elif x < x_intersection:
                                is_inside = not is_inside
            p1x, p1y = p2x, p2y
        
        return is_inside
    
    def get_board_args(self) -> tuple[float, float, float, float]:
        return (self.layer.weights[self.index[0]][self.index[1]], None, None, None)


class Board:
    font = py.font.Font(None, 36)  # font_size

    def __init__(self, position: tuple[int, int], args: tuple[float, float, float, float]) -> None:
        
        weight, bias, z, a = args
        
        if weight != None:
            text = 'w: ' + str(weight)
        elif bias != None:
            text = 'b: ' + str(bias) + '\n\n'
            text += 'z: ' + str(z) + '\n'
            text += 'a: ' + str(a)
        elif a != None:
            text = 'a: ' + str(a)
            
        text = text.split('\n')
        
        self.text_surfaces = [self.__class__.font.render(part, True, TEXT_COLOR) for part in text]
        self.text_rects = [sur.get_rect() for sur in self.text_surfaces]
        for i in range(len(self.text_rects)):
            self.text_rects[i].topleft = (position[0] + 20, position[1] + 20 + i * self.text_rects[0].height)
            
        self.bg_rect = py.Rect(position[0] + 5, position[1] + 5, 
                               30 + max([el.width for el in self.text_rects]), 
                               30 + self.text_rects[0].height * len(self.text_rects))

        self.border_rect = py.Rect(position[0], position[1], 
                               40 + max([el.width for el in self.text_rects]), 
                               40 + self.text_rects[0].height * len(self.text_rects))

    def draw(self, screen: py.Surface) -> None:
        py.draw.rect(screen, TEXT_COLOR, self.border_rect, 0, 5)
        py.draw.rect(screen, BOARD_BG_COLOR, self.bg_rect, 0, 5)
        for sur, rect in zip(self.text_surfaces, self.text_rects):
            screen.blit(sur, rect)


class Canvas:
    def __init__(self, position: tuple[int, int], size: tuple[int, int], brush_size: int,
                 bg_color: tuple[int, int, int]=(0,0,0), brush_color: tuple[int, int, int]=(255,255,255)):
        self.position = position
        self.size = size
        self.brush_size = brush_size
        self.bg_color = bg_color
        self.brush_color = brush_color
        
        self.canvas = py.Surface(size)
        self.canvas.fill(self.bg_color)
        
        self.last_pos = None
        
    def is_point_inside(self, point_pos: tuple[int, int]) -> bool:
        x, y = point_pos
        if x < self.position[0] or x >= self.position[0] + self.size[0]:
            return False
        if y < self.position[1] or y >= self.position[1] + self.size[1]:
            return False
        return True

    def draw(self, screen: py.Surface) -> None:
        screen.blit(self.canvas, self.position)
        
    def canvas_draw(self, point_pos: tuple[int, int]) -> None:
        relative_pos = (point_pos[0] - self.position[0], point_pos[1] - self.position[1])
        
        if self.last_pos != None:
            py.draw.line(self.canvas, self.brush_color, self.last_pos, relative_pos, self.brush_size)
        
        self.last_pos = relative_pos
        
    def canvas_erase(self, point_pos: tuple[int, int]) -> None:
        relative_pos = (point_pos[0] - self.position[0], point_pos[1] - self.position[1])
        
        if self.last_pos != None:
            py.draw.line(self.canvas, self.bg_color, self.last_pos, relative_pos, self.brush_size)
        
        self.last_pos = relative_pos

    def set_last_pos(self, pos: tuple[int, int]) -> None:
        self.last_pos = (pos[0] - self.position[0], pos[1] - self.position[1])


class MaxValues:
    def __init__(self, NeuralNetwork):
        self.max_values = [([0.0], [0.0]) for n in range(len(NeuralNetwork.layer_sizes))]

    def update(self, NeuralNetwork, output_max: float=None) -> None:
        for index, layer_maxs in enumerate(self.max_values):
            if index == 0:
                layer_maxs[1][0] = max(NeuralNetwork.inputs, key=abs)
            else:
                layer_maxs[0][0] = max([max(arr, key=abs) for arr in NeuralNetwork.layers[index-1].weights], key=abs)
                layer_maxs[1][0] = max(NeuralNetwork.layers[index-1].activation_values, key=abs)
        if output_max != None:
            layer_maxs[1][0] = output_max

    def get(self, layer: int, parameter: str) -> list[float]:
        return self.max_values[layer][0] if parameter == 'w' else self.max_values[layer][1]
