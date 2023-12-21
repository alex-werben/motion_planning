from operator import itemgetter

from shapely import Polygon, Point, LineString, MultiLineString, get_coordinates, intersection
from tqdm import tqdm
import time
from configuration_space import ConfigurationSpace
from graph import Graph
from utils import *


p = Polygon([[0, 0], [0, 2], [1, 0]])
l = LineString([[0, -1], [0, 3]])
# print(l.touches(p))
def measure_time():
    min_limit, max_limit = 0, 100
    total_time = []
    for i in tqdm(range(1, 16)):
        start = time.time()
        cs = ConfigurationSpace(min_limit, max_limit)
        cs.parse_json(f"data/{i}.json")
        cs.prepare_lines()
        cs.divide_space_into_trapezoids()


        graph = Graph(cs.edges, cs.graph_points, cs.start_point_index, cs.end_point_index)
        graph.construct_graph()
        graph.dijkstra()
        graph.reconstruct_path()
        end = time.time()
        total_time.append(end-start)
    with open("data/measurement.txt", 'w') as fp:
        for l in total_time:
            fp.write(str(l))

    plt.plot(range(len(total_time)), total_time)
    plt.grid()
    plt.xlabel("Плотность препятствий")
    plt.ylabel("Время, с")
    plt.show()

# measure_time()

def main():
    min_limit, max_limit = 0, 100
    cs = ConfigurationSpace(min_limit, max_limit)
    cs.parse_json("data/1.json")
    cs.prepare_lines()
    cs.divide_space_into_trapezoids()

    graph = Graph(cs.edges, cs.graph_points, cs.start_point_index, cs.end_point_index)
    graph.construct_graph()
    graph.dijkstra()
    graph.reconstruct_path()

    plot_obstacles(cs.obst)
    plot_boundaries(min_limit, max_limit)
    # plot_vertical_lines(cs.lines)
    # plot_edges(cs.edges, cs.graph_points)
    plot_shortest_path(graph.route, cs.graph_points)
    plot_start_end_points(cs.start_point, cs.end_point)

    plt.xlim(min_limit - 5, max_limit + 5)
    plt.ylim(min_limit - 5, max_limit + 5)
    plt.show()

main()