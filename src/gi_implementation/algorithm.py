from gi_implementation.colourization import colourize
from graphs.graph import *
from graphs.graph_io import *
import os
import collections
import time


def graph_isomorphism(g: 'Graph', h: 'Graph'):
    # Combine the two graphs to one graph with two components
    combined_graph, division = add_graphs(g, h)
    # Do an initial colouring based on degree and colourize
    colouring_dict, partitions, max_colour = colourize(combined_graph, True)
    # Update the graph labels in the combined graph
    for vertex in combined_graph:
        vertex.label = colouring_dict[vertex]
    # If the graph is not bijective but balanced, we can branch
    while not bijective(partitions) and balanced(partitions, division):
        # Find the first non bijective partition
        # TODO optimize this by doing it in bijective() function, already iterating over it there
        old_colouring_dict = colouring_dict
        non_bijective_colour = ""
        for colour in partitions:
            if len(partitions[colour]) != 2:
                non_bijective_colour = colour
                break
        # Set a variable used for breaking out of two loops at once
        doublebreak = False
        # Iterate over all the vertices in the first found non bijective partition
        for vertex in partitions[non_bijective_colour]:
            # If the vertex is in the component of the new graph that previously (before combining) was one graph (g)
            if vertex in division[0]:
                g_vertex = vertex
                # Iterate over all the vertices in the first found non bijective partition again
                for vertex in partitions[non_bijective_colour]:
                    # If the vertex is now in the other graph (h)
                    if vertex in division[1]:
                        h_vertex = vertex
                        # Change the labels of the g_vertex and h_vertex
                        h_vertex.label, g_vertex.label = max_colour, max_colour
                        # Colourize the new graph
                        new_colouring_dict, new_partitions, new_max_colour = colourize(combined_graph, False)
                        # Update the labels
                        for vertex in combined_graph:
                            vertex.label = new_colouring_dict[vertex]
                        # Check if the new graph is balanced
                        if balanced(new_partitions, division):
                            # If balanced, update variables and break out of for-loops
                            partitions = new_partitions
                            max_colour = new_max_colour
                            colouring_dict = new_colouring_dict
                            doublebreak = True
                            break
                        else:
                            # If not balanced, revert the changes
                            for vertex in combined_graph:
                                vertex.label = old_colouring_dict[vertex]
                if doublebreak:
                    break
    # The graphs are isomorphic if the partitions are balanced and bijective at the end of the loop
    result = bijective(partitions) and balanced(partitions, division)
    return combined_graph, result


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
    # Use the max_degree + 1 as new colour (this colour is not yet in use)
    current_colour = max_degree + 1
    # Assume the partitioning is not yet stable
    stable = False
    # While it is not stable
    while not stable:
        # Remember the old colouring, in order to check afterwards if changes were made
        old_colouring_dict = colouring_dict.copy()
        # Iterate over the partitions (the lists of vertices)
        for partition in partitions.values():
            # Something only can happen if the partition size is larger than 1
            if len(partition) > 1:
                # Store the colours of the neighbours of the first vertex in a partition
                reference_colours = []
                for neighbour in partition[0].neighbours:
                    reference_colours.append(colouring_dict[neighbour])
                # Since a vertex is equivalent to itself, initialize the list with equivalent vertices with itself in it
                equivalent_vertices = [partition[0]]
                # Iterate over all the other vertices in the partition
                for i in range(1, len(partition)):
                    # Get the colours of the neighbours of the current vertex that is being iterated over
                    current_vertex_colours = []
                    for neighbour in partition[i].neighbours:
                        current_vertex_colours.append(colouring_dict[neighbour])
                    # If the current neighbour colours match the reference colours, add vertex to equivalent vertices
                    if collections.Counter(reference_colours) == collections.Counter(current_vertex_colours):
                        equivalent_vertices.append(partition[i])
                # If not all vertices in the partition are equivalent (have equivalently coloured neighbourhoods)
                if len(equivalent_vertices) != len(partition):
                    # Create a new partition and update the vertex colours
                    for vertex in equivalent_vertices:
                        colouring_dict[vertex] = current_colour
                        partition.remove(vertex)
                    partitions[current_colour] = equivalent_vertices.copy()
                    # Increment the "new" colour (for the next partition) by 1
                    current_colour += 1
                    # Break out of the for loop, so a stable check can be done
                    break
        # Check if stable, and if so, break out of the while loop
        if colouring_dict == old_colouring_dict:
            stable = True
    # Return colouring if the vertices, the partition and a new max colour
    return colouring_dict, partitions, current_colour + 1


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

test2('eg4_7.grl')

