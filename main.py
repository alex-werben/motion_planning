from operator import itemgetter

from shapely import Polygon, Point, LineString, MultiLineString, get_coordinates, intersection
from configuration_space import ConfigurationSpace
import matplotlib.pyplot as plt
import numpy as np

p = Polygon(([0, 0], [2, 2], [0, 4], [4, 2]))
# # p = Polygon([[0, 0], [1, 1], [1, 0]])
l = LineString([[0, 1], [0, 2]])
po = Point([0, 4]).distance(l.centroid)
print(Point([0, 4]).distance(l.centroid))
# arr = [[0., 0.],
#     [2., 2.],
#     [0., 4.],
#     [4., 2.],
#     [0., 0.]]
#
#

cs = ConfigurationSpace()
cs.parse_json("data/my_output.json")
cs.prepare_lines()
cs.divide_space_into_trapezoids()
# print(cs.lines)
print(cs.graph_points)
# print(cs.edges)
for l in cs.lines:
    coords = l.coords.xy
    plt.plot(coords[0], coords[1])
for p in cs.obst:
    coords = np.array(get_coordinates(p)).T
    # for i in range(len(coords)-1):
    # print(coords[0], coords[1])
    plt.plot(coords[0], coords[1])
    # plt.plot(coords)

for edge in cs.edges:
    i, j, _ = edge
    point_i, point_j = cs.graph_points[i], cs.graph_points[j]
    x = [point_i.x, point_j.x]
    y = [point_i.y, point_j.y]
    plt.plot(x, y, linestyle="dashed")

plt.xlim(-1, 21)
plt.ylim(-1, 21)
plt.show()
