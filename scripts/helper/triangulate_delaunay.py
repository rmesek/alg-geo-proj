import functools
import math
import operator

import matplotlib.pyplot as plt
import time
from queue import Queue
import matplotlib
from scripts.visualizer.main import Visualizer
from scripts.helper.draw_mouse import draw_polygon_by_clicking


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.edges = set()

    def __hash__(self):
        return hash((self.x, self.y))

    def __eq__(self, other):
        if not isinstance(other, Point):
            return False
        return self.x == other.x and self.y == other.y

    def point_to_vis(self):
        return self.x, self.y


class Half_Edge:
    def __init__(self, origin):
        self.origin = origin
        self.next = None
        self.prev = None
        self.face = None
        self.twin = None

    def __hash__(self):
        return hash((self.origin, self.twin.origin))

    def __eq__(self, other):
        if not isinstance(other, Half_Edge):
            return False
        return self.origin == other.origin and self.twin.origin == other.twin.origin

    def edge_to_vis(self):
        return self.origin.point_to_vis(), self.twin.point_to_vis()


class Triangle:
    def __init__(self, e1, e2, e3):
        self.edges = {e1, e2, e3}
        self.visited = False

    def __hash__(self):
        return functools.reduce(operator.xor, (hash(e) for e in self.edges), 1)

    def __eq__(self, other):
        if not isinstance(other, Triangle):
            return False
        if len(self.edges) != len(other.edges):
            return False
        for e in self.edges:
            if e not in other.edges:
                return False
        return True

    def triangle_to_vis(self):
        edges = list(self.edges)
        return edges[0].edge_to_vis(), edges[1].edge_to_vis(), edges[2].edge_to_vis()


def orient(edge, p):
    A = edge.origin
    B = edge.twin.origin
    res = A.x * B.y + B.x * p.y + p.x * A.y - A.y * B.x - B.y * p.x - A.x * p.y
    if abs(res) < 1e-10:
        return 0
    return res


def is_point_in_circumcircle(triangle, point):
    circle_x, circle_y, radius_squared = circumcircle(triangle)
    dx = point.x - circle_x
    dy = point.y - circle_y
    distance_squared = dx**2 + dy**2
    return radius_squared >= distance_squared


def circumcircle(triangle):
    e1, e2, e3 = triangle.edges

    x1, y1 = e1.origin.point_to_vis()
    x2, y2 = e2.origin.point_to_vis()
    x3, y3 = e3.origin.point_to_vis()

    d = 2 * (x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2))

    if abs(d) < 1e-10:
        return float("inf"), float("inf"), float("inf")

    ux = ((x1**2 + y1**2) * (y2 - y3) + (x2**2 + y2**2) * (y3 - y1) + (x3**2 + y3**2) * (y1 - y2)) / d
    uy = ((x1**2 + y1**2) * (x3 - x2) + (x2**2 + y2**2) * (x1 - x3) + (x3**2 + y3**2) * (x2 - x1)) / d

    radius_squared = (x1 - ux) ** 2 + (y1 - uy) ** 2
    return ux, uy, radius_squared


def create_edge(p1, p2, flag):
    e1 = Half_Edge(p1)
    e2 = Half_Edge(p2)
    e1.twin = e2
    e2.twin = e1
    if flag:
        p1.edges.add(e1)
        p2.edges.add(e2)
    return e1


def connect_edges(frst, scnd):
    scnd.prev = frst
    frst.next = scnd


def vis_triangulation(vis, triangles, remove):
    lines_to_add = []
    points_to_add = []

    for triangle in triangles:
        head = list(triangle.edges)[0]
        curr_edge = head

        while True:
            p1 = (curr_edge.origin.x, curr_edge.origin.y)
            p2 = (curr_edge.twin.origin.x, curr_edge.twin.origin.y)
            if (p1, p2) not in lines_to_add:
                lines_to_add.append((p1, p2))
            if p1 not in points_to_add:
                points_to_add.append(p1)

            curr_edge = curr_edge.next
            if curr_edge == head:
                break

    lines_to_r = vis.add_line_segment(lines_to_add, color="blue")
    points_to_r = vis.add_point(points_to_add, color="green")
    vis.show()
    if remove:
        vis.remove_figure(lines_to_r)
        vis.remove_figure(points_to_r)

    return vis


def if_point_in_triangle(triangle, p):
    for e in triangle.edges:
        if orient(e, p) < 0:
            return False
    return True


def get_intersecting_edge(face, p, p_next):
    p_edge, p_edge.twin = Half_Edge(p), Half_Edge(p_next)
    for edge in face.edges:
        A, B = edge.origin, edge.twin.origin
        if orient(edge, p) * orient(edge, p_next) <= 0 and orient(p_edge, A) * orient(p_edge, B) <= 0:
            return edge
    return None


class Delaunay:
    def __init__(self, T):
        self.triangulation_faces = set()
        self.Points = [Point(p[0], p[1]) for p in T]

        A, B, C, mid = self.get_super_triangle(self.Points)
        self.middle = mid
        self.starting_points = [A, B, C]
        AB = create_edge(A, B, True)
        BC = create_edge(B, C, True)
        CA = create_edge(C, A, True)
        T = [AB.twin, BC.twin, CA.twin]

        for i in range(3):
            connect_edges(T[(i + 1) % 3], T[i])

        self.middle_triangle = self.create_triangle(T)

    def get_super_triangle(self, points):
        min_x = min(p.x for p in points)
        min_y = min(p.y for p in points)
        max_x = max(p.x for p in points)
        max_y = max(p.y for p in points)

        dx = max_x - min_x
        dy = max_y - min_y
        delta = max(dx, dy)
        mid_x = (min_x + max_x) / 2
        mid_y = (min_y + max_y) / 2

        return [
            Point(mid_x - 2 * delta, mid_y - delta),
            Point(mid_x, mid_y + 2 * delta),
            Point(mid_x + 2 * delta, mid_y - delta),
            Point((max_x + min_x) / 2, (max_y + min_y) / 2),
        ]

    def create_triangle(self, edges):
        triangle = Triangle(edges[0], edges[1], edges[2])

        for i in range(3):
            edges[i].face = triangle
        self.triangulation_faces.add(triangle)

        return triangle

    def update_triangles(self, p, triangle):
        triangles_to_change = set()

        list(map(lambda f: setattr(f, "visited", False), self.triangulation_faces))

        q = Queue()
        q.put(triangle)

        while not q.empty():
            triangle = q.get()
            triangle.visited = True

            if is_point_in_circumcircle(triangle, p):
                triangles_to_change.add(triangle)
                for e in triangle.edges:
                    if e.twin.face is not None and not e.twin.face.visited:
                        q.put(e.twin.face)

        return triangles_to_change

    def execute_triangulation_update(self, faces):
        edges = set()
        firstEdge = None

        for face in faces:
            if face == self.middle_triangle:
                self.middle_triangle = None
            edges.update(face.edges)
            self.triangulation_faces.remove(face)

        while edges:
            e = edges.pop()

            if e.twin in edges:
                e.twin.prev.next = e.next
                e.next.prev = e.twin.prev
                e.twin.next.prev = e.prev
                e.prev.next = e.twin.next

                edges.remove(e.twin)

                e.origin.edges.remove(e)
                e.twin.origin.edges.remove(e.twin)

            elif e not in edges:
                firstEdge = e

        return firstEdge

    def get_triangle_in_which_the_point_is(self, p):
        triangle = self.middle_triangle
        while True:
            for e in triangle.edges:
                if orient(e, p) < 0:
                    triangle = e.twin.face
                    break
            else:
                break
        return triangle

    def add_point(self, p):
        face = self.get_triangle_in_which_the_point_is(p)

        faces = self.update_triangles(p, face)

        first_edge = self.execute_triangulation_update(faces)
        last_edge = first_edge.prev

        q = first_edge.origin
        new_edge = create_edge(p, q, True)
        new_edge.next = first_edge
        new_edge.twin.prev = last_edge
        last_edge.next = new_edge.twin
        first_edge.prev = new_edge

        curr = first_edge.next

        while curr != last_edge.next:
            q = curr.origin

            new_edge = create_edge(p, q, True)
            new_edge.next = curr
            new_edge.twin.prev = curr.prev
            new_edge.twin.next = new_edge.twin.prev.prev
            new_edge.twin.next.prev = new_edge.twin
            curr.prev.next = new_edge.twin
            curr.prev = new_edge

            new_edge_twin = new_edge.twin
            T = [new_edge_twin, new_edge_twin.next, new_edge_twin.prev]
            new_triangle = self.create_triangle(T)

            if if_point_in_triangle(new_triangle, self.middle):
                self.middle_triangle = new_triangle

            curr = curr.next

        new_edge.prev = last_edge.next
        new_edge.prev.next = new_edge
        T = [new_edge, new_edge.next, new_edge.prev]

        new_triangle = self.create_triangle(T)
        if if_point_in_triangle(new_triangle, self.middle):
            self.middle_triangle = new_triangle

    def add_points(self):
        for p in self.Points:
            self.add_point(p)

    def add_points_with_vis(self, vis):
        for p in self.Points:
            self.add_point(p)
            vis_triangulation(vis, self.triangulation_faces, True)

    def recover_the_edges(self):
        for i in range(len(self.Points)):
            p = self.Points[i]
            p_next = self.Points[(i + 1) % len(self.Points)]

            curr_tab = [1 for e in p.edges if e.twin in p_next.edges]

            if not curr_tab:
                dx = p_next.x - p.x
                dy = p_next.y - p.y

                length = dx**2 + dy**2
                accuracy = 2 * (math.floor(math.log10(length)) // 2)
                t = 10e-8 * 10 ** (-accuracy)

                first_search_point = Point(p.x + t * dx, p.y + t * dy)
                face = self.get_triangle_in_which_the_point_is(first_search_point)

                curr_tab_2 = []
                while not curr_tab_2:
                    intersect_edge = get_intersecting_edge(face, first_search_point, p_next)

                    if intersect_edge.face == self.middle_triangle or intersect_edge.twin.face == self.middle_triangle:
                        self.middle_triangle = None

                    self.triangulation_faces.remove(intersect_edge.face)
                    self.triangulation_faces.remove(intersect_edge.twin.face)

                    # delete bad edge from points
                    intersect_edge.origin.edges.remove(intersect_edge)
                    intersect_edge.twin.origin.edges.remove(intersect_edge.twin)

                    # delete bad edge from edges
                    intersect_edge.next.prev = intersect_edge.twin.prev
                    intersect_edge.prev.next = intersect_edge.twin.next
                    intersect_edge.twin.prev.next = intersect_edge.next
                    intersect_edge.twin.next.prev = intersect_edge.prev

                    # create new edge
                    e1 = create_edge(intersect_edge.prev.origin, intersect_edge.twin.prev.origin, True)
                    e1.origin.edges.add(e1)
                    e1.twin.origin.edges.add(e1.twin)

                    # update edges
                    intersect_edge.next.next = e1
                    e1.prev = intersect_edge.next
                    intersect_edge.twin.prev.prev = e1
                    e1.next = intersect_edge.twin.prev
                    intersect_edge.prev.prev = e1.twin
                    e1.twin.next = intersect_edge.prev
                    intersect_edge.twin.next.next = e1.twin
                    e1.twin.prev = intersect_edge.twin.next

                    face1 = self.create_triangle([e1, e1.next, e1.prev])
                    face2 = self.create_triangle([e1.twin, e1.twin.next, e1.twin.prev])

                    if self.middle_triangle is None:
                        if if_point_in_triangle(face1, self.middle):
                            self.middle_triangle = face1
                        else:
                            self.middle_triangle = face2

                    face = e1.face
                    if get_intersecting_edge(face, first_search_point, p_next) is None:
                        face = e1.twin.face

                    curr_tab_2 = [1 for e in p.edges if e.twin in p_next.edges]

    def recover_the_edges_with_vis(self, vis):
        for i in range(len(self.Points)):
            p = self.Points[i]
            p_next = self.Points[(i + 1) % len(self.Points)]

            curr_tab = [1 for e in p.edges if e.twin in p_next.edges]

            if not curr_tab:
                dx = p_next.x - p.x
                dy = p_next.y - p.y

                length = dx**2 + dy**2
                accuracy = 2 * (math.floor(math.log10(length)) // 2)
                t = 10e-8 * 10 ** (-accuracy)

                first_search_point = Point(p.x + t * dx, p.y + t * dy)
                face = self.get_triangle_in_which_the_point_is(first_search_point)

                curr_tab_2 = []

                while not curr_tab_2:
                    intersect_edge = get_intersecting_edge(face, first_search_point, p_next)

                    if intersect_edge.face == self.middle_triangle or intersect_edge.twin.face == self.middle_triangle:
                        self.middle_triangle = None

                    self.triangulation_faces.remove(intersect_edge.face)
                    self.triangulation_faces.remove(intersect_edge.twin.face)

                    # delete bad edge from points
                    intersect_edge.origin.edges.remove(intersect_edge)
                    intersect_edge.twin.origin.edges.remove(intersect_edge.twin)

                    # delete bad edge from edges
                    intersect_edge.next.prev = intersect_edge.twin.prev
                    intersect_edge.prev.next = intersect_edge.twin.next
                    intersect_edge.twin.prev.next = intersect_edge.next
                    intersect_edge.twin.next.prev = intersect_edge.prev

                    # create new edge
                    e1 = create_edge(intersect_edge.prev.origin, intersect_edge.twin.prev.origin, True)
                    e1.origin.edges.add(e1)
                    e1.twin.origin.edges.add(e1.twin)

                    # update edges
                    intersect_edge.next.next = e1
                    e1.prev = intersect_edge.next
                    intersect_edge.twin.prev.prev = e1
                    e1.next = intersect_edge.twin.prev
                    intersect_edge.prev.prev = e1.twin
                    e1.twin.next = intersect_edge.prev
                    intersect_edge.twin.next.next = e1.twin
                    e1.twin.prev = intersect_edge.twin.next

                    face1 = self.create_triangle([e1, e1.next, e1.prev])
                    face2 = self.create_triangle([e1.twin, e1.twin.next, e1.twin.prev])

                    if self.middle_triangle is None:
                        if if_point_in_triangle(face1, self.middle):
                            self.middle_triangle = face1
                        else:
                            self.middle_triangle = face2

                    face = e1.face
                    if get_intersecting_edge(face, first_search_point, p_next) is None:
                        face = e1.twin.face

                    curr_tab_2 = [1 for e in p.edges if e.twin in p_next.edges]

                    vis.add_line_segment(
                        ((intersect_edge.origin.x, intersect_edge.origin.y), (intersect_edge.twin.origin.x, intersect_edge.twin.origin.y)), color="red"
                    )
                    vis.add_line_segment(((e1.origin.x, e1.origin.y), (e1.twin.origin.x, e1.twin.origin.y)), color="green")
                    vis.add_line_segment(((p.x, p.y), (p_next.x, p_next.y)), color="black")
                    vis_triangulation(vis, self.triangulation_faces, True)
                    vis.clear()

    def delete_triangles_not_in_polygon(self):
        potential_suspect_edges = set()

        for i in range(len(self.Points)):
            p = self.Points[i]
            p_next = self.Points[(i + 1) % len(self.Points)]
            e = create_edge(p, p_next, False)
            potential_suspect_edges.add(e)

        point = self.Points[0]
        for f in self.triangulation_faces:
            f.visited = False
        for e in point.edges:
            if e in potential_suspect_edges:
                break

        q = Queue()
        q.put(e.face)
        while not q.empty():
            face = q.get()

            face.visited = True
            for e in face.edges:
                if e not in potential_suspect_edges and not e.twin.face.visited:
                    q.put(e.twin.face)

        AllFaces = list(self.triangulation_faces)
        for face in AllFaces:
            if not face.visited:
                # deleting triangle
                for e in face.edges:
                    e.next = None
                    e.prev = None
                    e.face = None
                self.triangulation_faces.remove(face)

    def delete_triangles_not_in_polygon_with_vis(self, vis):
        vis_triangulation(vis, self.triangulation_faces, False)
        last = None

        potential_suspect_edges = set()
        for i in range(len(self.Points)):
            p = self.Points[i]
            p_next = self.Points[(i + 1) % len(self.Points)]
            e = create_edge(p, p_next, False)
            potential_suspect_edges.add(e)

        point = self.Points[0]
        for f in self.triangulation_faces:
            f.visited = False
        for e in point.edges:
            if e in potential_suspect_edges:
                break

        edges_to_vis = [((edge.origin.x, edge.origin.y), (edge.twin.origin.x, edge.twin.origin.y)) for edge in
                        potential_suspect_edges]
        vis.add_line_segment(edges_to_vis, color="black")

        q = Queue()
        q.put(e.face)

        while not q.empty():
            face = q.get()

            for f in self.triangulation_faces:
                if f.visited:
                    pts = [[edge.origin.x, edge.origin.y] for edge in f.edges]
                    vis.add_polygon(pts, color="green")

            pts = [[edge.origin.x, edge.origin.y] for edge in face.edges]
            last = pts
            vis.add_polygon(pts, color="red")

            face.visited = True
            for e in face.edges:
                if e not in potential_suspect_edges and not e.twin.face.visited:
                    q.put(e.twin.face)

        AllFaces = list(self.triangulation_faces)
        for face in AllFaces:
            if not face.visited:
                # deleting triangle
                for e in face.edges:
                    e.next = None
                    e.prev = None
                    e.face = None
                self.triangulation_faces.remove(face)

        if last is not None:
            vis.add_polygon(last, color="green")

        vis.save_gif()

    def get_delaunay_triangulation(self, visualize):
        if visualize:
            vis = Visualizer()
            tab_points = []
            for p in self.Points:
                tab_points.append(p.point_to_vis())
            vis.add_polygon(tab_points, color="grey")
            self.add_points_with_vis(vis)
            self.recover_the_edges_with_vis(vis)

            vis_remove = Visualizer()
            self.delete_triangles_not_in_polygon_with_vis(vis_remove)
            vis_remove.clear()
            vis_triangulation(vis_remove, self.triangulation_faces, False)
            vis_remove.save()
        else:
            self.add_points()
            self.recover_the_edges()
            self.delete_triangles_not_in_polygon()
            vis = Visualizer()
            vis_triangulation(vis, self.triangulation_faces, False)
            # vis.save()

    def get_delaunay_triangulation_no_vis(self):
        self.add_points()
        self.recover_the_edges()
        self.delete_triangles_not_in_polygon()


if __name__ == "__main__":
    original_backend = matplotlib.get_backend()
    matplotlib.use("TkAgg")
    L = draw_polygon_by_clicking()
    matplotlib.use(original_backend)
    Triangulation = Delaunay(L)
    vis_polygon = Visualizer()
    vis_polygon.add_polygon(L, color="grey")
    vis_polygon.show()

    visualize = True
    Triangulation.get_delaunay_triangulation(visualize)
    s = input()
