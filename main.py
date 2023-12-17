from operator import itemgetter

from shapely import Polygon, Point, LineString, MultiLineString, get_coordinates, intersection
from configuration_space import ConfigurationSpace
from graph import Graph
import matplotlib.pyplot as plt
import numpy as np
from utils import *

def main():
    min_limit, max_limit = 0, 100
    cs = ConfigurationSpace(min_limit, max_limit)
    cs.parse_json("data/maze.json")
    cs.prepare_lines()
    cs.divide_space_into_trapezoids()

    graph = Graph(cs.edges, cs.graph_points, 0, len(cs.graph_points)-1)
    graph.construct_graph()
    graph.dijkstra()
    graph.reconstruct_path()

    plot_obstacles(cs.obst)
    plot_boundaries(min_limit, max_limit)
    # plot_vertical_lines(cs.lines)
    # plot_edges(cs.edges, cs.graph_points)
    plot_shortest_path(graph.route, cs.graph_points)
    plot_start_end_points(cs.start_point, cs.end_point)

    # p = cs.graph_points[37]
    # plt.scatter(p.x, p.y)

    plt.xlim(min_limit - 5, max_limit + 5)
    plt.ylim(min_limit - 5, max_limit + 5)
    plt.show()

main()