from __future__ import annotations


class Point:
    EPSILON = 10**-12

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __repr__(self) -> str:
        return f"Point({self.x}, {self.y})"

    def distance(self, other: Point) -> float:
        return ((other.x - self.x) ** 2 + (other.y - self.y) ** 2) ** 0.5

    def as_tuple(self) -> tuple[float, float]:
        return (self.x, self.y)

    # TODO: Hash wouldn't work with floats + eps.
    # def __hash__(self) -> int:
    #     return hash((self.x, self.y))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Point):
            return NotImplemented
        return self.distance(other) < self.EPSILON

    @staticmethod
    def as_points(Q: list[tuple[float, float]]) -> list[Point]:
        points = []
        for x, y in Q:
            points.append(Point(x, y))
        return points

    @staticmethod
    def as_tuples(points: list[Point]) -> list[tuple[float, float]]:
        tuples = []
        for point in points:
            tuples.append(point.as_tuple())
        return tuples

    @staticmethod
    def det(a: Point, b: Point, c: Point) -> float:
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


if __name__ == "__main__":
    pass
