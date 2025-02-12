from enum import Enum
from math import floor


class Colors(Enum):
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)


DEFAULT_GRADIENT = {
    0: Colors.GREEN.value,
    0.5: Colors.RED.value,
    1: Colors.RED.value
}


def get_gradient_value(gradient: {int: (int, int, int)}, t: float) -> (int, int, int):
    points = list(gradient.keys())
    low = points[0]
    high = points[-1]

    for point in points:
        if 0 <= t - point < t - low:
            low = point

        if 0 >= t - point > t - high:
            high = point

    return lerp_color(gradient[low], gradient[high], t - low)


def lerp_color(c1: (int, int, int), c2: (int, int, int), t: float) -> (int, int, int):
    return floor((c2[0] - c1[0]) * t) + c1[0], floor((c2[1] - c1[1]) * t) + c1[1], floor((c2[2] - c1[2]) * t) + c1[2]
