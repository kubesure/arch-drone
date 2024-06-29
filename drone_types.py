from enum import Enum
from dataclasses import dataclass
import numpy as np
import queue
from typing import Dict, Union


# Define a constant for 30 frames per second
FPS30 = 30


class RingColor(Enum):
    """
    Enum class to represent the color of the ring.

    Attributes:
    YELLOW (int): Represents a yellow ring.
    RED (int): Represents a red ring.
    NONE (int): Represents no ring.
    """
    YELLOW = 1
    RED = 2
    NONE = 3


@dataclass
class Ring:
    """
    Dataclass to represent a ring's properties.

    Attributes:
    y (int): The y-coordinate of the ring.
    x (int): The x-coordinate of the ring.
    z (int): The z-coordinate (depth) of the ring.
    area (int): The area of the ring.
    color (RingColor): The color of the ring.
    """
    y: int
    x: int
    z: int
    area: int
    color: RingColor


class Direction(Enum):
    """
    Enum class to represent the possible directions the drone can move.

    Attributes:
    UP (int): Represents upward movement.
    DOWN (int): Represents downward movement.
    RIGHT (int): Represents rightward movement.
    LEFT (int): Represents leftward movement.
    HOVER (int): Represents hovering in place.
    FORWARD (int): Represents forward movement.
    BACKWARD (int): Represents backward movement.
    CENTER (int): Represents centering movement.
    STOP (int): Represents stopping all movement.
    """
    UP = 1
    DOWN = 2
    RIGHT = 3
    LEFT = 4
    HOVER = 5
    FORWARD = 6
    BACKWARD = 7
    CENTER = 8
    STOP = 9


@dataclass
class RingDataContour:
    """
    Dataclass to store contour data for rings.

    Attributes:
    red_mask (np.ndarray): Mask for detecting red rings.
    red_contour (list[np.ndarray]): List of contours for red rings.
    yellow_mask (np.ndarray): Mask for detecting yellow rings.
    yellow_contour (list[np.ndarray]): List of contours for yellow rings.
    """
    red_mask: np.ndarray
    red_contour: list[np.ndarray]
    yellow_mask: np.ndarray
    yellow_contour: list[np.ndarray]


@dataclass
class DroneState:
    """
    Dataclass to represent the current state of the drone.

    Attributes:
    current_x (int): Current x-coordinate of the drone.
    current_y (int): Current y-coordinate of the drone.
    current_z (int): Current z-coordinate of the drone.
    last_ring_passed (Ring): The last ring the drone passed.
    """
    current_x: int
    current_y: int
    current_z: int
    last_ring_passed: Ring


@dataclass
class NavigatorInput:
    """
    Dataclass to represent input parameters for the drone navigator.

    Attributes:
    ring_color (RingColor): The color of the ring to navigate towards.
    q (queue.Queue): Queue for is to communicate across threads.
    duration (int): Duration for the navigation task.
    last_ring_navigated (Ring): The last ring the drone navigated.
    ring_position (int): The position of the ring in the sequence.
    """
    ring_color: RingColor
    q: queue.Queue
    duration: int
    last_ring_navigated: Ring
    ring_position: int


class DroneErrorCode(Enum):
    """
    Enum class to represent possible error codes for the drone.

    Attributes:
    InternalError (int): Represents an internal error.
    TakeOffError (int): Represents an error during takeoff.
    HoverError (int): Represents an error during hovering.
    MoveForwardError (int): Represents an error during forward movement.
    WriterError (int): Represents an error related to data writing.
    """
    InternalError = 1
    TakeOffError = 2
    HoverError = 3
    MoveForwardError = 4
    WriterError = 5
