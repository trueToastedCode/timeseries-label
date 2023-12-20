import math


def is_pos_in_rect(pos, rect):
    return (
        rect[0] <= pos[0] <= rect[0] + rect[2]
        and rect[1] <= pos[1] <= rect[1] + rect[3]
    )


def calc_rect_center(rect):
    return rect[0] + rect[2] / 2, rect[1] + rect[3] / 2


def calc_pos_distance(pos_a, pos_b):
    return math.sqrt(math.pow(pos_b[0] - pos_a[0], 2) + math.pow(pos_b[1] - pos_a[1], 2))


def calc_distance_pos_rect(pos, rect):
    if is_pos_in_rect(pos, rect):
        return 0
    center = calc_rect_center(rect)
    if pos[0] == center[0]:
        return abs(pos[1] - center[1]) - abs(rect[1] - center[1])
    slope = (pos[1] - center[1]) / (pos[0] - center[0])
    if not slope:
        return abs(pos[0] - center[0]) - abs(rect[0] - center[0])
    intercept = center[1] - (slope * center[0])
    x1 = rect[0]
    y1 = slope * x1 + intercept
    if rect[1] <= y1 <= rect[1] + rect[3]:
        x2 = rect[0] + rect[2]
        y2 = slope * x2 + intercept
        return min(
            calc_pos_distance((x1, y1), pos),
            calc_pos_distance((x2, y2), pos)
        )
    y3 = rect[1]
    x3 = (y3 - intercept) / slope
    y4 = rect[1] + rect[3]
    x4 = (y4 - intercept) / slope
    return min(
        calc_pos_distance((x3, y3), pos),
        calc_pos_distance((x4, y4), pos)
    )
