import pygame

from src.draggable import Draggable, MOUSE_DRAG_MAX_DISTANCE
from src.calcs import is_pos_in_rect, calc_distance_pos_rect


class Slide(Draggable):
    DRAG_MODE_START = 0
    DRAG_MODE_STOP = 1
    DRAG_MODE_ALL = 2

    def __init__(self, start, stop, value_count, time_series, nth_class):
        self.start = start
        self.stop = stop
        self.value_count = value_count
        self.time_series = time_series
        self.start_pos = None
        self.start_start = None
        self.start_stop = None
        self.drag_status = None
        self.nth_class = nth_class

    def get_rect(self):
        l1 = min(max(self.time_series.calc_left_from_idx(self.start), 0), self.time_series.size[0])
        l2 = min(max(self.time_series.calc_left_from_idx(self.stop), 0), self.time_series.size[0])
        return (
            l1,
            0,
            l2 - l1,
            self.time_series.size[1]
        )

    def get_abs_l1_l2(self):
        return (
            min(
                max(self.time_series.calc_abs_left_from_idx(self.start), self.time_series.abs_pos[0]),
                self.time_series.abs_pos[0] + self.time_series.size[0]
            ),
            min(
                max(self.time_series.calc_abs_left_from_idx(self.stop), self.time_series.abs_pos[0]),
                self.time_series.abs_pos[0] + self.time_series.size[0]
            )
        )

    def get_abs_rect(self):
        l1, l2 = self.get_abs_l1_l2()
        return (
            l1,
            self.time_series.abs_pos[1],
            l2 - l1,
            self.time_series.size[1]
        )

    def get_distance(self, pos):
        return calc_distance_pos_rect(
            pos,
            self.get_abs_rect()
        )

    def is_enclosing(self, pos):
        return is_pos_in_rect(
            pos,
            self.get_abs_rect()
        )

    def start_drag(self, pos):
        l1, l2 = self.get_abs_l1_l2()
        l1_start = min(
            max(l1 - MOUSE_DRAG_MAX_DISTANCE, self.time_series.abs_pos[0]),
            self.time_series.abs_pos[0] + self.time_series.size[0]
        )
        l1_stop = min(
            max(l1 + MOUSE_DRAG_MAX_DISTANCE, self.time_series.abs_pos[0]),
            self.time_series.abs_pos[0] + self.time_series.size[0]
        )
        l2_start = min(
            max(l2 - MOUSE_DRAG_MAX_DISTANCE, self.time_series.abs_pos[0]),
            self.time_series.abs_pos[0] + self.time_series.size[0]
        )
        l2_stop = min(
            max(l2 + MOUSE_DRAG_MAX_DISTANCE, self.time_series.abs_pos[0]),
            self.time_series.abs_pos[0] + self.time_series.size[0]
        )
        if is_pos_in_rect(
            pos,
            (
                l1_start,
                self.time_series.abs_pos[0],
                l1_stop - l1_start,
                self.time_series.size[1],
            )
        ):
            self.drag_status = self.DRAG_MODE_START
        elif is_pos_in_rect(
                pos,
                (
                    l2_start,
                    self.time_series.abs_pos[0],
                    l2_stop - l2_start,
                    self.time_series.size[1],
                )
        ):
            self.drag_status = self.DRAG_MODE_STOP
        elif self.is_enclosing(pos):
            self.drag_status = self.DRAG_MODE_ALL
            self.start_pos = pos
            self.start_start = self.start
            self.start_stop = self.stop
        else:
            self.drag_status = None

    def update_drag(self, pos):
        if self.drag_status is None:
            return False
        start_before, stop_before = self.start, self.stop
        if self.drag_status == self.DRAG_MODE_START:
            start = self.time_series.calc_idx_from_left(pos[0])
            if start == start_before:
                return False
            start = max(min(start, len(self.time_series.adj_arr) - 1), 0)
            previous_slide = self.time_series.get_previous_slide(self)
            if previous_slide is not None:
                start = max(start, previous_slide.stop)
            if start > self.stop:
                next_slide = self.time_series.get_next_slide(self)
                if next_slide is None or next_slide.start >= start:
                    self.start, self.stop = self.stop, start
                    self.drag_status = self.DRAG_MODE_STOP
                    return True
            self.start = min(start, self.stop - 1)
        elif self.drag_status == self.DRAG_MODE_STOP:
            stop = self.time_series.calc_idx_from_left(pos[0])
            if stop == stop_before:
                return False
            stop = max(min(stop, len(self.time_series.adj_arr) - 1), 0)
            next_slide = self.time_series.get_next_slide(self)
            if next_slide is not None:
                stop = min(stop, next_slide.start)
            if stop < self.start:
                previous_slide = self.time_series.get_previous_slide(self)
                if previous_slide is None or previous_slide.stop <= stop:
                    self.start, self.stop = stop, self.start
                    self.drag_status = self.DRAG_MODE_START
                    return True
            self.stop = max(stop, self.start + 1)
        else:
            offset = round((pos[0] - self.start_pos[0]) / self.time_series.between)
            if offset > 0:
                stop = max(min(self.start_stop + offset, len(self.time_series.adj_arr) - 1), 0)
                next_slide = self.time_series.get_next_slide(self)
                if next_slide is not None:
                    stop = min(stop, next_slide.start)
                self.start += stop - self.stop
                self.stop = stop
            elif offset < 0:
                start = max(min(self.start_start + offset, len(self.time_series.adj_arr) - 1), 0)
                previous_slide = self.time_series.get_previous_slide(self)
                if previous_slide is not None:
                    start = max(start, previous_slide.stop)
                self.stop += start - self.start
                self.start = start
        return self.start != start_before or self.stop != stop_before

    def blit(self):
        rect = self.get_rect()
        color = pygame.Color(self.time_series.classes_colors[self.nth_class])
        pygame.draw.rect(
            self.time_series.surface_slides,
            color,
            self.get_rect()
        )
        pygame.draw.line(
            self.time_series.surface_slides_2,
            color,
            (rect[0] + 1, rect[1]),
            (rect[0] + 1, rect[1] + rect[3]),
            2
        )
        pygame.draw.line(
            self.time_series.surface_slides_2,
            color,
            (rect[0] + rect[2] - 1, rect[1]),
            (rect[0] + rect[2] - 1, rect[1] + rect[3]),
            2
        )
