from __future__ import annotations
import heapq
from enum import Enum
from scripts.helper.utils import Point


class PointType(Enum):
    UNKNOWN = -1
    STARTING = 0
    CLOSING = 1
    CONNECTIVE = 2
    SEPARATIVE = 3
    CORRECT = 4


class ColorPoint(Point):
    def __init__(self, x: float, y: float, type: PointType = PointType.UNKNOWN):
        super().__init__(x, y)
        self.type = type

    def __repr__(self) -> str:
        return f"Point({self.type.name}: {self.x}, {self.y})"

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, Point):
            return NotImplemented
        if abs(self.y - other.y) < self.EPSILON:
            return self.x > other.x
        return self.y < other.y

    @staticmethod
    def classify(a: Point, b: Point, c: Point, eps=Point.EPSILON) -> PointType:
        # starting or separative or correct
        if a.y < b.y and c.y < b.y:
            if Point.det(a, b, c) > eps:
                return PointType.STARTING
            elif Point.det(a, b, c) < -eps:
                return PointType.SEPARATIVE
        # closing or connective or correct
        elif a.y > b.y and c.y > b.y:
            if Point.det(a, b, c) > eps:
                return PointType.CLOSING
            elif Point.det(a, b, c) < -eps:
                return PointType.CONNECTIVE
        else:
            return PointType.CORRECT
        raise RuntimeError(f"Cannot classify {a, b, c}!")

    @staticmethod
    def color_points(points: list[Point]) -> list[ColorPoint]:
        colored_points = []

        for i in range(0, len(points) - 1):
            type = ColorPoint.classify(points[i - 1], points[i], points[i + 1])
            color_point = ColorPoint(points[i].x, points[i].y, type)
            colored_points.append(color_point)

        type = ColorPoint.classify(points[-2], points[-1], points[0])
        color_point = ColorPoint(points[-1].x, points[-1].y, type)
        colored_points.append(color_point)

        return colored_points


if __name__ == "__main__":
    polygon_example = [
        (2, 0),
        (5, 1),
        (6, 0),
        (8, 3),
        (7, 2),
        (8, 7),
        (6, 9),
        (5, 8),
        (2, 9),
        (1, 7),
        (2, 4),
        (4, 5),
        (3, 6),
        (5, 7),
        (5.5, 3),
        (2, 2),
        (1, 3),
        (0, 1),
    ]
    polygon_example_colors = [1, 3, 1, 0, 2, 4, 0, 2, 0, 4, 1, 4, 4, 3, 4, 2, 0, 4]

    color_points = ColorPoint.color_points(Point.as_points(polygon_example))
    print(color_points)

    # a = ColorPoint(1, 1, PointType.STARTING)
    # b = ColorPoint(2, 2)
    # c = ColorPoint(3, 2)
    # q = [a, b, c]
    # print(ColorPoint.classify(a,b,c))
    # heapq.heapify(q)
    # while q:
    #     print(heapq.heappop(q))
