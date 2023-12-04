from abc import ABC, abstractmethod
from point import Point
from typing import List


class Obstacle(ABC):
    def __init__(self, points: List[Point]) -> None:
        self.__points: List[Point] = points
        self.__x_borders, self.__y_borders = self.__compute_borders()


    def point_crosses_obstacle_horizontally(self, p: Point) -> bool:
        """
        Method checks if point crosses obstacle horizontally.

        :param p:
        :return:
        """
        return True if self.x_borders[0] < p.x < self.x_borders[1] else False

    def __compute_borders(self) -> List[List[float]]:
        left_x, left_y = 101.0, 101.0
        right_x, right_y = -1.0, -1.0
        for p in self.__points:
            if p.x < left_x:
                left_x = p.x
            if p.x > right_x:
                right_x = p.x
            if p.y < left_y:
                left_y = p.y
            if p.y > right_y:
                right_y = p.y
        return [[left_x, right_x], [left_y, right_y]]

    @abstractmethod
    def point_intersects_obstacle(self, p: Point) -> bool:
        pass

    @property
    def x_borders(self) -> List[float]:
        return self.__x_borders

    @property
    def points(self) -> List[Point]:
        return self.__points

    @points.setter
    def points(self, points: List[Point]) -> None:
        del self.__points
        self.__points = points


class Polyline(Obstacle):
    def __init__(self, points: List[Point], size: float = 1.0) -> None:
        super().__init__(points)
        self.__size: float = size

    def point_intersects_obstacle(self, p: Point) -> bool:
        x1, y1 = self.points[0].x, self.points[0].y
        x2, y2 = self.points[1].x, self.points[1].y
        slope = (y2 - y1) / (x2 - x1)
        p_on = (p.y - y1) == slope * (p.x - x1)
        p_between = (min(x1, x2) <= p.x <= max(x1, x2)) and (min(y1, y2) <= p.y <= max(y1, y2))
        return p_on and p_between

    @property
    def size(self) -> float:
        return self.__size


class Polygon(Obstacle):
    def __init__(self, points: List[Point]) -> None:
        super().__init__(points)

    # TODO
    def point_intersects_obstacle(self, p: Point) -> bool:
        for i in range(len(self.points)):
            p1, p2 = self.points[-1 + i], self.points[i]
            line = Polyline([p1, p2])
            if line.point_intersects_obstacle(p):
                return True
        return False


class Polypoint(Obstacle):
    def __init__(self, p: Point, size: float = 1.0) -> None:
        super().__init__([p])
        self.__size: float = size

    def point_intersects_obstacle(self, p: Point) -> bool:
        return True if self.points[0].x == p.x and self.points[1].y == p.y else False

    @property
    def size(self) -> float:
        return self.__size
