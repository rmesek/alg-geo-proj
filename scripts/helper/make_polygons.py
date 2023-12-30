from __future__ import annotations
from math import atan2, degrees
from scripts.helper.make_monotone import get_points_and_diagonals


class PolygonPoint:
    def __init__(self, x: float, y: float, id: int) -> None:
        self.x = x
        self.y = y
        self.id = id
        self.targets: list[PolygonPoint] = []

    def __repr__(self) -> str:
        return f"PolygonPoint{self.id}({self.x}, {self.y})"

    def add_target(self, target: PolygonPoint) -> None:
        self.targets.append(target)

    def remove_target(self, target: PolygonPoint) -> None:
        self.targets.remove(target)

    def as_tuple(self) -> tuple[float, float]:
        return (self.x, self.y)

    @staticmethod
    def det(a: PolygonPoint, b: PolygonPoint, c: PolygonPoint) -> float:
        """
        Orientacja punktu "c" względem prostej "a b" obliczając wyznacznik macierzy 2x2
        :param a: pierwszey punkt tworzący naszą prostą
        :param b: drugi punkt tworzący naszą prostą
        :param c: punkt, którego położenie względem prostej chcemy znaleźć
        :return: wartość wyznacznika macierzy
                (> 0) => Counterclockwise
                (== 0) => Collinear
                (< 0) => Clockwise
        """
        return (a.x - c.x) * (b.y - c.y) - (a.y - c.y) * (b.x - c.x)

    @staticmethod
    def get_angle(a: PolygonPoint, b: PolygonPoint, c: PolygonPoint) -> float:
        ang = degrees(atan2(c.y - b.y, c.x - b.x) - atan2(a.y - b.y, a.x - b.x))
        return ang + 360 if ang < 0 else ang


def next_target(prev_point: PolygonPoint, point: PolygonPoint) -> PolygonPoint | None:
    # TODO: Improve
    targets = point.targets
    best_target = None
    for target in targets:
        if target.id == prev_point.id:
            continue
        if best_target is None or PolygonPoint.get_angle(prev_point, point, target) > PolygonPoint.get_angle(prev_point, point, best_target):
            best_target = target
    # if best_target is None:
    #     raise RuntimeError(f"Could not find best_target for {prev_point=} {point=} {targets=}!")
    return best_target


def walk(prev_point: PolygonPoint, point: PolygonPoint) -> list[tuple[float, float]] | None:
    polygon: list[tuple[float, float]] = [prev_point.as_tuple(), point.as_tuple()]
    if not prev_point.targets:
        return None
    prev_point.remove_target(point)
    start_point = prev_point
    while True:
        next_point = next_target(prev_point, point)
        if next_point is None:
            break
        point.remove_target(next_point)
        if next_point.id == start_point.id:
            return polygon
        polygon.append(next_point.as_tuple())
        prev_point = point
        point = next_point


def make_polygons(polygon: list[tuple[float, float]]) -> list[list[tuple[float, float]]]:
    polygons: list[list[tuple[float, float]]] = []
    points, diagonals = get_points_and_diagonals(polygon)
    # prepare points
    polygon_points = [PolygonPoint(point[0], point[1], i) for i, point in enumerate(points)]
    # add targets to the next points
    for i in range(len(polygon_points) - 1):
        polygon_points[i].add_target(polygon_points[i + 1])
    polygon_points[-1].add_target(polygon_points[0])
    # add targets through the edges
    for source_id, target_id in diagonals:
        polygon_points[source_id].add_target(polygon_points[target_id])
        polygon_points[target_id].add_target(polygon_points[source_id])
    # now polygon_points are prepared
    #
    # walk through points choosing the next point(i_n) from i.targets choosing widest angle([i-1, i], [i, i_n])
    # and remove the target from the list
    for i in range(1, len(polygon_points)):
        walk_polygon = walk(polygon_points[i - 1], polygon_points[i])
        if walk_polygon is not None:
            polygons.append(walk_polygon)
    return polygons


if __name__ == "__main__":
    polygon_example = [
        (2, 0),  # 0
        (5, 1),  # 1
        (6, 0),  # 2
        (8, 3),  # 3
        (7, 2),  # 4
        (8, 7),  # 5
        (6, 9),  # 6
        (5, 8),  # 7
        (2, 9),  # 8
        (1, 7),  # 9
        (2, 4),  # 10
        (4, 5),  # 11
        (3, 6),  # 12
        (5, 7),  # 13
        (5.5, 3),  # 14
        (2, 2),  # 15
        (1, 3),  # 16
        (0, 1),  # 17
    ]
    print(*make_polygons(polygon_example), sep="\n")
