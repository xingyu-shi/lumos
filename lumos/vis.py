import os

import networkx as nx
from accelerate.commands.config.update import description
from pyvis.network import Network
from scipy.cluster.hierarchy import weighted

from lumos.colors import pick_color

WORKING_SPACE = "workspace_extracted_entity_types"
BASEDIR = os.path.abspath(os.path.dirname(__file__))
WORKING_DIR = os.path.join(BASEDIR, WORKING_SPACE)

graphml_path = os.path.join(WORKING_DIR, "graph_chunk_entity_relation.graphml")

graph = nx.read_graphml(graphml_path)
net = Network(notebook=True, filter_menu=True, cdn_resources='remote')


# 设置节点大小的范围
min_size = 10
max_size = 40

degree_dict: dict[str, int]
degree_dict = dict(graph.degree())
# 找出最大度和最小度
max_degree = max(degree_dict.values())
min_degree = min(degree_dict.values())
def get_node_size(degree: int):
    return (degree - min_degree) / (max_degree - min_degree) * (max_size - min_size) + min_size

for node, data in graph.nodes(data=True):
    entity_type = data.get('entity_type')
    # remove the " and ' in the entity_type
    # entity_type = entity_type.replace('"', '').replace("'", '')
    color = pick_color(entity_type)
    net.add_node(node,
                 label=node,
                 color=color,
                 size=get_node_size(degree_dict.get(node)),
                 title="entity type: {}\ndescription:{}".format(data.get('entity_type'), data.get('description'))
                 )

for src, dst, data in graph.edges(data=True):
    net.add_edge(src, dst, description=data.get('description'), weighte=data.get('weight'), title="keywords: {}\ndescription:{}".format(data.get('keywords'), data.get('description')))

# net.from_nx(graph)
net.show(os.path.join(BASEDIR, WORKING_SPACE, "example.html"))
