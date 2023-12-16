import json
from operator import itemgetter
from typing import List, Optional
from figure import Figure, Line, Trapezoid
from point import Point
from shapely import Polygon, Point, LineString, get_coordinates, GeometryCollection
import matplotlib.pyplot as plt


class ConfigurationSpace:
    def __init__(self):
        self.__obst = []
        self.__x_limit = [0.0, 100.0]
        self.__y_limit = [0.0, 20.0]
        self.__lines = []
        self.__points = []

    # TODO
    def parse_json(self, path: str) -> None:
        """
        Parses JSON file with obstacles and fills self.__obst.

        :param path:
        :return:
        """
        with open(path, 'r') as fp:
            array: List[dict] = json.load(fp)
            fp.close()
        for prim in array:
            if prim["type"] == "point":
                obj = Point(prim['x'], prim['y'])
                # obj = Polypoint(Point(prim['x'], prim['y']), prim["size"])
                self.__points.append(obj)
            # elif prim["type"] == "polyline":
            #     points: List[Point] = []
            #     for p in prim["points"]:
            #         points.append(Point(p['x'], p['y']))
            #     obj = LineString(points)
            #     self.__obst.append(obj)
            elif prim["type"] == "polygon":
                obst_points = []
                for p in prim["points"]:
                    point = [p['x'], p['y']]
                    self.__points.append(point)
                    obst_points.append(point)
                obj = Polygon(obst_points)
                self.__obst.append(obj)
            elif prim["type"] == "startPoint":
                # TODO
                pass
            elif prim["type"] == "endPoint":
                # TODO
                pass
        self.__points = sorted(self.__points, key=itemgetter(0))

    def __compare_intersection_points(self, y, closest_bottom_point, closest_upper_point, y_coord):
        if y < y_coord <= closest_upper_point:
            closest_upper_point = y_coord
        elif y > y_coord >= closest_bottom_point:
            closest_bottom_point = y_coord
        return closest_bottom_point, closest_upper_point

    def prepare_points(self) -> None:
        for obst in self.obst:
            obst_points = get_coordinates(obst)
            for i, p in enumerate(obst_points):
                if i == len(obst_points) - 1:
                    break
                self.__points.append(p)
        self.__points = sorted(self.__points, key=itemgetter(0))

    def prepare_lines(self) -> None:
        """
        Prepares points of configuration space to create Figures and Graph later.
        Points are saved in self.__configuration_points.

        :return:
        """
        for p in self.points:
            closest_upper_point = self.__y_limit[1]
            closest_bottom_point = self.__y_limit[0]
            x, y = p
            vertical = LineString([[x, self.__y_limit[0]], [x, self.__y_limit[1]]])

            for obst in self.obst:
                x_min, y_min, x_max, y_max = obst.bounds
                # Значит будет пересекать объект
                if x_min <= x <= x_max:
                    intersection = obst.intersection(vertical)
                    if intersection.geom_type == "MultiLineString":
                        lines = intersection.geoms
                        for l in lines:
                            y_intersections = l.coords.xy[1]
                            for y_coord in y_intersections:
                                (closest_bottom_point,
                                 closest_upper_point) = self.__compare_intersection_points(y,
                                                                                           closest_bottom_point,
                                                                                           closest_upper_point,
                                                                                           y_coord)
                    if intersection.geom_type == "LineString":
                        y_intersections = intersection.coords.xy[1]
                        for y_coord in y_intersections:
                            (closest_bottom_point,
                             closest_upper_point) = self.__compare_intersection_points(y,
                                                                                       closest_bottom_point,
                                                                                       closest_upper_point,
                                                                                       y_coord)
                    if intersection.geom_type == "Point":
                        y_coord = intersection.y
                        (closest_bottom_point,
                         closest_upper_point) = self.__compare_intersection_points(y,
                                                                                   closest_bottom_point,
                                                                                   closest_upper_point,
                                                                                   y_coord)
                    if intersection.geom_type == "MultiPoint":
                        i_points = intersection.geoms
                        for i_p in i_points:
                            y_coord = i_p.y
                            (closest_bottom_point,
                             closest_upper_point) = self.__compare_intersection_points(y,
                                                                                       closest_bottom_point,
                                                                                       closest_upper_point,
                                                                                       y_coord)
            new_lines = []
            if closest_upper_point == y:
                new_lines.append(LineString([[x, y], [x, closest_upper_point]]))
            elif closest_bottom_point == y:
                new_lines.append(LineString([[x, closest_bottom_point], [x, y]]))
            else:
                new_lines.append(LineString([[x, y], [x, closest_upper_point]]))
                new_lines.append(LineString([[x, closest_bottom_point], [x, y]]))
            for l in new_lines:
                self.__lines.append(l)




    def divide_space_into_trapezoids(self) -> None:
        """
        Method divides configuration space into trapezoids with
        given self.__configuration_points. Result will be saved in
        self.__lines and self.trapezoids.

        :return:
        """
        pass

    def create_line_with_points(self, points: List[Point]) -> List[Line]:
        """
        Method creates 1+ Line and returns it.

        :param points:
        :return:
        """

    def create_trapezoid_with_points(self,
                                     left: List[Line],
                                     right: List[Line]) -> Trapezoid:
        """
        Method creates Trapezoid with given lines.

        :param left:
        :param right:
        :return:
        """

    def add_line_to_list(self, line: Line) -> None:
        """
        Method adds line to list of lines.

        :param line:
        :return:
        """
        self.__lines.append(line)

    def add_trapezoid_to_lis(self, trapezoid: Trapezoid) -> None:
        """
        Method adds trapezoid to list of trapezoids.

        :param trapezoid:
        :return:
        """

    @property
    def obst(self):
        return self.__obst

    @property
    def points(self):
        return self.__points

    @property
    def lines(self):
        return self.__lines

    @property
    def trapezoids(self) -> List[Trapezoid]:
        return self.__trapezoids

    @points.setter
    def points(self, value):
        self.__points = value
