import json
import math
import os

import networkx as nx
from pyvis.network import Network

from LightRAG.lightrag.prompt import GRAPH_FIELD_SEP
from lumos.light_rag import config
from lumos.colors import pick_color

def scale_degree(degree):
    return math.log2(degree + 1)

def pretty(text: str):
    if len(text) > 100:
        return text[:100] + "..."
    return text

degree_threshold = 3

# 设置节点大小的范围
min_size = 10
max_size = 40

def nx_to_sigma(graph: nx.Graph):
    degree_dict: dict[str, int]
    degree_dict = dict(graph.degree())
    # 找出最大度和最小度
    max_degree = scale_degree(max(degree_dict.values()))
    min_degree = scale_degree(min(degree_dict.values()))
    def get_node_size(degree: int):
        degree = scale_degree(degree)
        return (degree - min_degree) / (max_degree - min_degree) * (max_size - min_size) + min_size

    orphan_nodes = [node for node in graph.nodes if graph.degree(node) == 0]
    print(f'nodes: {len(list(graph.nodes()))}, edges: {len(list(graph.edges()))}, orphans: {len(orphan_nodes)}')

    # return nx.readwrite.json_graph.node_link_data(G, edges="edges")
    nodes = []
    edges = []
    for node, data in graph.nodes(data=True):
        entity_type = data.get('entity_type')
        # remove the " and ' in the entity_type
        # entity_type = entity_type.replace('"', '').replace("'", '')
        color = pick_color(entity_type)
        description = "Entity Type: {}\nDescription:\n{}\nChunk:{}".format(data.get('entity_type'), data.get('description'), pretty(data.get('source_id'))).replace(GRAPH_FIELD_SEP, "\n")

        nodes.append({
            "id": str(node),
            "label": str(entity_type),
            "description": description,
            # color = color,
            # "x": graph.nodes[node].get('x', 0),  # 如果有位置信息可以加上
            # "y": graph.nodes[node].get('y', 0),
            # "size": get_node_size(degree_dict.get(node))
        })

    for src, dst, data in graph.edges(data=True):
        description = "Keywords: {}\nDescription:\n{}".format(data.get('keywords'), data.get('description')).replace(GRAPH_FIELD_SEP, "\n")
        edges.append({
            "id": f"{src}-{dst}",
            "source": str(src),
            "target": str(dst),
            "description": description
        })

    return {
        "nodes": nodes,
        "edges": edges
    }


if __name__ == '__main__':
    graphml_path = os.path.join(config.WORKING_DIR, "graph_chunk_entity_relation.graphml")
    G = nx.read_graphml(graphml_path)

    sigma_data = nx_to_sigma(G)
    with open(os.path.join(config.WORKING_DIR, "visualize_sigma.json"), 'w') as f:
        f.write(json.dumps(sigma_data))
    print("Graph data saved to graph_data.json")


    # nodes_to_keep = [node for node, degree in G.degree() if degree > degree_threshold]
    # visualize_graph(G.subgraph(nodes_to_keep), os.path.join(config.WORKING_DIR, f"visualize_mini_cas_ems_{degree_threshold}.html"))
