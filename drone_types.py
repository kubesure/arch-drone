from enum import Enum
from dataclasses import dataclass
import numpy as np
import queue
from typing import Dict, Union


FPS30 = 30


class RingColor(Enum):
    YELLOW = 1
    RED = 2
    NONE = 3


@dataclass
class Ring:
    y: int
    x: int
    z: int
    area: int
    color: RingColor


class Direction(Enum):
    UP = 1
    DOWN = 2
    RIGHT = 3
    LEFT = 4
    HOVER = 5
    FORWARD = 6
    BACKWARD = 7
    CENTER = 8


@dataclass
class RingDataContour:
    red_mask: np.ndarray
    red_contour: list[np.ndarray]
    yellow_mask: np.ndarray
    yellow_contour: list[np.ndarray]


@dataclass
class DroneState:
    current_x: int
    current_y: int
    current_z: int
    last_ring_passed: Ring


@dataclass
class NavigatorInput:
    ring: RingColor
    config: Dict[str, Union[float, int]]
    q: queue.Queue
    duration: int


class DroneErrorCode(Enum):
    InternalError = 1
    TakeOffError = 2
    HoverError = 3
    MoveForwardError = 4




