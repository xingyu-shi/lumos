import os

import networkx as nx
from accelerate.commands.config.update import description
from pyvis.network import Network
from scipy.cluster.hierarchy import weighted

BASEDIR = os.path.abspath(os.path.dirname(__file__))
WORKING_DIR = os.path.join(BASEDIR, './workspace/dickens')

graphml_path = os.path.join(WORKING_DIR, "graph_chunk_entity_relation.graphml")

graph = nx.read_graphml(graphml_path)
net = Network(notebook=True, filter_menu=True, cdn_resources='remote')

entity_type_to_color = {
    '"organization"': "#4CAF50",  # 绿色
    '"person"': "#9C27B0",        # 紫色
    '"geo"': "#00ACC1",           # 青色
    '"event': "#FF9800",         # 橙色
    '"category"': "#8BC34A",      # 浅绿色
    '"unknown"': "#FFEB3B",       # 黄色
}


for node, data in graph.nodes(data=True):
    entity_type = data.get('entity_type')
    # remove the " and ' in the entity_type
    # entity_type = entity_type.replace('"', '').replace("'", '')
    color = entity_type_to_color.get(entity_type.lower())
    net.add_node(node, label=node, color=color, title="entity type: {}\ndescription:{}".format(data.get('entity_type'), data.get('description')))

for src, dst, data in graph.edges(data=True):
    net.add_edge(src, dst, description=data.get('description'), weighte=data.get('weight'), title="keywords: {}\ndescription:{}".format(data.get('keywords'), data.get('description')))

# net.from_nx(graph)
net.show(os.path.join(BASEDIR, "example.html"))
