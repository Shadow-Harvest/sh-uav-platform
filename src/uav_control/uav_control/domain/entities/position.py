from dataclasses import dataclass

@dataclass
class Position:
    """Represents a 3D position in space."""
    x: float
    y: float
    z: float