from operator import itemgetter

from shapely import Polygon, Point, LineString, MultiLineString, get_coordinates, intersection
from tqdm import tqdm
import time
from configuration_space import ConfigurationSpace
from graph import Graph
from utils import *

l0 = LineString([[-1, -1], [-2, -2]])
l1 = LineString([[0, 0], [-2, 0]]) # общая точка
l2 = LineString([[0, 0], [0, 2]])  # лежит на границе полигона
l3 = LineString([[0, 0], [0, 4]])  # лежит на границе полигона и выходит за его пределы

l4 = LineString([[0.5, 0.5], [1, 1]])  # пересекает и лежит внутри полигона
l5 = LineString([[-1, -1], [5, 5]])  # пересекает

p = Polygon([[0, 0], [0, 2], [1, 3], [1, -2]])
print(l0.touches(p), l1.touches(p), l2.touches(p), l3.touches(p), l4.touches(p), l5.touches(p))
print(l0.intersects(p), l1.intersects(p), l2.intersects(p), l3.intersects(p), l4.intersects(p), l5.intersects(p))
print(l0.covered_by(p), l1.covered_by(p), l2.covered_by(p), l3.covered_by(p), l4.covered_by(p), l5.covered_by(p))
print(l0.crosses(p), l1.crosses(p), l2.crosses(p), l3.crosses(p), l4.crosses(p), l5.crosses(p))
# print(l1.overlaps(p), l1.overlaps(p), l2.overlaps(p), l3.overlaps(p), l4.overlaps(p), l5.overlaps(p))


arr = np.array(get_coordinates(p)).T

# plt.fill(arr[0], arr[1], 'b')
# plt.show()
# print(p)