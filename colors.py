from enum import Enum
from math import floor

class Colors(Enum):
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)

def lerp_color(c1: (int, int, int), c2: (int, int, int), t: float) -> (float, float, float):
    return floor((c2[0] - c1[0]) * t) + c1[0], floor((c2[1] - c1[1]) * t) + c1[1], floor((c2[2] - c1[2]) * t) + c1[2]


