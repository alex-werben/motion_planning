from typing import List
from obstacle import Obstacle
from figure import Figure, Line, Trapezoid
from point import Point


class ConfigurationSpace():
    def __init__(self):
        self.__obst: List[Obstacle] = None
        self.__lines = List[Figure] = None
        self.__trapezoids = List[Figure] = None
        self.__configuration_points: List[List[Point]] = None

    # TODO
    def parse_JSON(self, path: str) -> None:
        """
        Parses JSON file with obstacles and fills self.__obst.

        :param path:
        :return:
        """
        pass

    def prepare_points(self) -> None:
        """
        Prepares points of configuration space to create Figures and Graph later.
        Points are saved in self.__configuration_points.

        :return:
        """
        pass

    def sort_points(self) -> None:
        """
        Sorts all points in self.__configuration_points by x coordinate.

        :return:
        """
        pass

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
    def lines(self) -> List[Line]:
        return self.__lines

    @property
    def trapezoids(self) -> List[Trapezoid]:
        return self.__trapezoids
