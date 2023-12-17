class Graph:
    def __init__(self, from_to, coords, start, end):
        self.route = None
        self.graph = None
        self.previous_nodes = None
        self.shortest_path = None
        self.coords = coords
        self.from_to = from_to
        self.start = start
        self.end = end

    def construct_graph(self):
        self.graph = {}
        for pair in self.from_to:
            i, j, weight = pair
            if i not in self.graph:
                self.graph[i] = {}
            if j not in self.graph:
                self.graph[j] = {}
            self.graph[i][j] = weight
            self.graph[j][i] = weight

    def dijkstra(self):
        shortest_path = {}
        previous_nodes = {}
        unvisited = list(self.graph.keys())

        max_value = 10e5
        for k in self.graph.keys():
            shortest_path[k] = max_value

        shortest_path[0] = 0

        while unvisited:
            current_min_node = None
            for node in unvisited:
                if current_min_node is None:
                    current_min_node = node
                elif shortest_path[node] < shortest_path[current_min_node]:
                    current_min_node = node
            neighbors = list(self.graph[current_min_node].keys())
            for neighbor in neighbors:
                value = shortest_path[current_min_node] + self.graph[current_min_node][neighbor]
                if value < shortest_path[neighbor]:
                    shortest_path[neighbor] = value
                    previous_nodes[neighbor] = current_min_node

            unvisited.remove(current_min_node)
        self.previous_nodes = previous_nodes
        self.shortest_path = shortest_path
        # print(self.previous_nodes)
        # print(self.graph)

    def reconstruct_path(self):
        # self.end
        # curr = max(self.previous_nodes.keys()) - 1
        curr = self.end
        path = [curr]
        prev = None
        while prev != 0:
            prev = self.previous_nodes[curr]
            path.append(prev)
            curr = prev
        self.route = path
        print(path)
