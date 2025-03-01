from typing import Optional, List

from pydantic import BaseModel
from light_rag_openai import *
# from light_rag_local import *

deepseek_r1_think_end_tag = "</think>"

class QueryNode(BaseModel):
    id: str
    entity_name: str
    distance: float
    created_at: float

class QueryEdge(BaseModel):
    id: str
    src_id: str
    tgt_id: str
    distance: float
    created_at: float

class QueryKGContext(BaseModel):
    entities: Optional[List]
    relations: Optional[List]
    text_units: Optional[List]

class QueryResp(BaseModel):
    response: Optional[str] = None
    nodes: Optional[List[QueryNode]] = []
    edges: Optional[List[QueryEdge]] = []
    kg_context: Optional[QueryKGContext] = None
    vector_context: Optional[List] = None
    prompt: Optional[str] = None


def get_related_nodes_edges(nodes, edges):
    node_set = set([node.entity_name for node in nodes])
    for edge in edges:
        node_set.add(edge.src_id)
        node_set.add(edge.tgt_id)
    sub_graph = rag.chunk_entity_relation_graph.subgraph(list(node_set))
    nodes = [{
        "id": node,
        "text": data.get('description'),
        "data":{
            "entity_type": data.get('entity_type'),
            "source_id": data.get('source_id')[:80],
        }
    } for node, data in sub_graph.nodes(data=True)]
    edges = [{
        "from": src,
        "to": tgt,
        "text": data.get('description'),
        "isHideArrow": True,
        "data": {
            "keywords": data.get('keywords'),
            "weight": data.get('weight'),
            "source_id": data.get('source_id')[:80],
        }
    } for src, tgt, data in sub_graph.edges(data=True)]
    return nodes, edges