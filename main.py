import pygame
import numpy as np
from src.hor_bar import HorBar
from src.draggable import start_mouse_drag
from src.time_series import TimeSeries

arr = np.load('arr.npy')
classes_colors = list(map(pygame.Color, ['red', 'blue']))
save_file = 'indices.json'


SIZE = 600, 250
HOR_BAR_SIZE = SIZE[0], 30
HOR_BAR_POS = 0, SIZE[1] - HOR_BAR_SIZE[1]
TIME_SERIES_SIZE = SIZE[0], SIZE[1] - HOR_BAR_SIZE[1]
TIME_SERIES_POS = 0, 0
BETWEEN = 50
MOUSE_DRAG_MAX_DISTANCE = 18


if __name__ == '__main__':
    screen = pygame.display.set_mode(SIZE)
    running = True
    need_update = True
    mouse_drag_target = None

    hor_bar = HorBar(HOR_BAR_SIZE, HOR_BAR_POS, BETWEEN, len(arr))
    time_series = TimeSeries(TIME_SERIES_SIZE, TIME_SERIES_POS, BETWEEN, arr, hor_bar, None, classes_colors)

    while running:
        for event in pygame.event.get():
            keys = pygame.key.get_pressed()
            match event.type:
                case pygame.QUIT:
                    running = False
                case pygame.MOUSEBUTTONDOWN:
                    key_detected = False
                    if mouse_drag_target is None:
                        if keys[pygame.K_d]:
                            need_update = need_update or time_series.rm_slide() is not None
                            key_detected = True
                        elif keys[pygame.K_n]:
                            need_update = need_update or time_series.next_slide_class() is not None
                            key_detected = True
                    if not key_detected:
                        if mouse_drag_target is None:
                            mouse_drag_target = start_mouse_drag((hor_bar,), time_series.slides)
                        if mouse_drag_target is None:
                            mouse_drag_target = time_series.add_slide()
                            need_update = need_update or mouse_drag_target is not None
                case pygame.MOUSEBUTTONUP:
                    mouse_drag_target = None
                case pygame.KEYDOWN:
                    if keys[pygame.K_s]:
                        time_series.save_indices(save_file)

        if mouse_drag_target is not None:
            need_update = need_update or mouse_drag_target.update_drag(pygame.mouse.get_pos())

        if not need_update:
            continue

        screen.fill((23, 27, 33))
        hor_bar.blit(screen)
        time_series.blit(screen)
        pygame.display.flip()
        need_update = False

    pygame.quit()
    time_series.save_indices(save_file)
