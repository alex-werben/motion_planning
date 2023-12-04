from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Self, Optional
from point import Point


class Figure(ABC):
    def __init__(self) -> None:
        self.__distance: float = -1.0
        self.__center: Optional[Point] = None
        self.__parent: Optional[Figure] = None

    @property
    def distance(self) -> float:
        return self.__distance

    @property
    def center(self) -> Point:
        return self.__center

    @property
    def parent(self) -> Self:
        return self.__parent

    @abstractmethod
    def __compute_center(self) -> None:
        pass

    @distance.setter
    def distance(self, distance: float) -> None:
        self.__distance = distance

    @parent.setter
    def parent(self, parent: Self) -> None:
        self.__parent = parent

    @center.setter
    def center(self, center: Point) -> None:
        self.__center = center


class Line(Figure):
    def __init__(self, p1: Point, p2: Point) -> None:
        super().__init__()
        self.__left: Optional[Trapezoid] = None
        self.__right: Optional[Trapezoid] = None
        self.__points: List[Point] = [p1, p2]
        self.__compute_center()

    @property
    def points(self) -> List[Point]:
        return self.__points

    def __compute_center(self) -> None:
        center_x: float = (self.points[0].x + self.points[1].x) / 2
        center_y: float = (self.points[0].y + self.points[1].y) / 2
        self.center = Point(center_x, center_y)

    @property
    def left(self) -> Trapezoid:
        return self.__left

    @property
    def right(self) -> Trapezoid:
        return self.__right

    @left.setter
    def left(self, tr: Trapezoid) -> None:
        self.__left = tr

    @right.setter
    def right(self, tr: Trapezoid) -> None:
        self.__right = tr

    # TODO
    def find_closest_reachable_line(self) -> List[Self]:
        pass


class Trapezoid(Figure):
    def __init__(self, left: List[Line], right: List[Line]) -> None:
        super().__init__()
        self.__left: List[Line] = left
        self.__right: List[Line] = right
        self.__compute_center()

    def __compute_center(self) -> None:
        left_line: Line = Line(self.__left[0].points[0], self.__left[-1].points[1])
        right_line: Line = Line(self.__right[0].points[0], self.__right[-1].points[1])
        center_x: float = (left_line.center.x + right_line.center.x) / 2
        center_y: float = (left_line.center.y + right_line.center.y) / 2
        self.center = Point(center_x, center_y)

    @property
    def left(self) -> List[Line]:
        return self.__left

    @property
    def right(self) -> List[Line]:
        return self.__right
