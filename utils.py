import matplotlib.pyplot as plt
import numpy as np
from shapely import get_coordinates
from shapely import Polygon, Point, LineString, get_coordinates, GeometryCollection


def plot_obstacles(obstacles):
    for obst in obstacles:
        coords = np.array(get_coordinates(obst)).T
        plt.fill(coords[0], coords[1], 'b', alpha=0.5)

def plot_trapezoids(trapezoids):
    for tr in trapezoids:
        tr = tr["trapezoid"]
        coords = np.array(get_coordinates(tr)).T
        plt.fill(coords[0], coords[1], 'orange', alpha=0.5)
        plt.scatter(tr.centroid.x, tr.centroid.y, color="red")


def plot_boundaries(min_limit, max_limit):
    x, y = [min_limit, min_limit, max_limit, max_limit, min_limit], [min_limit, max_limit, max_limit, min_limit,
                                                                     min_limit]
    plt.plot(x, y, linewidth=2, color='b')


def plot_vertical_lines(lines):
    for l in lines:
        coords = l.coords.xy
        plt.plot(coords[0], coords[1], color="red")


def plot_edges(edges, graph_points):
    for edge in edges:
        i, j, _ = edge
        point_i, point_j = graph_points[i], graph_points[j]
        x = [point_i.x, point_j.x]
        y = [point_i.y, point_j.y]
        plt.plot(x, y, linestyle="dashed")


def plot_shortest_path(path, graph_points):
    for i in range(len(path) - 1):
        p1, p2 = graph_points[path[i]], graph_points[path[i + 1]]
        x, y = [p1.x, p2.x], [p1.y, p2.y]
        plt.plot(x, y, linestyle="dashed", color='r')


def plot_start_end_points(start, end):
    plt.scatter(start.x, start.y)
    plt.scatter(end.x, end.y)


def plot_show(min_limit, max_limit):
    plt.xlim(min_limit - 5, max_limit + 5)
    plt.ylim(min_limit - 5, max_limit + 5)
    plt.show()
