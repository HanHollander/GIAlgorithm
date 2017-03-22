import resources.graphs.practicum.graph
from resources.graphs.practicum.graph_io import load_graph, write_dot # graphIO import graphs.py, so we do not need to import it here.
import os
import math

# Use these options to change the tests:

TEST_BELLMAN_FORD_DIRECTED = True
TEST_BELLMAN_FORD_UNDIRECTED = False
TEST_DIJKSTRA_DIRECTED = True
TEST_DIJKSTRA_UNDIRECTED = False

WRITE_DOT_FILES = True

# Use this to select the graphs to test your algorithms on:
# TestInstances = ["weightedexample.gr"]
# TestInstances = ["testgraphs2017/graph1.gr"]
# TestInstances=["randomplanar.gr"]
# TestInstances = ["randomplanar10.gr"]
# TestInstances=["bd.gr","bbf.gr"]; WriteDOTFiles=False
# TestInstances=["bbf2000.gr"]; WriteDOTFiles=False
# TestInstances=["bbf200.gr"]
# TestInstances=["negativeweightexample.gr"]
# TestInstances=["negativeweightcycleexample.gr"]
# TestInstances=["WDE100.gr","WDE200.gr","WDE400.gr","WDE800.gr","WDE2000.gr"]; WriteDOTFiles=False
# TestInstances=["weightedex500.gr"];	WriteDOTFiles=False
TestInstances = ["testgraphs2017/graph1.gr", "testgraphs2017/graph2.gr", "testgraphs2017/graph3.gr",
                 "testgraphs2017/graph4.gr", "testgraphs2017/graph5.gr", "testgraphs2017/graph6.gr", ]


USE_UNSAFE_GRAPH = False


def bellman_ford_undirected(graph, start):
    """
    Arguments: <graph> is a graph object, where edges have integer <weight>
        attributes,	and <start> is a vertex of <graph>.
    Action: Uses the Bellman-Ford algorithm to compute all vertex distances
        from <start> in <graph>, and assigns these values to the vertex attribute <dist>.
        Optional: assigns the vertex attribute <in_edge> to be the incoming
        shortest path edge, for every reachable vertex except <start>.
        <graph> is viewed as an undirected graph.
    """
    # Initialize the vertex attributes:
    for v in graph.vertices:
        v.dist = math.inf
        v.in_edge = None

    start.dist = 0

    # Insert your code here.


def bellman_ford_directed(graph, start):
    """
    Arguments: <graph> is a graph object, where edges have integer <weight>
        attributes,	and <start> is a vertex of <graph>.
    Action: Uses the Bellman-Ford algorithm to compute all vertex distances
        from <start> in <graph>, and assigns these values to the vertex attribute <dist>.
        Optional: assigns the vertex attribute <in_edge> to be the incoming
        shortest path edge, for every reachable vertex except <start>.
        <graph> is viewed as a directed graph.
    """
    # Initialize the vertex attributes:
    for v in graph.vertices:
        v.dist = math.inf
        v.in_edge = None

    start.dist = 0

    for count in range(0, len(graph.vertices) - 1):
        for v in graph.vertices:
            for e in v.incidence:
                if e.tail == v and e.tail.dist != math.inf and e.weight + e.tail.dist < e.head.dist:
                    e.head.dist = e.weight + e.tail.dist
                    e.head.in_edge = e.tail

    for v in graph.vertices:
        for e in v.incidence:
            if e.tail == v and e.tail.dist != math.inf and e.weight + e.tail.dist < e.head.dist:
                print('Negative weight cycle detected!')
                return False

    return True


def dijkstra_undirected(graph, start):
    """
    Arguments: <graph> is a graph object, where edges have integer <weight>
        attributes,	and <start> is a vertex of <graph>.
    Action: Uses Dijkstra's algorithm to compute all vertex distances
        from <start> in <graph>, and assigns these values to the vertex attribute <dist>.
        Optional: assigns the vertex attribute <in_edge> to be the incoming
        shortest path edge, for every reachable vertex except <start>.
        <graph> is viewed as an undirected graph.
    """
    # Initialize the vertex attributes:
    for v in graph.vertices:
        v.dist = math.inf
        v.in_edge = None

    start.dist = 0

    # Insert your code here.


def dijkstra_directed(graph, start):
    """
    Arguments: <graph> is a graph object, where edges have integer <weight>
        attributes,	and <start> is a vertex of <graph>.
    Action: Uses Dijkstra's algorithm to compute all vertex distances
        from <start> in <graph>, and assigns these values to the vertex attribute <dist>.
        Optional: assigns the vertex attribute <in_edge> to be the incoming
        shortest path edge, for every reachable vertex except <start>.
        <graph> is viewed as a directed graph.
    """
    # Initialize the vertex attributes:
    for v in graph.vertices:
        v.dist = math.inf
        v.in_edge = None

    start.dist = 0

    unvisited = graph.vertices
    cur_vertex = None

    while len(unvisited) > 0:
        lowest_dist = math.inf
        for v in unvisited:
            if v.dist <= lowest_dist:
                cur_vertex = v
                lowest_dist = cur_vertex.dist
        unvisited.remove(cur_vertex)
        for e in cur_vertex.incidence:
            if e.tail == cur_vertex and e.weight + e.tail.dist < e.head.dist:
                e.head.dist = e.weight + e.tail.dist
                e.head.in_edge = e.tail



            # cur_lowest_cost = math.inf
        # for e in cur_ver.incidence:
        #     if e.tail == cur_ver and e.weight < cur_lowest_cost and e.head in unvisited:
        #         cur_edge = e
        # if cur_edge.tail.dist + cur_edge.weight < cur_edge.head.dist:
        #     cur_edge.head.dist = cur_edge.tail.dist + cur_edge.weight
        #     cur_edge.head.in_edge = cur_edge.tail
        # print(cur_ver, cur_edge.head)
        # unvisited.remove(cur_ver)
        # if cur_edge.head in unvisited:
        #     cur_ver = cur_edge.head


##############################################################################
#
# Below is test code that does not need to be changed.
#
##############################################################################

def print_max_dist(graph):
    unreachable = False
    numreachable = 0
    sorted_vertices = sorted(graph.vertices, key=lambda v: v.label)
    remote = sorted_vertices[0]
    for v in graph.vertices:
        if v.dist == math.inf:
            unreachable = True
            # print("Vertex", v,"is unreachable")
        else:
            numreachable += 1
            if v.dist > remote.dist:
                remote = v
    print("Number of reachable vertices:", numreachable, "out of", len(graph))
    print("Largest distance:", remote.dist, "For vertex", remote)


def prepare_drawing(graph):
    for e in graph.edges:
        e.colornum = 0
    for v in graph.vertices:
        if hasattr(v, "in_edge") and v.in_edge is not None:
            v.in_edge.colornum = 1
    for v in graph:
        v.label = str(v.dist)


def do_testalg(testalg, G):
    if testalg[1]:
        print("\n\nTesting", testalg[0])
        startt = time()
        if testalg[0] == "Kruskal":
            ST = testalg[2](G)
            totalweight = 0
            for e in ST:
                totalweight += e.weight
        else:
            sorted_vertices = sorted(G.vertices, key=lambda v: v.label)
            testalg[2](G, sorted_vertices[0])
        endt = time()
        print("Elapsed time in seconds:", endt - startt)

        if testalg[0] != "Kruskal":
            print_max_dist(G)
            prepare_drawing(G)
        else:
            if len(ST) < len(G.vertices) - 1:
                print("Total weight of maximal spanning forest:", totalweight)
            else:
                print("Total weight of spanning tree:", totalweight)
            for e in G.edges:
                e.colornum = 0
            for e in ST:
                e.colornum = 1
            for v in G.vertices:
                v.label = v._label

        if WRITE_DOT_FILES:
            with open(os.path.join(os.getcwd(), testalg[3] + '.dot'), 'w') as f:
                write_dot(G, f, directed=testalg[4])


if __name__ == "__main__":
    from time import time

    for FileName in TestInstances:
        # Tuple arguments below:
        # First: printable string
        # Second: Boolean value
        # Third: Function
        # Fourth: Filename
        # Fifth: Whether output should be directed
        for testalg in [("Bellman-Ford, undirected", TEST_BELLMAN_FORD_UNDIRECTED, bellman_ford_undirected,
                         "BellmanFordUndirected", False),
                        ("Bellman-Ford, directed", TEST_BELLMAN_FORD_DIRECTED, bellman_ford_directed, "BellmanFordDirected",
                         True),
                        ("Dijkstra, undirected", TEST_DIJKSTRA_UNDIRECTED, dijkstra_undirected, "DijkstraUndirected",
                         False),
                        ("Dijkstra, directed", TEST_DIJKSTRA_DIRECTED, dijkstra_directed, "DijkstraDirected", True)]:
            if USE_UNSAFE_GRAPH:
                print("\n\nLoading graph", FileName, "(Fast graph)")
                with open(os.path.join(os.getcwd(), FileName)) as f:
                    G = load_graph(f, graph.Graph)
            else:
                print("\n\nLoading graph", FileName)
                with open(os.path.join(os.getcwd(), FileName)) as f:
                    G = load_graph(f)

            for i, vertex in enumerate(list(G.vertices)):
                vertex.colornum = i
            do_testalg(testalg, G)