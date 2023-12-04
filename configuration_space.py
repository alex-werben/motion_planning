import json
from typing import List, Optional
# from obstacle import Obstacle, Polypoint, Polygon, Polyline
from figure import Figure, Line, Trapezoid
from point import Point
from shapely import Polygon, Point, LineString

#
# class ConfigurationSpace():
#     def __init__(self):
#         self.__obst: Optional[List[Obstacle]] = None
#         self.__lines: Optional[List[Line]] = None
#         self.__trapezoids: Optional[List[Trapezoid]] = None
#         self.__configuration_points: Optional[List[List[Point]]] = None
#         self.__start_end_points: Optional[List[Point]] = None
#
#     # TODO
#     def parse_json(self, path: str) -> None:
#         """
#         Parses JSON file with obstacles and fills self.__obst.
#
#         :param path:
#         :return:
#         """
#         with open(path, 'r') as fp:
#             array: List[dict] = json.load(fp)
#             fp.close()
#         for prim in array:
#             if prim["type"] == "point":
#                 obj = Point(prim['x'], prim['y'])
#                 # obj = Polypoint(Point(prim['x'], prim['y']), prim["size"])
#                 self.__obst.append(obj)
#             elif prim["type"] == "polyline":
#                 points: List[Point] = []
#                 for p in prim["points"]:
#                     points.append(Point(p['x'], p['y']))
#                 obj = LineString(points)
#                 self.__obst.append(obj)
#             elif prim["type"] == "polygon":
#                 points: List[Point] = []
#                 for p in prim["points"]:
#                     points.append(Point(p['x'], p['y']))
#                 points.append(Point(prim["points"][0]['x'], prim["points"][0]['y']))
#                 obj = Polygon(points)
#                 self.__obst.append(obj)
#             elif prim["type"] == "startPoint":
#                 # TODO
#                 pass
#             elif prim["type"] == "endPoint":
#                 # TODO
#                 pass
#
#     def prepare_points(self) -> None:
#         """
#         Prepares points of configuration space to create Figures and Graph later.
#         Points are saved in self.__configuration_points.
#
#         :return:
#         """
#
#         points: List[Point] = []
#         for obst in self.obst:
#             for p in obst.points:
#                 points.append(p)
#
#         for p in points:
#             closest_upper_point: Point = None
#             closest_bottom_point: Point = None
#             for obst in self.obst:
#                 # if current obstacle owns current point
#                 if p.owner == obst:
#                     # if current point lies on the left or on the right border of obstacle,
#                     # then search for intersections with 2 other obstacles
#                     if p.x == obst.x_borders[0] or p.x == obst.x_borders[1]:
#                         # TODO
#                         pass
#                     # if point is in the middle of obstacle then only one more intersection
#                     # needs. Upper if obstacle lies in the bottom and bottom if obstacle
#                     # lies upon point.
#                     else:
#                         # TODO
#                         pass
#                 if obst.point_crosses_obstacle_horizontally(p):
#                     pass
#
#
#
#     def sort_points(self) -> None:
#         """
#         Sorts all points in self.__configuration_points by x coordinate.
#
#         :return:
#         """
#         pass
#
#     def divide_space_into_trapezoids(self) -> None:
#         """
#         Method divides configuration space into trapezoids with
#         given self.__configuration_points. Result will be saved in
#         self.__lines and self.trapezoids.
#
#         :return:
#         """
#         pass
#
#     def create_line_with_points(self, points: List[Point]) -> List[Line]:
#         """
#         Method creates 1+ Line and returns it.
#
#         :param points:
#         :return:
#         """
#
#     def create_trapezoid_with_points(self,
#                                      left: List[Line],
#                                      right: List[Line]) -> Trapezoid:
#         """
#         Method creates Trapezoid with given lines.
#
#         :param left:
#         :param right:
#         :return:
#         """
#
#     def add_line_to_list(self, line: Line) -> None:
#         """
#         Method adds line to list of lines.
#
#         :param line:
#         :return:
#         """
#         self.__lines.append(line)
#
#     def add_trapezoid_to_lis(self, trapezoid: Trapezoid) -> None:
#         """
#         Method adds trapezoid to list of trapezoids.
#
#         :param trapezoid:
#         :return:
#         """
#
#     @property
#     def obst(self) -> List[Obstacle]:
#         return self.__obst
#
#     @property
#     def lines(self) -> List[Line]:
#         return self.__lines
#
#     @property
#     def trapezoids(self) -> List[Trapezoid]:
#         return self.__trapezoids
#
# cs = ConfigurationSpace()
# cs.parse_json("data/sample_random_primitives.json")

print(Polygon(([0, 1], [1, 0], [1, 1], [0, 0], [0, 1])).exterior.coords.xy)