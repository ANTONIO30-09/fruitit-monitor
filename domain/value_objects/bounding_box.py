import math
from dataclasses import dataclass

@dataclass(frozen=True)
class BoundingBox:
    x1: float
    y1: float
    x2: float
    y2: float

    def width(self) -> float:
        return max(0.0, self.x2 - self.x1)

    def height(self) -> float:
        return max(0.0, self.y2 - self.y1)

    def center(self) -> tuple[float, float]:
        return ((self.x1 + self.x2) / 2, (self.y1 + self.y2) / 2)

    def distance_to(self, other: "BoundingBox") -> float:
        cx1, cy1 = self.center()
        cx2, cy2 = other.center()
        return max(1.0, math.hypot(cx2 - cx1, cy2 - cy1))

    def area(self) -> float:
        return self.width() * self.height()

    def intersection_area(self, other: "BoundingBox") -> float:
        x1 = max(self.x1, other.x1)
        y1 = max(self.y1, other.y1)
        x2 = min(self.x2, other.x2)
        y2 = min(self.y2, other.y2)
        return max(0.0, x2 - x1) * max(0.0, y2 - y1)

    def overlap_ratio(self, other: "BoundingBox") -> float:
        a = self.area()
        return 0.0 if a == 0 else self.intersection_area(other) / a
