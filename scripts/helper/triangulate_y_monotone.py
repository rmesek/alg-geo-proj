from __future__ import annotations


class Point:
    EPSILON = 10**-12

    def __init__(self, x: float, y: float, id: int):
        self.x = x
        self.y = y
        self.id = id

    def __repr__(self) -> str:
        return f"Point{self.id}({self.x}, {self.y})"

    def distance(self, other) -> float:
        return ((other.x - self.x) ** 2 + (other.y - self.y) ** 2) ** 0.5

    def as_tuple(self) -> tuple[float, float]:
        return (self.x, self.y)

    def __hash__(self) -> int:
        return hash((self.x, self.y, self.id))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Point):
            return NotImplemented
        return self.distance(other) < self.EPSILON

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, Point):
            return NotImplemented
        if abs(self.x - other.x) < self.EPSILON:
            return self.y > other.y
        return self.x > other.x

    @staticmethod
    def as_points(Q: list[tuple[float, float]]) -> list[Point]:
        points = []
        for i, (x, y) in enumerate(Q):
            points.append(Point(x, y, i))
        return points

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


def triangulate_y_monotone(polygon: list[tuple[float, float]]) -> list[tuple[tuple[float, float], tuple[float, float]]]:
    def find_chains(points: list[Point]) -> tuple[set[int], set[int]]:
        right_chain: set[int] = set()
        left_chain: set[int] = set()
        starting = max(points, key=lambda p: (p.y, -p.x)).id
        ending = min(points, key=lambda p: (p.y, -p.x)).id
        i = ending
        while i != starting:
            right_chain.add(points[i].id)
            i = (i + 1) % len(points)
        while i != ending:
            left_chain.add(points[i].id)
            i = (i + 1) % len(points)
        return left_chain, right_chain

    def check_same_chains(left_chain: set[int], right_chain: set[int], p1: Point, p2: Point) -> bool:
        if (p1.id in left_chain and p2.id in left_chain) or (p1.id in right_chain and p2.id in right_chain):
            return True
        return False

    def triangle_in_polygon(chain: set[int], a: Point, b: Point, c: Point, epsilon: float = Point.EPSILON) -> bool:
        if b.id in chain:
            return Point.det(a, b, c) > epsilon
        else:
            return Point.det(a, b, c) < -epsilon

    def check_neighbours(points: list[Point], a: Point, b: Point) -> bool:
        if abs(a.id - b.id) == 1 or abs(a.id - b.id) == len(points) - 1:
            return True
        return False

    points = Point.as_points(polygon)
    left_chain, right_chain = find_chains(points)
    points.sort(key=lambda p: (p.y, -p.x), reverse=True)
    stack = [points[0], points[1]]
    diagonals: list[tuple[tuple[float, float], tuple[float, float]]] = []
    for i in range(2, len(points)):
        if not check_same_chains(left_chain, right_chain, stack[-1], points[i]):
            while len(stack) > 0:
                p = stack.pop()
                if not check_neighbours(points, p, points[i]):
                    diagonals.append((points[i].as_tuple(), p.as_tuple()))
            stack.append(points[i - 1])
            stack.append(points[i])
        else:
            p = stack.pop()
            while len(stack) > 0 and triangle_in_polygon(left_chain, stack[-1], p, points[i]):
                if not check_neighbours(points, stack[-1], points[i]):
                    diagonals.append((points[i].as_tuple(), stack[-1].as_tuple()))
                p = stack.pop()
            stack.append(p)
            stack.append(points[i])
    return diagonals


if __name__ == "__main__":
    polygon = [
        (0.03523160349938177, -0.0065379891676061175),
        (0.0037396680155108025, 0.01637867749906055),
        (0.025884829305833385, 0.02446691279317821),
        (0.014848538983252729, 0.03794730495004095),
        (0.02767111962841403, 0.04435049122455076),
        (0.005735635757446289, 0.05210171671474684),
        (-0.04837726746836017, -0.0466421558342728),
        (0.05437726746836017, -0.0266421558342728),
        (-0.01137726746836017, -0.0166421558342728),
    ]
    print(*triangulate_y_monotone(polygon), sep="\n")
