# https://www.geeksforgeeks.org/floyd-warshall-algorithm-dp-16/
# https://www.geeksforgeeks.org/detecting-negative-cycle-using-floyd-warshall/

import networkx as nx
import matplotlib.pyplot as plt
import numpy as np


def draw_graph(n, distances, edges):
    # Create directed graph
    G = nx.DiGraph()

    # Add nodes (vertices)
    for i in range(n):
        G.add_node(i)

    # Add edges from the input data and the shortest distances
    for u, v, weight in edges:
        G.add_edge(u, v, weight=weight)

    # Use the shortest distances to update edges if needed
    for i in range(n):
        for j in range(n):
            if distances[i][j] != float('inf') and i != j:
                # Add edges only if the distance is finite
                if not G.has_edge(i, j):
                    G.add_edge(i, j, weight=distances[i][j])

    # Define node labels
    node_labels = {i: f'X{i + 1}' for i in range(n)}

    # Draw the graph with labels
    pos = nx.spring_layout(G)  # Positioning of nodes
    plt.figure(figsize=(8, 6))
    nx.draw(G, pos, with_labels=True, node_size=3000, node_color="skyblue", font_size=12, font_weight='bold',
            arrows=True)

    # Edge labels (weights)
    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

    # Display the graph
    plt.title("Graph of Shortest Paths")
    plt.show()

def floyd_warshall(n, edges):
    INF = float('inf')
    d = np.full((n, n), INF)
    next_node = np.full((n, n), -1)

    # Initialize the diagonal
    for i in range(n):
        d[i][i] = 0

    # Add the edges
    for u, v, weight in edges:
        d[u][v] = weight
        next_node[u][v] = v

    # Apply Floyd-Warshall
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if d[i][k] + d[k][j] < d[i][j]:
                    d[i][j] = d[i][k] + d[k][j]
                    next_node[i][j] = next_node[i][k]

    # If distance of any vertex from itself becomes negative, then
    # there is a negative weight cycle.
    for i in range(n):
        if d[i][i] < 0:
            negative_cycle = []
            current = i
            for _ in range(n):
                current = next_node[current][i]

            start = current
            while True:
                negative_cycle.append(int(current))
                current = next_node[current][i]
                if current == start and len(negative_cycle) > 1:
                    break

            return f"Inconsistent problem: Negative cycle {negative_cycle}"

    # Find a solution
    solution = [float(d[0][j]) for j in range(n)]
    return d, solution

if __name__ == '__main__':
    # Based on the data from the exercise
    # Vertexes: X1 = 0, X2 = 1, X3 = 2, X4 = 3
    # Edges (u, v, weight): u -> v  weight
    edges = [
        (0, 1, 40),     # X1 -> X2: d(X1, X2) <= 40
        (1, 0, -30),    # X2 -> X1: d(X2, X1) <= -30
        (2, 3, 15),     # X3 -> X4: d(X3, X4) <= 15
        (3, 2, -5),     # X4 -> X3: d(X4, X3) <= -5
        (1, 3, 15),     # X2 -> X4: d(X2, X4) <= 15
        (3, 1, 0)       # X4 -> X2: d(X4, X2) <= 0
    ]

    # Edges for detective negative circle
    # edges = [
    #     (0, 1, -40),
    #     (1, 0, -30),
    #     (2, 3, -15),
    #     (3, 2, -5),
    #     (1, 3, 15),
    #     (3, 1, 0)
    # ]

    # With 4 vertexes
    n = 4
    result  = floyd_warshall(n, edges)

    if isinstance(result, str):
        print(result)  # If there is a negative circle, print it
    else:
        distances, solution = result
        print("Table of shortest distances:")
        print(distances)
        print("Solution:")
        print(solution)
        draw_graph(n, distances, edges)

    """
    Η λύση που δίνεται είναι [0.0, 40.0, 50.0, 55.0] άρα
        - Η Χ1 ξεκινά στο χρόνο 0
        - Η X2 ξεκινά μετά από 40΄
        - Η X3 ξεκινά μετά από 50΄
        - Η X4 ξεκινά μετά από 55΄
    Άρα :
        - Η Μαρία φεύγει απο το σπίτι της 8:00
        - Η Μαρία φτάνει στην δουλεία 8:40
        - Η Ελένη φεύγει απο το σπίτι της 8:50
        - Η Ελένη φτάνει στην δουλεία 8:55
    """