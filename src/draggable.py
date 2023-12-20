import itertools
import pygame

MOUSE_DRAG_MAX_DISTANCE = 10


class Draggable:
    def get_distance(self, pos) -> float:
        raise NotImplemented

    def is_enclosing(self, pos) -> bool:
        raise NotImplemented

    def start_drag(self, pos):
        raise NotImplemented

    def update_drag(self, pos) -> bool:
        raise NotImplemented


def start_mouse_drag(*targets):
    pos = pygame.mouse.get_pos()
    targets = list(filter(
        lambda target: target.is_enclosing(pos) or target.get_distance(pos) <= MOUSE_DRAG_MAX_DISTANCE,
        itertools.chain.from_iterable(targets)
    ))
    if not targets:
        return
    try:
        target = next(target for target in targets if target.is_enclosing(pos))
    except StopIteration:
        target = min(
            map(lambda target: (target.get_distance(pos), target), targets),
            key=lambda x: x[0]
        )[1]
    target.start_drag(pos)
    return target
