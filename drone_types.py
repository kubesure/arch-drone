from enum import Enum
from dataclasses import dataclass
import numpy as np


class RingColor(Enum):
    YELLOW = 1
    RED = 2
    NONE = 3


class Direction(Enum):
    UP = 1
    DOWN = 2
    RIGHT = 3
    LEFT = 4    


@dataclass
class Ring:
    y: int
    x: int
    z: int
    area: int
    color: RingColor


@dataclass
class RingDataContour:
    red_mask: np.ndarray
    red_contour: list[np.ndarray]
    yellow_mask: np.ndarray
    yellow_contour: list[np.ndarray]
