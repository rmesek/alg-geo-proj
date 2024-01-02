from __future__ import annotations
import heapq
from enum import Enum
from sortedcontainers import SortedList
from scripts.helper.utils import Point


class PointType(Enum):
    UNKNOWN = -1
    STARTING = 0
    CLOSING = 1
    CONNECTIVE = 2
    SEPARATIVE = 3
    CORRECT = 4


class Edge:
    line_y: float | None = None

    def __init__(self, source: ColorPoint, target: ColorPoint, helper: None | ColorPoint = None) -> None:
        self.source = source
        self.target = target
        self.helper = helper

    def __repr__(self) -> str:
        return f"Edge({self.source}->{self.target})"

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Edge):
            return NotImplemented
        return (self.source == __value.source and self.target == __value.target) or (self.source == __value.target and self.target == __value.source)

    def __gt__(self, __value: object) -> bool:
        if Edge.line_y is None:
            raise RuntimeError("Swipeline's value is not set!")
        if isinstance(__value, Edge):
            return Edge.find_sweep_intersection(self, Edge.line_y) > Edge.find_sweep_intersection(__value, Edge.line_y)
        elif isinstance(__value, float | int):
            return Edge.find_sweep_intersection(self, Edge.line_y) > __value
        return NotImplemented

    def __lt__(self, __value: object) -> bool:
        if Edge.line_y is None:
            raise RuntimeError("Swipeline's value is not set!")
        if isinstance(__value, Edge):
            return Edge.find_sweep_intersection(self, Edge.line_y) < Edge.find_sweep_intersection(__value, Edge.line_y)
        elif isinstance(__value, float | int):
            return Edge.find_sweep_intersection(self, Edge.line_y) < __value
        return NotImplemented

    @staticmethod
    def find_sweep_intersection(edge: Edge, y: float, eps: float = 10**-12) -> float:
        """https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection#Given_two_points_on_each_line"""
        x_1, y_1 = edge.source.as_tuple()
        x_2, y_2 = edge.target.as_tuple()
        denom = y_1 - y_2
        if denom == 0:
            return x_1
            raise RuntimeError(f"Could not find intersection between {edge} and {y=}")
            return None
        p_x = ((y_1 * x_2 - x_1 * y_2) + (x_1 - x_2) * y) / denom
        # p_y = ((y_1 - y_2) * y) / denom
        if not min(x_1, x_2) - eps <= p_x <= max(x_1, x_2) + eps:
            raise RuntimeError(f"Could not find intersection between {edge} and {y=}")
            return None
        return p_x

    @staticmethod
    def as_edges(points: list[ColorPoint]) -> list[Edge]:
        edges: list[Edge] = []
        for i in range(1, len(points)):
            edge = Edge(points[i - 1], points[i])
            points[i - 1].source_edge = edge
            points[i].target_edge = edge
            edges.append(edge)
        edge = Edge(points[-1], points[0])
        points[-1].source_edge = edge
        points[0].target_edge = edge
        edges.append(edge)
        return edges


class ColorPoint(Point):
    def __init__(self, x: float, y: float, id: int | None, type: PointType = PointType.UNKNOWN) -> None:
        super().__init__(x, y)
        self.id = id
        self.type = type
        self.source_edge: Edge | None = None
        self.target_edge: Edge | None = None

    def __repr__(self) -> str:
        return f"ColorPoint({self.type.name}: {self.x}, {self.y})"

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
            color_point = ColorPoint(points[i].x, points[i].y, i, type)
            colored_points.append(color_point)
        type = ColorPoint.classify(points[-2], points[-1], points[0])
        color_point = ColorPoint(points[-1].x, points[-1].y, len(points) - 1, type)
        colored_points.append(color_point)
        return colored_points


def make_monotone(polygon: list[tuple[float, float]]) -> tuple[list[Edge], list[Edge]]:
    def add_edge(D: list[Edge], source: ColorPoint, target: ColorPoint) -> None:
        edge = Edge(source, target)
        D.append(edge)

    def handle_start_vertex(T: SortedList, color_point: ColorPoint) -> None:
        edge = color_point.source_edge
        if edge is None:
            raise RuntimeError(f"Source edge for {color_point} was not set!")
        T.add(edge)
        edge.helper = color_point

    def handle_end_vertex(T: SortedList, D: list[Edge], color_point: ColorPoint) -> None:
        edge = color_point.target_edge
        if edge is None:
            raise RuntimeError(f"Target edge for {color_point} was not set!")
        if edge.helper is None:
            raise RuntimeError(f"Helper for {edge} was not set!")
        if edge.helper.type == PointType.CONNECTIVE:
            add_edge(D, color_point, edge.helper)
        T.remove(edge)

    def handle_split_vertex(T: SortedList, D: list[Edge], color_point: ColorPoint) -> None:
        edge_index = T.bisect(color_point.y) - 1
        if edge_index < 0 or edge_index > len(T) - 1:
            raise RuntimeError(f"No edge to the left of {color_point}!")
        edge: Edge = T[edge_index]  # type: ignore
        if edge.helper is None:
            raise RuntimeError(f"Helper for {edge} was not set!")
        add_edge(D, color_point, edge.helper)
        edge.helper = color_point
        if color_point.source_edge is None:
            raise RuntimeError(f"Source edge for {color_point} was not set!")
        edge = color_point.source_edge
        T.add(edge)
        edge.helper = color_point

    def handle_merge_vertex(T: SortedList, D: list[Edge], color_point: ColorPoint) -> None:
        if color_point.target_edge is None:
            raise RuntimeError(f"Target edge for {color_point} was not set!")
        edge = color_point.target_edge
        if edge.helper is None:
            raise RuntimeError(f"Helper for {edge} was not set!")
        if edge.helper.type == PointType.CONNECTIVE:
            add_edge(D, color_point, edge.helper)
        T.remove(edge)
        edge_index = T.bisect(color_point.y) - 1
        if edge_index < 0 or edge_index > len(T) - 1:
            raise RuntimeError(f"No edge to the left of {color_point}!")
        edge: Edge = T[edge_index]  # type: ignore
        if edge.helper is None:
            raise RuntimeError(f"Helper for {edge} was not set!")
        if edge.helper.type == PointType.CONNECTIVE:
            add_edge(D, color_point, edge.helper)
        edge.helper = color_point

    def handle_regular_vertex(T: SortedList, D: list[Edge], color_point: ColorPoint) -> None:
        def polygon_to_the_right(color_point: ColorPoint) -> bool:
            if color_point.target_edge is None:
                raise RuntimeError(f"Target edge for {color_point} was not set!")
            if color_point.source_edge is None:
                raise RuntimeError(f"Source edge for {color_point} was not set!")
            prev_color_point = color_point.target_edge.source
            # next_color_point = color_point.source_edge.target
            return prev_color_point.y > color_point.y

        if polygon_to_the_right(color_point):
            if color_point.target_edge is None:
                raise RuntimeError(f"Target edge for {color_point} was not set!")
            edge = color_point.target_edge
            if edge.helper is None:
                raise RuntimeError(f"Helper for {edge} was not set!")
            if edge.helper.type == PointType.CONNECTIVE:
                add_edge(D, color_point, edge.helper)
            T.remove(edge)
            T.add(color_point.source_edge)
            if color_point.source_edge is None:
                raise RuntimeError(f"Source edge for {color_point} was not set!")
            color_point.source_edge.helper = color_point
        else:
            edge_index = T.bisect(color_point.y) - 1
            if edge_index < 0 or edge_index > len(T) - 1:
                raise RuntimeError(f"No edge to the left of {color_point}!")
            edge: Edge = T[edge_index]  # type: ignore
            if edge.helper is None:
                raise RuntimeError(f"Helper for {edge} was not set!")
            if edge.helper.type == PointType.CONNECTIVE:
                add_edge(D, color_point, edge.helper)
            edge.helper = color_point

    points = Point.as_points(polygon)
    Q = ColorPoint.color_points(points)
    edges = Edge.as_edges(Q)
    new_edges: list[Edge] = []
    heapq.heapify(Q)  # event queue
    T = SortedList()  # [https://grantjenks.com/docs/sortedcontainers/sortedlist.html#sortedlist]  # sweep line status tree
    while Q:
        color_point = heapq.heappop(Q)
        Edge.line_y = color_point.y
        match color_point.type:
            case PointType.STARTING:
                handle_start_vertex(T, color_point)
            case PointType.CLOSING:
                handle_end_vertex(T, new_edges, color_point)
            case PointType.CONNECTIVE:
                handle_merge_vertex(T, new_edges, color_point)
            case PointType.SEPARATIVE:
                handle_split_vertex(T, new_edges, color_point)
            case PointType.CORRECT:
                handle_regular_vertex(T, new_edges, color_point)
            case _:
                raise RuntimeError(f"Cannot handle {color_point.type=}!")
    return edges, new_edges


def get_points_and_diagonals(polygon: list[tuple[float, float]]) -> tuple[list[tuple[float, float]], list[tuple[int, int]]]:
    points: list[tuple[float, float]] = []
    diagonals: list[tuple[int, int]] = []
    edges, new_edges = make_monotone(polygon)
    for edge in edges:
        points.append(edge.source.as_tuple())
    for new_edge in new_edges:
        if new_edge.source.id is None:
            raise RuntimeError(f"ID for {new_edge.source} is None!")
        if new_edge.target.id is None:
            raise RuntimeError(f"ID for {new_edge.target} is None!")
        diagonal = (new_edge.source.id, new_edge.target.id)
        diagonals.append(diagonal)
    return points, diagonals


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
    points, diagonals = get_points_and_diagonals(polygon_example)
    print("POINTS")
    for i, point in enumerate(points):
        print(f"{i}. {point}")
    print("DIAGONALS")
    for diagonal in diagonals:
        print(f"{diagonal[0]}. -> {diagonal[1]}.")
