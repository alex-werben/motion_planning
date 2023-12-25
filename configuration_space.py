import json
from operator import itemgetter
from typing import List, Optional
import numpy as np
from tqdm import tqdm

from figure import Figure, Line, Trapezoid
from point import Point
from shapely import Polygon, Point, LineString, get_coordinates, GeometryCollection
import matplotlib.pyplot as plt


# Если в полигоне есть вертикальная линия, то сразу добавить ее в self.lines

class ConfigurationSpace:
    def __init__(self, min_limit, max_limit):
        self.trapezoids = []
        self.end_point_index = None           
        self.start_point_index = None
        self.end_point = None
        self.start_point = None
        self.obst = []
        self.x_limit = [min_limit, max_limit]
        self.y_limit = [min_limit, max_limit]
        self.lines = []
        self.vertices = []
        self.points = []
        self.edges = []
        self.centroids = []
        self.graph_points = []

    def parse_json(self, path: str) -> None:
        """
        Parses JSON file with obstacles and fills self.obst.

        После парсинга будет множество точек препятствий и препятствия
        """
        with open(path, 'r') as fp:
            array: List[dict] = json.load(fp)
            fp.close()
        i = 0
        for prim in array:
            if prim["type"] == "point":
                obj = Point(prim['x'], prim['y'])
                self.points.append(obj)
            elif prim["type"] == "polygon":
                obst_points = []
                for p in prim["points"]:
                    point = Point(p['x'], p['y'])
                    self.points.append(point)
                    obst_points.append(point)
                obj = Polygon(obst_points)
                self.obst.append(obj)
            elif prim["type"] == "startPoint":
                p = Point(prim['x'], prim['y'])
                # self.start_point = p
                self.centroids.append(p)
                obj = {
                    "point": p,
                    "position": "start"
                }
                self.start_point = obj
                self.graph_points.append(self.start_point["point"])
                self.start_point_index = len(self.graph_points) - 1
                # self.vertices.append(obj)
            elif prim["type"] == "endPoint":
                p = Point(prim['x'], prim['y'])
                # self.points.append(p)
                self.centroids.append(p)
                obj = {
                    "point": p,
                    "position": "end"
                }
                self.end_point = obj
                self.graph_points.append(self.end_point["point"])
                self.end_point_index = len(self.graph_points) - 1
                # self.vertices.append(obj)
        self.points = sorted(self.points, key=lambda point: point.x)
        self.vertices = sorted(self.vertices, key=lambda vertex: vertex["point"].x)

    def prepare_vertices(self):
        for obst in self.obst:
            x_min, y_min, x_max, y_max = obst.bounds
            points = get_coordinates(obst)[:-1]
            for i, p in enumerate(points):
                x = p[0]
                y = p[1]
                obj = {}
                obj["point"] = Point(x, y)
                j = i + 1 if i < len(points) - 1 else 0
                if points[i-1][0] < x and points[j][0] < x:
                    obj["position"] = "out"
                elif points[i-1][0] > x and points[j][0] > x:
                    obj["position"] = "in"
                else:
                    obj["position"] = "middle"
                obj["left_trap_graph_point_index"] = []
                obj["right_trap_graph_point_index"] = []
                obj["right_trapezoids_index"] = []
                obj["left_trapezoids_index"] = []
                self.vertices.append(obj)
        self.vertices = sorted(self.vertices, key=lambda vertex: vertex["point"].x)

    def unite_obst(self):
        new_obst = self.obst
        new_occurs = True
        while new_occurs:
            new_occurs = False
            for i in range(len(new_obst)):
                for j in range(len(new_obst)):
                    if i == j:
                        continue
                    union = self.obst[i].union(self.obst[j])
                    if union.geom_type == "Polygon":
                        new_obst.append(union)
                        new_obst.remove(self.obst[i])
                        new_obst.remove(self.obst[j])
                        new_occurs = True
                        break
                if new_occurs:
                    break
        self.obst = new_obst
        new_obst = []
        for obst in self.obst:
            new_obst.append(obst.simplify(0))
        self.obst = new_obst

    def prepare_lines(self) -> None:
        """
        Prepares points of configuration space to create Figures and Graph later.
        Points are saved in self.__configuration_points.

        На выходе будет множество вертикальных линий и их центроидов, отсортированных по х
        При этом центроидов на 2 больше, чем линий, тк там еще начальная и конечная точки
        """
        new_left_boundary, new_right_boundary = True, True
        for index, vertex in enumerate(self.vertices):
            # if self.point_inside_obst(vertex["point"]):
            #     vertex["position"] = "closed"
            #     continue
            if vertex["position"] == "boundary":
                closest_lower_point = closest_upper_point = y
            closest_upper_point = self.y_limit[1]
            closest_lower_point = self.y_limit[0]
            change_lower, change_upper = True, True
            x, y = vertex["point"].x, vertex["point"].y

            if x == 0:
                new_left_boundary = False
            if x == 100:
                new_right_boundary = False

            vertical = LineString([[x, self.y_limit[0]], [x, self.y_limit[1]]])
            for obst in self.obst:
                x_min, y_min, x_max, y_max = obst.bounds
                # Значит будет пересекать объект
                if x_min <= x <= x_max:
                    intersection = obst.intersection(vertical)
                    if intersection.geom_type == "GeometryCollection":
                        geoms = intersection.geoms
                        for g in geoms:
                            if g.geom_type != "LineString":
                                continue
                            y_intersections = g.coords.xy[1]
                            for i, y_coord in enumerate(y_intersections):
                                if y_coord == y:
                                    if i == 0:
                                        if y_intersections[1] < y_coord:
                                            closest_lower_point = y_coord
                                        else:
                                            closest_upper_point = y_coord
                                    else:
                                        if y_intersections[0] < y_coord:
                                            closest_lower_point = y_coord
                                        else:
                                            closest_upper_point = y_coord
                                (closest_lower_point,
                                 closest_upper_point) = self.compare_intersection_points(y,
                                                                                           closest_lower_point,
                                                                                           closest_upper_point,
                                                                                           y_coord)
                    if intersection.geom_type == "MultiLineString":
                        lines = intersection.geoms
                        for l in lines:
                            y_intersections = l.coords.xy[1]
                            for i, y_coord in enumerate(y_intersections):
                                if y_coord == y:
                                    if i == 0:
                                        if y_intersections[1] < y_coord:
                                            closest_lower_point = y_coord
                                        else:
                                            closest_upper_point = y_coord
                                    else:
                                        if y_intersections[0] < y_coord:
                                            closest_lower_point = y_coord
                                        else:
                                            closest_upper_point = y_coord
                                (closest_lower_point,
                                 closest_upper_point) = self.compare_intersection_points(y,
                                                                                           closest_lower_point,
                                                                                           closest_upper_point,
                                                                                           y_coord)
                    if intersection.geom_type == "LineString":
                        y_intersections = intersection.coords.xy[1]
                        for i, y_coord in enumerate(y_intersections):
                            if y_coord == y:
                                if i == 0:
                                    if y_intersections[1] < y_coord:
                                        closest_lower_point = y_coord
                                    else:
                                        closest_upper_point = y_coord
                                else:
                                    if y_intersections[0] < y_coord:
                                        closest_lower_point = y_coord
                                    else:
                                        closest_upper_point = y_coord

                            (closest_lower_point,
                             closest_upper_point) = self.compare_intersection_points(y,
                                                                                       closest_lower_point,
                                                                                       closest_upper_point,
                                                                                       y_coord)
            new_lines = []

            if closest_lower_point == y == closest_upper_point:
                vertex["lower"] = None
                vertex["upper"] = None
                vertex["position"] = "boundary"
            elif closest_upper_point == y:
                lower = LineString([[x, closest_lower_point], [x, y]])
                vertex["position"] = "middle"
                vertex["lower"] = lower
                vertex["upper"] = None
                new_lines.append(lower)
            elif closest_lower_point == y:
                upper = LineString([[x, y], [x, closest_upper_point]])
                vertex["position"] = "middle"
                vertex["upper"] = upper
                vertex["lower"] = None
                new_lines.append(upper)
            else:
                lower = LineString([[x, closest_lower_point], [x, y]])
                upper = LineString([[x, y], [x, closest_upper_point]])
                vertex["lower"] = lower
                vertex["upper"] = upper
                new_lines.append(lower)
                new_lines.append(upper)
            vertex["lower_y"] = closest_lower_point
            vertex["upper_y"] = closest_upper_point
            for l in new_lines:
                self.lines.append(l)
        
        if new_left_boundary:
            left_vertical = {
                "point": Point([self.x_limit[0], (self.y_limit[0] + self.y_limit[1]) / 2]),
                "upper_y": 100,
                "lower_y": 0, 
                "upper": LineString([
                    Point([self.x_limit[0], (self.y_limit[0] + self.y_limit[1]) / 2]),
                    Point([self.x_limit[0], self.y_limit[1]])
                    ]),
                "lower": LineString([
                    Point([self.x_limit[0], self.y_limit[0]]), 
                    Point([self.x_limit[0], (self.y_limit[0] + self.y_limit[1]) / 2])
                ]),
                "position": "out",
                "left_trap_graph_point_index": [],
                "right_trap_graph_point_index": [],
                "right_trapezoids_index": [],
                "left_trapezoids_index": []
            }
            self.vertices.append(left_vertical)
        if new_right_boundary:
            right_vertical = LineString([[self.x_limit[1], self.y_limit[0]], [self.x_limit[1], self.y_limit[1]]])
            self.lines.append(right_vertical)

            right_vertical = {
                "point": Point([self.x_limit[1], (self.y_limit[0] + self.y_limit[1]) / 2]),
                "upper_y": 100,
                "lower_y": 0,
                "upper": LineString([
                    Point([self.x_limit[1], (self.y_limit[0] + self.y_limit[1]) / 2]),
                    Point([self.x_limit[1], self.y_limit[1]])
                    ]),
                "lower": LineString([
                    Point([self.x_limit[1], self.y_limit[0]]), 
                    Point([self.x_limit[1], (self.y_limit[0] + self.y_limit[1]) / 2])
                ]),
                "position": "in",
                "left_trap_graph_point_index": [],
                "right_trap_graph_point_index": [],
                "right_trapezoids_index": [],
                "left_trapezoids_index": []
            }
            self.vertices.append(right_vertical)

        for line in self.lines:
            self.centroids.append(line.centroid)
        
        self.vertices = sorted(self.vertices, key=lambda vertex: vertex["point"].x)
        # self.centroids = sorted(self.centroids, key=lambda point: point.x)
        for i, point in enumerate(self.centroids):
            if point == self.start_point:
                self.start_point_index = i
            if point == self.end_point:
                self.end_point_index = i

    def line_intersects_obst(self, line):
        for obst in self.obst:
            if (line.covered_by(obst) and not line.touches(obst)):
                return True
            if line.crosses(obst) and line.intersects(obst):
                if np.round(line.intersection(obst).length, 4) > 0:
                    return True
        return False

    def point_inside_obst(self, point):
        for obst in self.obst:
            if point.within(obst):
                return True
        return False

    def prepare_edges(self):
        # print(self.graph_points)
        start_owner_index = self.start_point["owner_trap_graph_point_index"]
        start_owner = self.graph_points[start_owner_index]
        start_dst = self.start_point["point"].distance(start_owner.centroid)
        self.edges.append([self.start_point_index, self.start_point["owner_trap_graph_point_index"], start_dst])

        for v in self.vertices:
            if len(v["left_trap_graph_point_index"]) and len(v["right_trap_graph_point_index"]):
                if v["position"] == "in":
                    # centroids
                    upper_centroid = v["upper"].centroid
                    lower_centroid = v["lower"].centroid
                    left_trapezoid = self.trapezoids[v["left_trapezoids_index"][0]]["trapezoid"]
                    right_trapezoid = []
                    for i in v["right_trapezoids_index"]:
                        right_trapezoid.append(self.trapezoids[i]["trapezoid"])

                    # index
                    left_trap_i = v["left_trap_graph_point_index"][0]
                    right_trap_i = []
                    for i in v["right_trap_graph_point_index"]:
                        right_trap_i.append(i)
                    upper_centroid_i = len(self.graph_points)
                    self.graph_points.append(upper_centroid)
                    lower_centroid_i = len(self.graph_points)
                    self.graph_points.append(lower_centroid)

                    # find upper and lower trapezoids
                    min_y = []
                    for trap in right_trapezoid:
                        min_y.append(trap.bounds[1])
                    if min_y[0] < min_y[1]:
                        self.edges.append([left_trap_i, upper_centroid_i, left_trapezoid.centroid.distance(upper_centroid)])
                        self.edges.append([left_trap_i, lower_centroid_i, left_trapezoid.centroid.distance(lower_centroid)])
                        self.edges.append([upper_centroid_i, right_trap_i[1], right_trapezoid[1].centroid.distance(upper_centroid)])
                        self.edges.append([lower_centroid_i, right_trap_i[0], right_trapezoid[0].centroid.distance(lower_centroid)])
                    else:
                        self.edges.append([left_trap_i, upper_centroid_i, left_trapezoid.centroid.distance(upper_centroid)])
                        self.edges.append([left_trap_i, lower_centroid_i, left_trapezoid.centroid.distance(lower_centroid)])
                        self.edges.append([upper_centroid_i, right_trap_i[0], right_trapezoid[0].centroid.distance(upper_centroid)])
                        self.edges.append([lower_centroid_i, right_trap_i[1], right_trapezoid[1].centroid.distance(lower_centroid)])
                elif v["position"] == "out":
                    # centroids
                    upper_centroid = v["upper"].centroid
                    lower_centroid = v["lower"].centroid
                    left_trapezoid = []
                    right_trapezoid = self.trapezoids[v["right_trapezoids_index"][0]]["trapezoid"]
                    for i in v["left_trapezoids_index"]:
                        left_trapezoid.append(self.trapezoids[i]["trapezoid"])

                    # index
                    right_trap_i = v["right_trap_graph_point_index"][0]
                    left_trap_i = []
                    for i in v["left_trap_graph_point_index"]:
                        left_trap_i.append(i)
                    upper_centroid_i = len(self.graph_points)
                    self.graph_points.append(upper_centroid)
                    lower_centroid_i = len(self.graph_points)
                    self.graph_points.append(lower_centroid)

                    # find upper and lower trapezoids
                    min_y = []
                    for trap in left_trapezoid:
                        min_y.append(trap.bounds[1])
                    if min_y[0] < min_y[1]:
                        self.edges.append([right_trap_i, upper_centroid_i, right_trapezoid.centroid.distance(upper_centroid)])
                        self.edges.append([right_trap_i, lower_centroid_i, right_trapezoid.centroid.distance(lower_centroid)])
                        self.edges.append([upper_centroid_i, left_trap_i[1], left_trapezoid[1].centroid.distance(upper_centroid)])
                        self.edges.append([lower_centroid_i, left_trap_i[0], left_trapezoid[0].centroid.distance(lower_centroid)])
                    else:
                        self.edges.append([right_trap_i, upper_centroid_i, right_trapezoid.centroid.distance(upper_centroid)])
                        self.edges.append([right_trap_i, lower_centroid_i, right_trapezoid.centroid.distance(lower_centroid)])
                        self.edges.append([upper_centroid_i, left_trap_i[0], left_trapezoid[0].centroid.distance(upper_centroid)])
                        self.edges.append([lower_centroid_i, left_trap_i[1], left_trapezoid[1].centroid.distance(lower_centroid)])
                elif v["position"] == "middle":
                    # centroids
                    if v["upper_y"] > v["point"].y:
                        centroid = v["upper"].centroid
                    elif v["lower_y"] < v["point"].y:
                        centroid = v["lower"].centroid
                    left_trapezoid = self.trapezoids[v["left_trapezoids_index"][0]]["trapezoid"]
                    right_trapezoid = self.trapezoids[v["right_trapezoids_index"][0]]["trapezoid"]

                    # index
                    right_trap_i = v["right_trap_graph_point_index"][0]
                    left_trap_i = v["left_trap_graph_point_index"][0]
                    centroid_i = len(self.graph_points)
                    self.graph_points.append(centroid)

                    self.edges.append([right_trap_i, centroid_i, right_trapezoid.centroid.distance(centroid)])
                    self.edges.append([left_trap_i, centroid_i, left_trapezoid.centroid.distance(centroid)])
                
            # if len(v["left_trap_graph_point_index"]) and len(v["right_trap_graph_point_index"]):
            #     left = v["left_trap_graph_point_index"]
            #     right = v["right_trap_graph_point_index"]
            #     # print(left, right)
            #     centroid_left = self.graph_points[left[0]]
            #     centroid_right = self.graph_points[right[0]]
            #     dst = centroid_left.distance(centroid_right)
            #     self.edges.append([left, right, dst])

        end_owner_index = self.end_point["owner_trap_graph_point_index"]
        end_owner = self.graph_points[end_owner_index]
        end_dst = self.end_point["point"].distance(end_owner.centroid)
        self.edges.append([self.end_point["owner_trap_graph_point_index"], self.end_point_index, end_dst])

    def divide_space_into_trapezoids(self):
        for i, v_left in enumerate(self.vertices):
            left_point = v_left["point"]
            if v_left["position"] == "in":
                upper_found, lower_found = False, False
                try:
                    upper_centroid, lower_centroid = v_left["upper"].centroid, v_left["lower"].centroid
                except AttributeError:
                    print(v_left)
                    v_left["error"] = True
                for j in range(i + 1, len(self.vertices)):
                    v_right = self.vertices[j]
                    right_point = v_right["point"]
                    line_upper = LineString([upper_centroid, right_point])
                    line_lower = LineString([lower_centroid, right_point])

                    if not self.line_intersects_obst(line_upper) and not upper_found:
                        if v_right["position"] == "in":
                            coords = [
                                [left_point.x, v_left["upper_y"]],
                                [left_point.x, left_point.y],
                                [right_point.x, v_right["lower_y"]],
                                [right_point.x, v_right["upper_y"]]
                            ]
                        elif v_right["position"] == "out":
                            line = LineString([[left_point.x, v_left["upper_y"]],[right_point.x, v_right["lower_y"]]])
                            if not self.line_intersects_obst(line):
                                coords = [
                                    [left_point.x, v_left["upper_y"]],
                                    [left_point.x, left_point.y],
                                    [right_point.x, v_right["lower_y"]],
                                    [right_point.x, right_point.y],
                                ]
                            else:
                                coords = [
                                    [left_point.x, v_left["upper_y"]],
                                    [left_point.x, left_point.y],
                                    [right_point.x, right_point.y],
                                    [right_point.x, v_right["upper_y"]]
                                ]
                        elif v_right["position"] == "middle":
                            if v_right["upper_y"] > right_point.y:
                                coords = [
                                    [left_point.x, v_left["upper_y"]],
                                    [left_point.x, left_point.y],
                                    [right_point.x, right_point.y],
                                    [right_point.x, v_right["upper_y"]]
                                ]
                            else:
                                coords = [
                                    [left_point.x, v_left["upper_y"]],
                                    [left_point.x, left_point.y],
                                    [right_point.x, v_right["lower_y"]],
                                    [right_point.x, right_point.y]
                                ]
                        elif v_right["position"] == "boundary":
                            coords = [
                                [left_point.x, left_point.y],
                                [left_point.x, v_left["upper_y"]],
                                [right_point.x, right_point.y]
                            ]
                        upper_found = True
                        self.add_new_trapezoid(coords, v_left, v_right)
                    if not self.line_intersects_obst(line_lower) and not lower_found:
                        if v_right["position"] == "in":
                            coords = [
                                [left_point.x, left_point.y],
                                [left_point.x, v_left["lower_y"]],
                                [right_point.x, v_right["lower_y"]],
                                [right_point.x, v_right["upper_y"]]
                            ]
                        elif v_right["position"] == "out":
                            line = LineString([[left_point.x, v_left["lower_y"]],[right_point.x, v_right["upper_y"]]])
                            if not self.line_intersects_obst(line):
                                coords = [
                                    [left_point.x, left_point.y],
                                    [left_point.x, v_left["lower_y"]],
                                    [right_point.x, right_point.y],
                                    [right_point.x, v_right["upper_y"]],
                                ]
                            else:
                                coords = [
                                    [left_point.x, left_point.y],
                                    [left_point.x, v_left["lower_y"]],
                                    [right_point.x, v_right["lower_y"]],
                                    [right_point.x, right_point.y],
                                ]            
                        elif v_right["position"] == "middle":
                            if v_right["upper_y"] > right_point.y:
                                coords = [
                                    [left_point.x, left_point.y],
                                    [left_point.x, v_left["lower_y"]],
                                    [right_point.x, right_point.y],
                                    [right_point.x, v_right["upper_y"]]
                                ]
                            else:
                                coords = [
                                    [left_point.x, left_point.y],
                                    [left_point.x, v_left["lower_y"]],
                                    [right_point.x, v_right["lower_y"]],
                                    [right_point.x, right_point.y]
                                ]
                        elif v_right["position"] == "boundary":
                                coords = [
                                    [left_point.x, left_point.y],
                                    [left_point.x, v_left["lower_y"]],
                                    [right_point.x, right_point.y]
                                ]
                        lower_found = True
                        self.add_new_trapezoid(coords, v_left, v_right)
                    if upper_found and lower_found:
                        break
            elif v_left["position"] == "out":
                for j in range(i + 1, len(self.vertices)):
                    v_right = self.vertices[j]
                    right_point = v_right["point"]
                    line = LineString([left_point, right_point])
                    intersects = self.line_intersects_obst(line)
                    if not intersects:
                        if v_right["position"] == "in":
                            coords = [
                                    [left_point.x, v_left["upper_y"]],
                                    [left_point.x, v_left["lower_y"]],
                                    [right_point.x, v_right["lower_y"]],
                                    [right_point.x, v_right["upper_y"]]
                            ]
                        elif v_right["position"] == "out":
                            if left_point.y >= right_point.y:
                                coords = [
                                    [left_point.x, v_left["upper_y"]],
                                    [left_point.x, v_left["lower_y"]],
                                    [right_point.x, right_point.y],
                                    [right_point.x, v_right["upper_y"]]
                                ]
                            else:
                                coords = [
                                    [left_point.x, v_left["upper_y"]],
                                    [left_point.x, v_left["lower_y"]],
                                    [right_point.x, v_right["lower_y"]],
                                    [right_point.x, right_point.y]
                                ]
                        elif v_right["position"] == "middle":
                            if v_right["upper_y"] > right_point.y:
                                coords = [
                                    [left_point.x, v_left["upper_y"]],
                                    [left_point.x, v_left["lower_y"]],
                                    [right_point.x, right_point.y],
                                    [right_point.x, v_right["upper_y"]]
                                ]
                            else:
                                coords = [
                                    [left_point.x, v_left["upper_y"]],
                                    [left_point.x, v_left["lower_y"]],
                                    [right_point.x, v_right["lower_y"]],
                                    [right_point.x, right_point.y]
                                ]
                        try:
                            self.add_new_trapezoid(coords, v_left, v_right)
                        except UnboundLocalError:
                            print(coords)
                        break
            elif v_left["position"] == "middle":
                for j in range(i + 1, len(self.vertices)):
                    v_right = self.vertices[j]
                    right_point = v_right["point"]
                    line = LineString([left_point, right_point])
                    intersects = self.line_intersects_obst(line)
                    if not intersects:
                        if v_right["position"] == "in":
                            if v_left["upper_y"] > left_point.y:
                                coords = [
                                        [left_point.x, v_left["upper_y"]],
                                        [left_point.x, left_point.y],
                                        [right_point.x, v_right["lower_y"]],
                                        [right_point.x, v_right["upper_y"]]
                                ]
                            elif v_left["lower_y"] < left_point.y:
                                coords = [
                                        [left_point.x, left_point.y],
                                        [left_point.x, v_left["lower_y"]],
                                        [right_point.x, v_right["lower_y"]],
                                        [right_point.x, v_right["upper_y"]]
                                ]
                        elif v_right["position"] == "out":
                            if v_left["upper_y"] > left_point.y:
                                line = LineString([[left_point.x, v_left["upper_y"]], [right_point.x, v_right["lower_y"]]])
                                if not self.line_intersects_obst(line):
                                    coords = [
                                        [left_point.x, v_left["upper_y"]],
                                        [left_point.x, left_point.y],
                                        [right_point.x, v_right["lower_y"]],
                                        [right_point.x, right_point.y]
                                    ]
                                else:
                                    coords = [
                                        [left_point.x, v_left["upper_y"]],
                                        [left_point.x, left_point.y],
                                        [right_point.x, right_point.y],
                                        [right_point.x, v_right["upper_y"]],
                                    ]
                            elif v_left["lower_y"] < left_point.y:
                                line = LineString([[left_point.x, v_left["lower_y"]], [right_point.x, v_right["upper_y"]]])
                                if not self.line_intersects_obst(line):
                                    coords = [
                                        [left_point.x, left_point.y],
                                        [left_point.x, v_left["lower_y"]],
                                        [right_point.x, right_point.y],
                                        [right_point.x, v_right["upper_y"]]
                                    ]
                                else:
                                    coords = [
                                        [left_point.x, left_point.y],
                                        [left_point.x, v_left["lower_y"]],
                                        [right_point.x, v_right["lower_y"]],
                                        [right_point.x, right_point.y]
                                    ]
                        elif v_right["position"] == "middle":
                            if v_left["upper_y"] > left_point.y and v_right["upper_y"] > right_point.y:
                                coords = [
                                    [left_point.x, v_left["upper_y"]],
                                    [left_point.x, left_point.y],
                                    [right_point.x, right_point.y],
                                    [right_point.x, v_right["upper_y"]]
                                ]
                            elif v_left["upper_y"] > left_point.y and v_right["lower_y"] < right_point.y:
                                coords = [
                                    [left_point.x, v_left["upper_y"]],
                                    [left_point.x, left_point.y],
                                    [right_point.x, v_right["lower_y"]],
                                    [right_point.x, right_point.y]
                                ]
                            elif v_left["lower_y"] < left_point.y and v_right["lower_y"] < right_point.y:
                                coords = [
                                    [left_point.x, left_point.y],
                                    [left_point.x, v_left["lower_y"]],
                                    [right_point.x, v_right["lower_y"]],
                                    [right_point.x, right_point.y]
                                ]
                            elif v_left["lower_y"] < left_point.y and v_right["upper_y"] > right_point.y:
                                coords = [
                                    [left_point.x, left_point.y],
                                    [left_point.x, v_left["lower_y"]],
                                    [right_point.x, right_point.y],
                                    [right_point.x, v_right["upper_y"]],
                                ]
                        elif v_right["position"] == "boundary":
                            if v_left["upper_y"] > left_point.y:
                                coords = [
                                    [left_point.x, left_point.y],
                                    [left_point.x, v_left["upper_y"]],
                                    [right_point.x, right_point.y]
                                ]
                            elif v_left["lower_y"] < left_point.y:
                                coords = [
                                    [left_point.x, left_point.y],
                                    [left_point.x, v_left["lower_y"]],
                                    [right_point.x, right_point.y]
                                ]
                        self.add_new_trapezoid(coords, v_left, v_right)
                        break
            elif v_left["position"] == "boundary":
                for j in range(i + 1, len(self.vertices)):
                    v_right = self.vertices[j]
                    right_point = v_right["point"]
                    line = LineString([left_point, right_point])
                    intersects = self.line_intersects_obst(line)
                    if not intersects:
                        if v_right["position"] == "out":
                            line = LineString([
                                [left_point.x, left_point.y],
                                [right_point.x, v_right["upper_y"]]
                            ])
                            if not self.line_intersects_obst(line):
                                coords = [
                                        [left_point.x, left_point.y],
                                        [right_point.x, right_point.y],
                                        [right_point.x, v_right["upper_y"]]
                                ]
                            else:
                                coords = [
                                        [left_point.x, left_point.y],
                                        [right_point.x, v_right["lower_y"]],
                                        [right_point.x, right_point.y]
                                ]
                        elif v_right["position"] == "in":
                            coords = [
                                [left_point.x, left_point.y],
                                [right_point.x, v_right["lower_y"]],
                                [right_point.x, v_right["upper_y"]],
                            ]
                        elif v_right["position"] == "middle":
                            if v_right["upper_y"] > right_point.y:
                                coords = [
                                    [left_point.x, left_point.y],
                                    [right_point.x, right_point.y],
                                    [right_point.x, v_right["upper_y"]]
                                ]
                            elif v_right["lower_y"] < right_point.y:
                                coords = [
                                    [left_point.x, left_point.y],
                                    [right_point.x, right_point.y],
                                    [right_point.x, v_right["lower_y"]],
                                ]
                        self.add_new_trapezoid(coords, v_left, v_right)
                        break
            elif v_left["position"] == "closed":
                continue

    def compare_intersection_points(self,
                                      y,
                                      closest_lower_point,
                                      closest_upper_point,
                                      y_coord):
        if y < y_coord <= closest_upper_point:
            closest_upper_point = y_coord
        elif y > y_coord >= closest_lower_point:
            closest_lower_point = y_coord
        return closest_lower_point, closest_upper_point

    def add_new_trapezoid(self, coords, v_left, v_right):
        trapezoid = Polygon(coords)
        obj = {
            "trapezoid": trapezoid,
            "left": v_left,
            "right": v_right
        }
        obj["centroid"] = trapezoid.centroid
        self.graph_points.append(obj["centroid"])
        graph_point_index = len(self.graph_points) - 1
        obj["graph_point_index"] = graph_point_index
        self.trapezoids.append(obj)
        trap_index = len(self.trapezoids) - 1
        if trapezoid.contains(self.start_point["point"]):
            self.start_point["owner_trap_graph_point_index"] = graph_point_index
        if trapezoid.contains(self.end_point["point"]):
            self.end_point["owner_trap_graph_point_index"] = graph_point_index
        v_left["right_trap_graph_point_index"].append(graph_point_index)
        v_right["left_trap_graph_point_index"].append(graph_point_index)
        v_left["right_trapezoids_index"].append(trap_index)
        v_right["left_trapezoids_index"].append(trap_index)
