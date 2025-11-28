def bfs_topology(start_nodes, network_data):
    from collections import deque
    
    if isinstance(start_nodes, list):
        start_nodes = tuple(start_nodes)  # Convert list to tuple if necessary
    
    visited = set()
    graph = {}
    queue = deque([start_nodes])

    while queue:
        node = queue.popleft()
        
        if isinstance(node, list):
            node = tuple(node)  # Convert list to tuple if necessary
            
        if node not in visited:
            visited.add(node)
            neighbors = network_data.get(node, [])
            
            # Convert all list neighbors to tuple
            neighbors = [tuple(neighbor) if isinstance(neighbor, list) else neighbor for neighbor in neighbors]
            
            graph[node] = neighbors

            for neighbor in neighbors:
                if neighbor not in visited:
                    queue.append(neighbor)
                    
    return graph

def construct_topology(bfs_result):
    import networkx as nx
    G = nx.Graph()
    
    for node, neighbors in bfs_result.items():
        for neighbor in neighbors:
            G.add_edge(node, neighbor)
    
    return G

def visualize_topology(graph):
    import matplotlib.pyplot as plt
    import networkx as nx

    pos = nx.spring_layout(graph)
    nx.draw(graph, pos, with_labels=True)
    plt.show()
