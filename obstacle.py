from abc import ABC, abstractmethod
from point import Point
from typing import List


class Obstacle(ABC):
    def __init__(self, points: List[Point]) -> None:
        self.__points: List[Point] = points

    @abstractmethod
    def point_inside_obst(self, p: Point) -> bool:
        pass

    @property
    def points(self) -> List[Point]:
        return self.__points

    @points.setter
    def points(self, points: List[Point]) -> None:
        del self.__points
        self.__points = points


class Polyline(Obstacle):
    def __init__(self, p1: Point, p2: Point, size: float) -> None:
        super().__init__([p1, p2])
        self.__size: float = size

    # TODO
    def point_inside_obst(self, p: Point) -> bool:
        pass

    @property
    def size(self) -> float:
        return self.__size


class Polygon(Obstacle):
    def __init__(self, points: List[Point]) -> None:
        super().__init__(points)

    # TODO
    def point_inside_obst(self, p: Point) -> bool:
        pass


class Polypoint(Obstacle):
    def __init__(self, p: Point, size: float) -> None:
        super().__init__([p])
        self.__size: float = size

    # TODO
    def point_inside_obst(self, p: Point) -> bool:
        pass

    @property
    def size(self) -> float:
        return self.__size

