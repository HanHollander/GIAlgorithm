from gi_implementation.colourization import colourize
from graphs.graph import *
from graphs.graph_io import *
import os
import collections
import time

# SIMPLE ISOMORPHISM DETECTION - more efficient colourization

def graph_isomorphism(g: 'Graph', h: 'Graph'):
    # Combine the two graphs to one graph with two components
    combined_graph, division = add_graphs(g, h)
    # Do an initial colouring based on degree and colourize: get initial coarsest stable partition
    starting_colour, rec_colouring_dict, rec_partitions, max_colour = colourize(combined_graph, True)
    # Update the graph labels in the combined graph
    for combined_vertex in combined_graph:
        combined_vertex.label = rec_colouring_dict[combined_vertex]
    # Create queue and add first partition
    queue = collections.deque
    in_queue = []
    queue.appendleft(starting_colour)
    in_queue.append(starting_colour)
    # While there are still unchecked partitions in the queue
    partitions = rec_partitions
    colouring_dict = rec_colouring_dict
    while len(queue) != 0:
        # Refine on partition
        did_refine, new_colours, new_partitions = refine(queue[0], max_colour)
        # Check if the partition split
        if did_refine: # TODO HELP HELP HELP HELP HELP EHLPE HE P HE LE PH FE PEFHL S LSF FSHA
            max_colour += 1
            # Update partitions and colouring dictionary, update the labels of the vertices
            for i in range(0, len(new_partitions)):
                partitions[new_colours[i]] = new_partitions[i]
                for new_vertex in new_partitions[i]:
                    colouring_dict[new_vertex] = new_colours[i]
                    new_vertex.label = colouring_dict[new_vertex]
            # Check if the refined_color is in the queue
            if new_colours[0] in in_queue:
                # Find smallest partition
                smallest_partition = len(new_partitions[1])
                sp_index = 1
                if len(new_partitions) >= 2:
                    for j in range(2, len(new_partitions)):
                        if len(new_partitions[j]) < smallest_partition:
                            smallest_partition = len(new_partitions[j])
                            sp_index = j
                    # Add smallest partition to queue
                    queue.append(new_colours[sp_index])
                    in_queue.append(new_colours[sp_index])
                else:
                    queue.append(new_colours[1])
                    in_queue.append(new_colours[1])
            else:
                # Find smallest partition
                smallest_partition = len(new_partitions[0])
                sp_index = 0
                for j in range(1, len(new_partitions)):
                    if len(new_partitions[j]) < smallest_partition:
                        smallest_partition = len(new_partitions[j])
                        sp_index = j
                # Add smallest partition to queue
                queue.append(new_colours[sp_index])
                in_queue.append(new_colours[sp_index])




        queue.pop()



    # The graphs are isomorphic if the partitions are balanced and bijective at the end of the loop
    result = bijective(partitions) and balanced(partitions, division)
    return combined_graph, result

def refine(ref_partition, max_colour):
    new_partitions = []
    did_refine = False
    new_colour = 0
    # TODO
    return did_refine, new_colour, new_partitions

def bijective(partitions):
    # Assume the partitions are bijective
    is_bijective = True
    # Now iterate over the partitions
    for colour in partitions:
        # If the lenght of a partition is not 2, the graph is not bijective
        if len(partitions[colour]) != 2:
            is_bijective = False
            break
    return is_bijective


def balanced(partitions, division):
    # Assume the partitions are balanced
    is_balanced = True
    # Now iterate over the partitions
    for colour in partitions:
        # Count how many of the nodes in the partition are in which graph
        g = 0
        h = 0
        # If the length of the partition is odd, the partitions cannot be balanced
        if len(partitions[colour]) % 2 != 0:
            is_balanced = False
            break
        else:
            # Iterate over the vertices in the partitions
            for v in partitions[colour]:
                # Count vertices in two components/subgraphs
                if v in division[0]:
                    g += 1
                else:
                    h += 1
            # If there are more in one graph than in the other, the partition is not balanced
            if g != h:
                is_balanced = False
                break
    return is_balanced


def add_graphs(g, h):
    # Initialize variables
    vs = {}
    mv = 0
    division = []
    g_ver = []
    h_ver = []
    # Create a new, empty graph
    new_graph = Graph(False)
    # Iterate over graph g, map old to new vertices and copy all the vertices to the new graph
    for v in g.vertices:
        s = str(mv)
        nv = Vertex(new_graph, s)
        new_graph.add_vertex(nv)
        vs[v] = nv
        mv = mv + 1
        g_ver.append(nv)
    # Do the same for graph h
    for v in h.vertices:
        s = str(mv)
        nv = Vertex(new_graph, s)
        new_graph.add_vertex(nv)
        vs[v] = nv
        mv = mv + 1
        h_ver.append(nv)
    # Using the mapping of old to new vertices, copy all the edges in the old graphs to the new graph
    for e in g.edges:
        new_graph.add_edge(Edge(vs[e.tail], vs[e.head]))
    for e in h.edges:
        new_graph.add_edge(Edge(vs[e.tail], vs[e.head]))
    # Store what vertices are originally from what graph in the new graph
    division.append(g_ver)
    division.append(h_ver)
    return new_graph, division


def copy_graph(g):
    vs = {}
    # Create a new empty graph
    copy = Graph(False)
    # Iterate over all the vertices in the graph, map the old vertices to te new ones and copy them
    for v in g.vertices:
        nv = Vertex(copy, v.label)
        copy.add_vertex(nv)
        vs[v] = nv
    # Using the vertex mapping copy all the edges
    for e in g.edges:
        copy.add_edge(Edge(vs[e.tail], vs[e.head]))
    return copy


def colourize(graph: 'Graph', recolour):
    # Initialize storage for colourization dictionary (vertex -> colour) and partitions (colour -> [vertex])
    colouring_dict = dict()
    partitions = dict()
    max_degree = 0
    # Get the current max degree/colour and depending on 'recolour' variable, recolour all the vertices
    for vertex in graph.vertices:
        # First give every vertex a colour
        if vertex.label != "" and not recolour:
            degree = int(vertex.label)
        else:
            degree = len(vertex.neighbours)
        colouring_dict[vertex] = degree
        # Now partition the vertices and get the max degree/colour
        if degree in partitions.keys():
            partitions[degree].append(vertex)
        else:
            partitions[degree] = [vertex]
        if degree > max_degree:
            max_degree = degree
    starting_colour = max_degree
    # Use the max_degree + 1 as new colour (this colour is not yet in use)
    current_colour = max_degree + 1
    # Return colouring if the vertices, the partition and a new max colour
    return starting_colour, colouring_dict, partitions, current_colour


def test():
    d = os.path.dirname(__file__)

    filename = os.path.join(d, 'eg3.gr')

    with open(filename) as f:
        G = load_graph(f, Graph, False)

    filename = os.path.join(d, 'eg4.gr')

    with open(filename) as f:
        H = load_graph(f, Graph, False)

    start_time = time.time()
    I, result = graph_isomorphism(G, H)
    end_time = time.time()
    print("computation time:", end_time - start_time, "seconds")

    filename = os.path.join(d, 'dotfile.dot')

    with open(filename,  'w') as f1:
        write_dot(I, f1)

    print("result =", result)

def test2(filepathname):
    d = os.path.dirname(__file__)

    filename = os.path.join(d, filepathname)

    with open(filename) as f:
        GL, options = load_graph(f, Graph, True)

    pairs = []
    classes = []
    total_start_time = time.time()
    for i in range(0, len(GL)):
        for j in range(i + 1, len(GL)):
            already_in_class = False
            for iso_class in classes:
                if i in iso_class and j in iso_class:
                    already_in_class = True
                    break
            if already_in_class == False:
                print("> compare", i, "and", j)
                start_time = time.time()
                I, result = graph_isomorphism(GL[i], GL[j])
                if result == True:
                    pair = [i, j]
                    pairs.append(pair)
                    added = False
                    if len(classes) == 0:
                        classes.append(pair)
                    else:
                        for iso_class in classes:
                            if pair[0] in iso_class and pair[1] in iso_class:
                                added = True
                                break
                            elif pair[0] in iso_class and pair[1] not in iso_class:
                                iso_class.append(pair[1])
                                added = True
                                break
                            elif pair[1] in iso_class and pair[0] not in iso_class:
                                iso_class.append(pair[0])
                                added = True
                                break
                        if added == False:
                            classes.append(pair)
                end_time = time.time()
                print("-> computation time:", end_time - start_time, "seconds")
                print("-> result:", result, "\n")
    total_end_time = time.time()
    print(">total time:", total_end_time - total_start_time)
    print(">isomorphism classes:", classes)

test2('agInet.grl')
