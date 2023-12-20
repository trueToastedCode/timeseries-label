import pygame

from src.draggable import Draggable
from src.calcs import is_pos_in_rect, calc_distance_pos_rect


class HorBar(Draggable):
    def __init__(self, size, abs_pos, get_between, value_count):
        self.size = size
        self.last_pos = None
        self.surface = pygame.Surface(size)
        self.abs_pos = abs_pos
        self.slider_offset = 0
        self.get_between = get_between
        self.value_count = value_count
        self.hor_bar_slider_size = None
        self.hor_bar_max_offset = None
        self.update_between()

    def update_between(self):
        self.hor_bar_slider_size = \
            min((((self.size[0] // self.get_between()) + 1) / self.value_count) * self.size[0], self.size[0]), \
                self.size[1]
        self.hor_bar_max_offset = max(self.size[0] - self.hor_bar_slider_size[0], 0)
        self.slider_offset = min(self.slider_offset, self.hor_bar_max_offset)

    def get_rect(self):
        return self.slider_offset, 0, *self.hor_bar_slider_size

    def get_abs_rect(self):
        return self.abs_pos[0] + self.slider_offset, self.abs_pos[1], *self.hor_bar_slider_size

    def get_distance(self, pos):
        return calc_distance_pos_rect(
            pos,
            self.get_abs_rect()
        )

    def is_enclosing(self, pos):
        return is_pos_in_rect(pos, self.get_abs_rect())

    def start_drag(self, pos):
        self.last_pos = pos

    def update_drag(self, pos):
        if self.last_pos is None:
            return False
        slider_offset = min(max(self.slider_offset + (pos[0] - self.last_pos[0]), 0), self.hor_bar_max_offset)
        self.last_pos = pos
        if slider_offset == self.slider_offset:
            return False
        self.slider_offset = slider_offset
        return True

    def blit(self, screen):
        self.surface.fill((14, 17, 22))
        pygame.draw.rect(
            self.surface,
            pygame.Color((34, 38, 44)),
            self.get_rect()
        )
        screen.blit(self.surface, self.abs_pos)
