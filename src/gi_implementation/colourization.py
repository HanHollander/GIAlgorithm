from graphs.graph import *
from graphs.graph_io import *
import collections
import os


def colourize(graph: 'Graph', recolour):
    colouring_dict = dict()
    partitions = dict()

    max_degree = 0

    for vertex in graph.vertices:
        if vertex.label != "" and not recolour:
            degree = int(vertex.label)
        else:
            degree = len(vertex.neighbours)
        colouring_dict[vertex] = degree
        if degree in partitions.keys():
            partitions[degree].append(vertex)
        else:
            partitions[degree] = [vertex]
        if degree > max_degree:
            max_degree = degree

    current_colour = max_degree + 1

    stable = False

    while not stable:
        old_colouring_dict = colouring_dict.copy()
        for partition in partitions.values():
            if len(partition) > 1:
                reference_colours = []
                for neighbour in partition[0].neighbours:
                    reference_colours.append(colouring_dict[neighbour])
                equivalent_vertices = [partition[0]]

                for i in range(1, len(partition)):
                    current_vertex_colours = []
                    for neighbour in partition[i].neighbours:
                        current_vertex_colours.append(colouring_dict[neighbour])
                    if collections.Counter(reference_colours) == collections.Counter(current_vertex_colours):
                        equivalent_vertices.append(partition[i])

                if len(equivalent_vertices) != len(partition):
                    for vertex in equivalent_vertices:
                        colouring_dict[vertex] = current_colour
                        partition.remove(vertex)
                    partitions[current_colour] = equivalent_vertices.copy()
                    current_colour += 1
                    break

        if colouring_dict == old_colouring_dict:
            stable = True

    return colouring_dict, partitions
#
#
# def test():
#     d = os.path.dirname(__file__)
#     filename = os.path.join(d, 'eg3.gr')
#
#     with open(filename) as f:
#         G = load_graph(f)
#
#     G = G + G
#
#     colouring_dict = colourize(G, True)
#
#     for vertex in colouring_dict.keys():
#         vertex.label = colouring_dict[vertex]
#
#     filename = os.path.join(d, 'dotfile.dot')
#
#     with open(filename, 'w') as f1:
#         write_dot(G, f1)
#
# test()
