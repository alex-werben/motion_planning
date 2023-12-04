from typing import Any


class Point:
    def __init__(self, x: float, y: float) -> None:
        self.__x: float = x
        self.__y: float = y
        self.__owner: Any = None

    @property
    def x(self) -> float:
        return self.__x

    @property
    def y(self) -> float:
        return self.__y

    @property
    def owner(self) -> Any:
        return self.__owner

    @owner.setter
    def owner(self, owner) -> None:
        self.__owner = owner
