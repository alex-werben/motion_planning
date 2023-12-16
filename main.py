from operator import itemgetter

from shapely import Polygon, Point, LineString, MultiLineString, get_coordinates, intersection
from configuration_space import ConfigurationSpace
import matplotlib.pyplot as plt
import numpy as np

# p = Polygon(([0, 0], [2, 2], [0, 4], [4, 2]))
# # p = Polygon([[0, 0], [1, 1], [1, 0]])
# l = LineString([[0, 0], [0, 4]])
# po = Point([0, 4])
#
# arr = [[0., 0.],
#     [2., 2.],
#     [0., 4.],
#     [4., 2.],
#     [0., 0.]]
#
#
# ml = MultiLineString([[[1, 0.5], [1, 1]], [[1, 3], [1, 3.5]]])
# print(ml.geoms[0].coords.xy[1])
cs = ConfigurationSpace()
cs.parse_json("data/my_output.json")
cs.prepare_lines()
for l in cs.lines:
    coords = l.coords.xy
    plt.plot(coords[0], coords[1])
for p in cs.obst:
    coords = np.array(get_coordinates(p)).T
    # for i in range(len(coords)-1):
    # print(coords[0], coords[1])
    plt.plot(coords[0], coords[1])
    # plt.plot(coords)

plt.xlim(-1, 21)
plt.ylim(-1, 21)
plt.show()
