import pygame as py


# Transforms hex-color into a tuple
def color(hex_color: str) -> tuple[int, ...]:
    hex_color = hex_color.lstrip('#')  # Remove '#' if present
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


# A line of text that functions as a button
class Button:
    def __init__(self, button_text: str, button_font: py.font.Font, x: float, y: float, screen: py.Surface,
                 onclick_func) -> None:
        self.text = button_text
        self.font = button_font
        self.screen = screen
        self.x = x
        self.y = y
        self.fillColors = {
            'normal': color("F9C74F"),
            'hover': color("F8961E"),
            'pressed': color("F3722C"),
        }
        self.surface = self.font.render(self.text, True, self.fillColors['normal'])
        self.rect = self.surface.get_rect(center=(self.screen.get_width() * self.x, self.screen.get_height() * self.y))
        self.pressed = False
        self.hovered = False
        self.onclick_func = onclick_func

    def process(self) -> None:
        mouse_pos = py.mouse.get_pos()
        self.set_text_color("normal")
        if self.rect.collidepoint(mouse_pos):
            if not py.mouse.get_pressed(num_buttons=3)[0]:
                self.hovered = True
            self.set_text_color("hover")
            if py.mouse.get_pressed(num_buttons=3)[0] and self.hovered:
                self.set_text_color("pressed")
                if not self.pressed:
                    self.onclick_func()
                    self.pressed = True
            else:
                self.pressed = False
        else:
            self.hovered = False
        self.screen.blit(self.surface, self.rect)

    def set_text_color(self, color_mode: str) -> None:
        self.surface = self.font.render(self.text, True, self.fillColors[color_mode])
        self.rect = self.surface.get_rect(center=(self.screen.get_width() * self.x, self.screen.get_height() * self.y))

    def set_font(self, new_font: py.font.Font) -> None:
        self.font = new_font


class Graph:
    def __init__(self, size, x, y, width, height, capacity, step):
        self.size = int(size)
        self.data = []
        for i in range(size):
            self.data.append([])
        self.x = int(x)
        self.y = int(y)
        self.width = int(width)
        self.height = int(height)
        self.capacity = int(capacity)
        self.step = int(step)
        self.colors = [color("F8793A"), color("8BB964")]

    def add_data(self, *args: float):
        if len(args) != self.size:
            print("Wrong number of arguments")
        else:
            for i in range(len(self.data)):
                self.data[i].append(args[i])
            while len(self.data[0]) > self.capacity:
                for data in self.data:
                    data.pop(0)

    def draw(self, screen: py.Surface) -> None:
        py.draw.line(screen, (255, 255, 255), (self.x, self.y), (self.x, self.y + self.height), 3)
        py.draw.line(screen, (255, 255, 255), (self.x, self.y + self.height), (self.x + self.width, self.y + self.height), 3)
        for i in range(len(self.data)):
            for j in range(len(self.data[i]) - 1):
                py.draw.line(screen, self.colors[i], (self.x + j * self.step, self.y + self.height - self.data[i][j] * 3), (self.x + (j + 1) * self.step, self.y + self.height - self.data[i][j+1] * 3), 3)
