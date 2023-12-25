from operator import itemgetter

from shapely import Polygon, Point, LineString, MultiLineString, get_coordinates, intersection
from tqdm import tqdm
import time
from configuration_space import ConfigurationSpace
from graph import Graph
from utils import *

l0 = LineString([[-1, -1], [-2, -2]])
l1 = LineString([[0, 0], [0, 0]]) # общая точка
# print(l1)
l2 = LineString([[0, 0], [0, 2]])  # лежит на границе полигона
l3 = LineString([[0, 0], [0, 4]])  # лежит на границе полигона и выходит за его пределы

l4 = LineString([[0.1, 0.1], [0.1, 0.1]])  # пересекает и лежит внутри полигона
l5 = LineString([[-1, -1], [5, 5]])  # пересекает
a = get_coordinates(l4)
print(l4.length)
p1 = Point([0, 0])          # на границе
p2 = Point([-3, -3])        # снаружи

p3 = Point([1, 1])          # внутри

p1 = Polygon([[-1, 0], [-2, 0], [-2, 3]])
p2 = Polygon([[0, 0], [0, 1], [0, 2], [2, 2], [2, 0]])

# p = p1.union(p2)
print(p2.bounds)
# print(get_coordinates(p))

# print(p1.covered_by(p), p2.covered_by(p), p3.covered_by(p))
# print(p1.intersects(p), p2.intersects(p), p3.intersects(p))
# print(p1.touches(p), p2.touches(p), p3.touches(p))
# print(p1.within(p), p2.within(p), p3.within(p))
# print(p.contains(p1), p.contains(p2), p.contains(p3))
# print(l0.touches(p), l1.touches(p), l2.touches(p), l3.touches(p), l4.touches(p), l5.touches(p))
# print(l0.intersects(p), l1.intersects(p), l2.intersects(p), l3.intersects(p), l4.intersects(p), l5.intersects(p))
# print(l0.covered_by(p), l1.covered_by(p), l2.covered_by(p), l3.covered_by(p), l4.covered_by(p), l5.covered_by(p))
# print(l4.crosses(p), l5.crosses(p))
# print(l1.overlaps(p), l1.overlaps(p), l2.overlaps(p), l3.overlaps(p), l4.overlaps(p), l5.overlaps(p))


# arr = np.array(get_coordinates(p)).T
# plt.scatter([p1.x, p2.x, p3.x], [p1.y, p2.y, p3.y], color="orange")
# plt.fill(arr[0], arr[1], 'b', alpha=0.5)
# plt.show()
# print(p)