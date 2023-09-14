from enum import Enum
from dataclasses import dataclass

class RingColor(Enum):
    YELLOW = 1
    RED = 2
    NONE = 3

@dataclass
class Ring:
    height: int
    x: int
    distance: int
    area: int
    color: RingColor