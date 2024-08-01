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
