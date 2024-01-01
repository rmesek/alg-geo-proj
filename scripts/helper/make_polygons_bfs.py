from __future__ import annotations
from collections import deque
from scripts.helper.make_monotone import get_points_and_diagonals


class PolygonPoint:
    def __init__(self, x: float, y: float, id: int) -> None:
        self.x = x
        self.y = y
        self.id = id
        self.targets: set[PolygonPoint] = set()
        self.parent: None | PolygonPoint = None

    def __repr__(self) -> str:
        return f"PolygonPoint{self.id}({self.x}, {self.y})"

    def __hash__(self) -> int:
        return self.id

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, PolygonPoint):
            return NotImplemented
        return self.id == __value.id

    def add_target(self, target: PolygonPoint) -> None:
        self.targets.add(target)

    def remove_target(self, target: PolygonPoint) -> None:
        self.targets.remove(target)

    def as_tuple(self) -> tuple[float, float]:
        return (self.x, self.y)


def walk_bfs(start_point: PolygonPoint) -> list[PolygonPoint] | None:
    # polygon: list[PolygonPoint] = []
    path_found: bool = False
    visited: set[PolygonPoint] = set([start_point])  # possible replacement with visited[p.id] = True/False
    queue: deque[PolygonPoint] = deque([start_point])
    while queue and not path_found:
        point = queue.popleft()
        for target in point.targets:
            if target not in visited:
                visited.add(target)
                queue.append(target)
                target.parent = point
            elif target == start_point and point.parent != start_point:  # ... and <sussy hack>
                target.parent = point
                path_found = True
                break
    if not path_found:
        return None
    path: list[PolygonPoint] = []
    point = start_point.parent
    while point != start_point:
        if point is None:
            raise RuntimeError("Path was broken!")
        path.append(point)
        point = point.parent
    path.append(start_point)
    path = path[::-1]
    if len(path) < 3:
        raise RuntimeError("Path < 3! How did it happen?")
    return path


def remove_targets(path: list[PolygonPoint]) -> None:
    for i, point in enumerate(path):
        path[i - 1].remove_target(point)


def path_as_tuples(path: list[PolygonPoint]) -> list[tuple[float, float]]:
    polygon = []
    for point in path:
        polygon.append(point.as_tuple())
    return polygon


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
    for i in range(len(polygon_points)):
        path = walk_bfs(polygon_points[i])
        if path is not None:
            remove_targets(path)
            polygons.append(path_as_tuples(path))
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
