import math
import pygame
import json

from src.slide import Slide


class TimeSeries:
    def __init__(self, size, abs_pos, between, arr, hor_bar, slides, classes_colors):
        self.size = size
        self.abs_pos = abs_pos
        self.values_stop_offset = (size[0] // between) + 2
        self.max_x_offset = max((len(arr) - (size[0] // between) - 1) * between, 0)
        self.surface = pygame.Surface(size)
        self.surface_slides = pygame.Surface(size, pygame.SRCALPHA)
        self.surface_slides.set_alpha(round(0.2 * 255))
        self.surface_slides_2 = pygame.Surface(size, pygame.SRCALPHA)
        self.surface_slides_2.set_alpha(round(0.3 * 255))
        self.adj_arr = arr = arr - arr.min()
        self.adj_arr = (arr / arr.max()) * size[1]
        self.adj_arr = self.size[1] - self.adj_arr
        self.hor_bar = hor_bar
        self.between = between
        self.slides = slides or []
        self.update_x_offset()
        self.classes_colors = classes_colors

    def calc_left_from_idx(self, idx):
        return idx * self.between - self.x_offset

    def calc_abs_left_from_idx(self, idx):
        return self.abs_pos[0] + idx * self.between - self.x_offset

    def update_x_offset(self):
        self.x_offset = (self.hor_bar.slider_offset / self.hor_bar.hor_bar_max_offset) * self.max_x_offset \
            if self.hor_bar.hor_bar_max_offset else 0

    def calc_idx_from_left(self, left, adj_func=round):
        return adj_func((left + self.x_offset) / self.between)

    def calc_idx_from_left_not_round(self, left):
        return (left + self.x_offset) / self.between

    def blit(self, screen):
        self.surface.fill((23, 27, 33))
        self.update_x_offset()
        start = math.floor(self.x_offset / self.between)
        stop = min(start + self.values_stop_offset, len(self.adj_arr))
        adj_arr = self.adj_arr[start : stop]
        pygame.draw.circle(
            self.surface,
            pygame.Color('red'),
            (self.calc_left_from_idx(start), adj_arr[0]),
            5
        )
        for i, t1, t2 in zip(
            range(start, stop - 1),
            adj_arr[:-1],
            adj_arr[1:]
        ):
            pygame.draw.line(
                self.surface,
                pygame.Color('red'),
                (self.calc_left_from_idx(i), t1),
                (self.calc_left_from_idx(i + 1), t2),
                2
            )
            pygame.draw.circle(
                self.surface,
                pygame.Color('red'),
                (self.calc_left_from_idx(i + 1), t2),
                5
            )
        self.surface_slides.fill((0, 0, 0, 0))
        self.surface_slides_2.fill((0, 0, 0, 0))
        for slide in self.slides:
            slide.blit()
        self.surface.blit(self.surface_slides, (0, 0))
        self.surface.blit(self.surface_slides_2, (0, 0))
        screen.blit(self.surface, self.abs_pos)

    def get_previous_slide(self, slide):
        i = self.slides.index(slide)
        if i:
            return self.slides[i - 1]

    def get_next_slide(self, slide):
        i = self.slides.index(slide)
        if i + 1 < len(self.slides):
            return self.slides[i + 1]

    def add_slide(self):
        i = self.calc_idx_from_left(pygame.mouse.get_pos()[0], math.floor)
        try:
            next(slide for slide in self.slides if slide.start <= i < slide.stop)
            return
        except StopIteration:
            pass
        try:
            next_slide = next(slide for slide in self.slides if slide.start > i)
        except StopIteration:
            next_slide = None
        try:
            previous_slide = next(slide for slide in self.slides[::-1] if i >= slide.stop)
        except StopIteration:
            previous_slide = None
        if (
            previous_slide is None
            or next_slide is None
            or previous_slide.stop != next_slide.start
        ):
            slide = Slide(i, i + 1, len(self.adj_arr), self, 0)
            if next_slide is None:
                self.slides.append(slide)
            else:
                self.slides.insert(self.slides.index(next_slide), slide)
            slide.drag_status = Slide.DRAG_MODE_STOP
            return slide


    def rm_slide(self):
        i = self.calc_idx_from_left_not_round(pygame.mouse.get_pos()[0])
        try:
            slide = next(slide for slide in self.slides if slide.start <= i <= slide.stop)
        except StopIteration:
            return
        self.slides.remove(slide)
        return slide

    def next_slide_class(self):
        i = self.calc_idx_from_left_not_round(pygame.mouse.get_pos()[0])
        try:
            slide = next(slide for slide in self.slides if slide.start <= i <= slide.stop)
        except StopIteration:
            return
        slide.nth_class = (slide.nth_class + 1) % len(self.classes_colors)
        return slide

    def save_indices(self, path):
        with open(path, 'w') as f:
            json.dump(
                list(map(lambda slide: (slide.start, slide.stop), self.slides)),
                f
            )
