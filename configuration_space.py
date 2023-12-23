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
        self.end_point_index = None             # index among centroids
        self.start_point_index = None
        self.end_point = None
        self.start_point = None
        self.obst = []
        self.__x_limit = [min_limit, max_limit]
        self.__y_limit = [min_limit, max_limit]
        self.lines = []
        self.vertices = []
        self.points = []
        self.edges = []
        self.centroids = []
        self.connections = {}

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
                x_min, y_min, x_max, y_max = obj.bounds
                for p in obst_points:
                    obj = {}
                    obj["point"] = p
                    if p.x == x_min:
                        obj["position"] = "in"
                    elif p.x == x_max:
                        obj["position"] = "out"
                    else:
                        obj["position"] = "middle"
                    self.vertices.append(obj)
            elif prim["type"] == "startPoint":
                p = Point(prim['x'], prim['y'])
                self.start_point = p
                # self.points.append(p)
                self.centroids.append(p)
                obj = {
                    "point": p,
                    "position": "start"
                }
                # self.vertices.append(obj)
            elif prim["type"] == "endPoint":
                p = Point(prim['x'], prim['y'])
                self.end_point = p
                # self.points.append(p)
                self.centroids.append(p)
                obj = {
                    "point": p,
                    "position": "end"
                }
                # self.vertices.append(obj)
        self.points = sorted(self.points, key=lambda point: point.x)
        self.vertices = sorted(self.vertices, key=lambda vertex: vertex["point"].x)

    def __compare_intersection_points(self,
                                      y,
                                      closest_lower_point,
                                      closest_upper_point,
                                      y_coord):
        if y < y_coord <= closest_upper_point:
            closest_upper_point = y_coord
        elif y > y_coord >= closest_lower_point:
            closest_lower_point = y_coord
        return closest_lower_point, closest_upper_point

    def prepare_lines(self) -> None:
        """
        Prepares points of configuration space to create Figures and Graph later.
        Points are saved in self.__configuration_points.

        На выходе будет множество вертикальных линий и их центроидов, отсортированных по х
        При этом центроидов на 2 больше, чем линий, тк там еще начальная и конечная точки
        """
        left_vertical = LineString([[self.__x_limit[0], self.__y_limit[0]], [self.__x_limit[0], self.__y_limit[1]]])
        self.lines.append(left_vertical)
        for index, vertex in enumerate(self.vertices):
            closest_upper_point = self.__y_limit[1]
            closest_lower_point = self.__y_limit[0]
            change_lower, change_upper = True, True
            x, y = vertex["point"].x, vertex["point"].y
            vertical = LineString([[x, self.__y_limit[0]], [x, self.__y_limit[1]]])

            for obst in self.obst:
                x_min, y_min, x_max, y_max = obst.bounds
                # Значит будет пересекать объект
                if x_min <= x <= x_max:
                    intersection = obst.intersection(vertical)
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
                             closest_upper_point) = self.__compare_intersection_points(y,
                                                                                       closest_lower_point,
                                                                                       closest_upper_point,
                                                                                       y_coord)
            new_lines = []
            if closest_lower_point == y == closest_upper_point:
                vertex["lower"] = None
                vertex["upper"] = None
                vertex["lower_y"] = None
                vertex["upper_y"] = None
            elif closest_upper_point == y:
                lower = LineString([[x, closest_lower_point], [x, y]])
                vertex["lower"] = lower
                vertex["upper"] = None
                vertex["lower_y"] = closest_lower_point
                vertex["upper_y"] = None
                new_lines.append(lower)
            elif closest_lower_point == y:
                upper = LineString([[x, y], [x, closest_upper_point]])
                vertex["upper"] = upper
                vertex["lower"] = None
                vertex["upper_y"] = closest_upper_point
                vertex["lower_y"] = None
                new_lines.append(upper)
            else:
                lower = LineString([[x, closest_lower_point], [x, y]])
                upper = LineString([[x, y], [x, closest_upper_point]])
                vertex["lower"] = lower
                vertex["upper"] = upper
                vertex["lower_y"] = closest_lower_point
                vertex["upper_y"] = closest_upper_point
                new_lines.append(lower)
                new_lines.append(upper)

            for l in new_lines:
                self.lines.append(l)
        for index, p in enumerate(self.points):
            closest_upper_point = self.__y_limit[1]
            closest_lower_point = self.__y_limit[0]
            change_lower, change_upper = True, True
            x, y = p.x, p.y
            vertical = LineString([[x, self.__y_limit[0]], [x, self.__y_limit[1]]])

            for obst in self.obst:
                x_min, y_min, x_max, y_max = obst.bounds
                # Значит будет пересекать объект
                if x_min <= x <= x_max:
                    intersection = obst.intersection(vertical)
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
                             closest_upper_point) = self.__compare_intersection_points(y,
                                                                                       closest_lower_point,
                                                                                       closest_upper_point,
                                                                                       y_coord)
            new_lines = []
            if closest_lower_point == y == closest_upper_point:
                pass
            elif closest_upper_point == y:
                lower = LineString([[x, closest_lower_point], [x, y]])
                new_lines.append(lower)
            elif closest_lower_point == y:
                upper = LineString([[x, y], [x, closest_upper_point]])
                new_lines.append(upper)
            else:
                new_lines.append(LineString([[x, closest_lower_point], [x, y]]))
                new_lines.append(LineString([[x, y], [x, closest_upper_point]]))

            for l in new_lines:
                self.lines.append(l)
            # self.points_and_their_verticals[index]["lower"]
        
        right_vertical = LineString([[self.__x_limit[1], self.__y_limit[0]], [self.__x_limit[1], self.__y_limit[1]]])
        self.lines.append(right_vertical)

        for line in self.lines:
            self.centroids.append(line.centroid)

        # self.centroids = sorted(self.centroids, key=lambda point: point.x)
        for i, point in enumerate(self.centroids):
            if point == self.start_point:
                self.start_point_index = i
            if point == self.end_point:
                self.end_point_index = i

    def divide_space_into_verticals(self) -> None:
        """
        Method divides configuration space into trapezoids with
        given self.__configuration_points. Result will be saved in
        self.lines and self.trapezoids.
        Есть набор линий, набор их центров, нужно построить набор трапецоидов

        """
        for i in tqdm(range(len(self.centroids))):
            centroid_i = self.centroids[i]
            neighbor_x_coord = None
            self.connections[i] = []
            for j in range(i + 1, len(self.centroids)):
                if j == i:
                    continue
                centroid_j = self.centroids[j]

                if neighbor_x_coord and centroid_j.x > neighbor_x_coord:
                    break

                line = LineString([centroid_i, centroid_j])
                intersects = False

                for obst in self.obst:
                    if line.intersects(obst):
                        if (centroid_i.x == centroid_j.x and not line.touches(obst)) or (centroid_i.x != centroid_j.x):
                            intersects = True
                            break
                if not intersects:
                    if centroid_i.x != centroid_j.x:
                        neighbor_x_coord = centroid_j.x
                    distance = centroid_i.distance(centroid_j)
                    self.edges.append([i, j, distance])
                    # self.connections[i].append(j)

        # print("Space division end")

    def line_intersects_obst(self, line):
        for obst in self.obst:
            if line.crosses(obst) or (line.covered_by(obst) and not line.touches(obst)):
                return True
        return False

    def divide_space_into_trapezoids(self):
        for i, v_left in enumerate(self.vertices):
            left_point = v_left["point"]
            if v_left["position"] == "in":
                upper_found, lower_found = False, False
                upper_centroid, lower_centroid = v_left["upper"].centroid, v_left["lower"].centroid
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
                            coords = [
                                [left_point.x, v_left["upper_y"]],
                                [left_point.x, left_point.y],
                                [right_point.x, v_right["lower_y"]],
                                [right_point.x, right_point.y]
                            ]
                        elif v_right["position"] == "middle":
                            if v_right["upper_y"]:
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
                        trapezoid = Polygon(coords)
                        self.trapezoids.append(trapezoid)
                        upper_found = True
                    if not self.line_intersects_obst(line_lower) and not lower_found:
                        if v_right["position"] == "in":
                            coords = [
                                [left_point.x, left_point.y],
                                [left_point.x, v_left["lower_y"]],
                                [right_point.x, v_right["lower_y"]],
                                [right_point.x, v_right["upper_y"]]
                            ]
                        elif v_right["position"] == "out":
                            coords = [
                                [left_point.x, left_point.y],
                                [left_point.x, v_left["lower_y"]],
                                [right_point.x, v_right["lower_y"]],
                                [right_point.x, right_point.y]
                            ]
                        elif v_right["position"] == "middle":
                            if v_right["upper_y"]:
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
                        trapezoid = Polygon(coords)
                        self.trapezoids.append(trapezoid)
                        lower_found = True
                    
                    if upper_found and lower_found:
                        break
            elif v_left["position"] == "out":
                for j in range(i + 1, len(self.vertices)):
                    v_right = self.vertices[j]
                    right_point = v_right["point"]
                    line = LineString([left_point, right_point])
                    intersects = False
                    for obst in self.obst:
                        if line.crosses(obst) or (line.covered_by(obst) and not line.touches(obst)):
                            intersects = True
                            break
                    if not intersects:
                        if v_right["position"] == "in":
                            trap_right = [
                                    [right_point.x, v_right["lower_y"]],
                                    [right_point.x, v_right["upper_y"]],
                                    [left_point.x, v_left["upper_y"]],
                                    [left_point.x, v_left["lower_y"]]
                            ]
                            trapezoid = Polygon(trap_right)
                            self.trapezoids.append(trapezoid)
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
                            trapezoid = Polygon(coords)
                            self.trapezoids.append(trapezoid)
                        elif v_right["position"] == "middle":
                            if v_right["upper_y"]:
                                coords = [
                                    [left_point.x, v_left["upper_y"]],
                                    [left_point.x, v_left["lower_y"]],
                                    [right_point.x, right_point.y]
                                    [right_point.x, v_right["upper_y"]],
                                ]
                            trapezoid = Polygon(coords)
                            self.trapezoids.append(trapezoid)
                        break
            elif v_left["position"] == "middle":
                for j in range(i + 1, len(self.vertices)):
                    v_right = self.vertices[j]
                    right_point = v_right["point"]
                    line = LineString([left_point, right_point])
                    intersects = False
                    for obst in self.obst:
                        # if (line.intersects(obst) and not line.touches(obst) and line.covered_by(obst)):
                        if line.crosses(obst) or (line.covered_by(obst) and not line.touches(obst)):
                            intersects = True
                            break
                    if not intersects:
                        if v_right["position"] == "in":
                            trap_right = [
                                    [right_point.x, v_right["lower_y"]],
                                    [right_point.x, v_right["upper_y"]],
                                    [left_point.x, v_left["upper_y"]],
                                    [left_point.x, left_point.y]
                            ]
                            if not v_left["lower_y"]:
                                trap_left = [
                                        [left_point.x, v_left["upper_y"]],
                                        [left_point.x, left_point.y]
                                    ]
                            trapezoid = Polygon(trap_right)
                            self.trapezoids.append(trapezoid)
                        elif v_right["position"] == "out":
                            if left_point.y >= right_point.y:
                                coords = [
                                    [left_point.x, v_left["upper_y"]],
                                    [left_point.x, left_point.y],
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
                            trapezoid = Polygon(coords)
                            self.trapezoids.append(trapezoid)
                        elif v_right["position"] == "middle":
                            if left_point.y >= right_point.y:
                                coords = [
                                    [left_point.x, v_left["upper_y"]],
                                    [left_point.x, left_point.y],
                                    [right_point.x, right_point.y],
                                    [right_point.x, v_right["upper_y"]]
                                ]
                            else:
                                coords = [
                                    [left_point.x, left_point.y],
                                    [left_point.x, v_left["lower_y"]],
                                    [right_point.x, right_point.y],
                                    [right_point.x, v_right["lower_y"]]
                                ]
                        break