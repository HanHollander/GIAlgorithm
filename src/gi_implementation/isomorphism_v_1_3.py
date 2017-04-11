from graphs.graph import *
from graphs.graph_io import *
import os
import collections
import time

# SIMPLE ISOMORPHISM DETECTION - more efficient colourization

def graph_isomorphism(g: 'Graph', h: 'Graph'):
    total_automorphisms = 1
    # Combine the two graphs to one graph with two components
    combined_graph, division = add_graphs(g, h)
    # Do an initial colouring based on degree and colourize: get initial coarsest stable partition
    rec_colouring_dict, rec_partitions, max_colour = colour_by_degree(combined_graph)
    # Update the graph labels in the combined graph
    for combined_vertex in combined_graph:
        combined_vertex.label = rec_colouring_dict[combined_vertex]

    if not bijective(rec_partitions) and balanced(rec_partitions, division):
        rec_partitions, rec_colouring_dict, max_colour = colourize(rec_colouring_dict, max_colour, rec_partitions)
    # print("initial partitions:", len(rec_partitions))

    # Create queue and fill
    partitions = rec_partitions
    colouring_dict = rec_colouring_dict
    # If the graph is not bijective but balanced, we can branch
    while not bijective(partitions) and balanced(partitions, division):
        # Find the first non bijective partition
        non_bijective_colour = ""
        for colour in partitions:
            if len(partitions[colour]) != 2:
                non_bijective_colour = colour
                break
        last_stable_partitions = None
        last_stable_max_colour = None
        last_stable_colouring_dict = None
        partition_automorphisms = 0
        g_vertex = partitions[non_bijective_colour][0]
        # Iterate over all the vertices in the first found non bijective partition again
        for vertex_b in partitions[non_bijective_colour]:
            # If the vertex is now in the other graph (h)
            if vertex_b in division[1]:
                h_vertex = vertex_b
                max_colour += 1
                # Change the labels of the g_vertex and h_vertex
                h_vertex.label, g_vertex.label = max_colour, max_colour
                old_colouring_dict = colouring_dict.copy()
                old_max_colour = max_colour
                old_partitions = partitions.copy()
                new_partitions, new_colouring_dict, new_max_colour = colourize(colouring_dict, max_colour, partitions, max_colour)
                # The graphs are isomorphic if the partitions are balanced and bijective at the end of the loop

                # Check if the new graph is balanced
                if balanced(new_partitions, division):
                    # If balanced, update variables and break out of for-loops
                    last_stable_partitions = new_partitions
                    last_stable_max_colour = new_max_colour
                    last_stable_colouring_dict = new_colouring_dict
                    partition_automorphisms += 1

                # If not balanced, revert the changes
                for vertex_d in combined_graph:
                    vertex_d.label = old_colouring_dict[vertex_d]
                colouring_dict = old_colouring_dict
                max_colour = old_max_colour
                partitions = old_partitions
        if last_stable_partitions is not None:
            partitions = last_stable_partitions
            max_colour = last_stable_max_colour
            colouring_dict = last_stable_colouring_dict
            # Update the labels
            for vertex_e in combined_graph:
                vertex_e.label = colouring_dict[vertex_e]
            if partition_automorphisms > 0:
                total_automorphisms = total_automorphisms * partition_automorphisms
        else:
            return combined_graph, False, 0
    result = bijective(partitions) and balanced(partitions, division)
    return combined_graph, result, total_automorphisms


def colourize(colouring_dict, max_colour, partitions, new_color=None):
    print("[DEBUG] START colourize()")
    start_time = time.time()

    biggest_partition_size = 0
    biggest_partition_colour = None
    for colour in partitions:
        size = len(partitions[colour])
        if size > biggest_partition_size:
            biggest_partition_size = size
            biggest_partition_colour = colour

    queue = collections.deque()
    inqueue = []
    if new_color is None:
        for colour in partitions:
            if colour != biggest_partition_colour:
                queue.append(colour)
                inqueue.append(colour)
    else:
        queue.append(new_color)
        inqueue.append(new_color)
    # While there are still unchecked partitions in the queue
    while len(queue) != 0:
        # Refine on partition
        partitions, colouring_dict, max_colour, add_to_queue = refine(queue[0], partitions, colouring_dict, max_colour,
                                                                      inqueue)
        for new_queue_member in add_to_queue:
            queue.append(new_queue_member)
            inqueue.append(new_queue_member)

        queue.popleft()

    print("[DEBUG] END colourize() (took", time.time() - start_time, "s)", len(inqueue),"refines   max_colour =", max_colour)
    return partitions, colouring_dict, max_colour


def refine(refining_colour, partitions, colouring_dict, max_colour, inqueue):
    print("\t[DEBUG] START refine()")
    start_time = time.time()

    add_to_queue = []

    splitting_colours = []
    for splitting_colour in partitions:
        if splitting_colour != refining_colour:
            splitting_colours.append(splitting_colour)

    DEBUGLIST = []  # <------ DEBUG
    for splitting_colour in splitting_colours:
        splitting_partition = partitions[splitting_colour]
        sub_partitions = dict()
        # print(splitting_colour, len(partitions[splitting_colour]))
        for splitting_vertex in splitting_partition:
            #print("started vertices iteration", len(splitting_partition))
            neighbours_in_ref_col = 0
            for splitting_neighbour in splitting_vertex.neighbours:
                if splitting_neighbour.label == refining_colour:
                    neighbours_in_ref_col += 1
            # print("(DEBUG) neighbours_in_ref_col", neighbours_in_ref_col)
            if neighbours_in_ref_col in sub_partitions:
                sub_partitions[neighbours_in_ref_col].append(splitting_vertex)
            else:
                sub_partitions[neighbours_in_ref_col] = [splitting_vertex]
                #print("added some new", len(sub_partitions), neighbours_in_ref_col)
        # print("(DEBUG) splitting colour =", splitting_colour, "sub_partitions size =", len(sub_partitions))

            #print(sub_partitions)

        i = 0
        largest_partition_size = 0
        largest_partition_colour = 0

        sc_in_inqueue = splitting_colour in inqueue
        for amount_of_edges_to_reference_colour in sub_partitions:
            sub_partition = sub_partitions[amount_of_edges_to_reference_colour]
            if len(sub_partition) > largest_partition_size:
                largest_partition_size = len(sub_partition)
                largest_partition_colour = amount_of_edges_to_reference_colour

        if (len(sub_partitions) > 1):
            for amount_of_edges_to_reference_colour in sub_partitions:
                sub_partition = sub_partitions[amount_of_edges_to_reference_colour]
                if i == 0:
                    partitions[splitting_colour] = sub_partition
                    if not sc_in_inqueue and amount_of_edges_to_reference_colour != largest_partition_colour:
                        add_to_queue.append(splitting_colour)
                    DEBUGLIST.append(splitting_colour) # <----- DEBUG
                else:
                    max_colour += 1
                    partitions[max_colour] = sub_partition
                    for new_vertex in sub_partition:
                        new_vertex.label = max_colour
                        colouring_dict[new_vertex] = max_colour
                    if sc_in_inqueue:
                        add_to_queue.append(max_colour)
                    elif amount_of_edges_to_reference_colour != largest_partition_colour:
                        add_to_queue.append(max_colour)
                    DEBUGLIST.append(max_colour)

                i += 1

    print("\t[DEBUG] END refine() (took", time.time() - start_time, "s)")
    return partitions, colouring_dict, max_colour, add_to_queue

def bijective(partitions):
    print("[DEBUG] START bijective()")
    start_time = time.time()
    # Assume the partitions are bijective
    is_bijective = True
    # Now iterate over the partitions
    for colour in partitions:
        # If the lenght of a partition is not 2, the graph is not bijective
        if len(partitions[colour]) != 2:
            is_bijective = False
            break
    print("[DEBUG] END bijective() (took", time.time() - start_time, "s)")
    return is_bijective


def balanced(partitions, division):
    print("[DEBUG] START balanced()")
    start_time = time.time()
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
    print("[DEBUG] END balanced() (took", time.time() - start_time, "s)")
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


def colour_by_degree(graph: 'Graph'):
    # Initialize storage for colourization dictionary (vertex -> colour) and partitions (colour -> [vertex])
    colouring_dict = dict()
    partitions = dict()
    max_degree = 0
    # Get the current max degree/colour and depending on 'recolour' variable, recolour all the vertices
    for vertex in graph.vertices:
        # First give every vertex a colour
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
    current_colour = max_degree
    # Return colouring if the vertices, the partition and a new max colour
    return colouring_dict, partitions, current_colour


def test():
    d = os.path.dirname(__file__)

    filename = os.path.join(d, 'tp320.gr')

    with open(filename) as f:
        G = load_graph(f, Graph, False)

    filename = os.path.join(d, 'tp320.gr')

    with open(filename) as f:
        H = load_graph(f, Graph, False)

    print("Started...")
    start_time = time.time()
    I, result, aut = graph_isomorphism(G, H)
    end_time = time.time()
    print("computation time:", end_time - start_time, "seconds")

    filename = os.path.join(d, 'dotfile.dot')

    with open(filename,  'w') as f1:
        write_dot(I, f1)

    print("result =", result)
    print("automorphisms =", aut)

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
                I, result, aut = graph_isomorphism(GL[i], GL[j])
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
                print("-> automorphisms:", aut)
                print("-> result:", result, "\n")
    total_end_time = time.time()
    print(">total time:", total_end_time - total_start_time)
    print(">isomorphism classes:", classes)

def test3():
    d = os.path.dirname(__file__)

    filename = os.path.join(d, "eg4_7.grl")

    with open(filename) as f:
        GL, options = load_graph(f, Graph, True)

    I = GL[3]

    with open("eg4_7DOT.dot",  'w') as df:
        write_dot(I, df)

# test()
test2('eg4_1026.grl')
# eg4_1026.grl
# >total time: 235.28841519355774
# >isomorphism classes: [[0, 1], [2, 3]]