import os
from typing import Optional, List

from openai import BaseModel

from LightRAG.lightrag import LightRAG
from LightRAG.lightrag.llm import openai_embedding, openai_complete_if_cache, GPTKeywordExtractionFormat
from LightRAG.lightrag.utils import EmbeddingFunc
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

load_dotenv(os.path.join(BASE_DIR, "../.env"))

# ================ config ====================
class CFG:
    WORKSPACE = os.environ.get("WORKSPACE", "workspace")
    WORKING_DIR = os.path.join(BASE_DIR, "../" , WORKSPACE)

    if not os.path.exists(WORKING_DIR):
        os.mkdir(WORKING_DIR)
    CHUNK_TOKEN_SIZE = 1200

# ================ end config ====================
config = CFG()

def get_llm_complete_func(model, base_url, api_key=None):
    async def __complete(prompt, system_prompt=None, history_messages=[],
                   keyword_extraction=False, **kwargs):
        keyword_extraction = kwargs.pop("keyword_extraction", None)
        if keyword_extraction:
            kwargs["response_format"] = GPTKeywordExtractionFormat
        return await openai_complete_if_cache(
            model,
            prompt,
            system_prompt=system_prompt,
            history_messages=history_messages,
            base_url=base_url,
            api_key=api_key,
            **kwargs
        )
    return __complete

llm_complete = get_llm_complete_func(
    os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
    os.environ.get("OPENAI_API_BASE_URL"),
    os.environ.get("OPENAI_API_KEY")
)

llm_embedding = EmbeddingFunc(
    embedding_dim=1536, max_token_size=8192,
    func=lambda texts:openai_embedding(
        texts,
        base_url=os.environ.get("OPENAI_API_BASE_URL"),
        api_key=os.environ.get("OPENAI_API_KEY")
    )
)

rag = LightRAG(
    working_dir=config.WORKING_DIR,
    llm_model_func=llm_complete,
    embedding_func=llm_embedding,
    addon_params={
        "language": "English or Chinese",
        "entity_types": ["organization", "person", "geo", "event", "category", "technical-term"],
    },
    chunk_token_size=config.CHUNK_TOKEN_SIZE,
    enable_embedding_func_cache = False,
    enable_llm_cache = False,
    # llm_model_func=gpt_4o_complete
)

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
    vector_context: Optional[str] = None
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