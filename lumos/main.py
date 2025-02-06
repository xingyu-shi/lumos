from typing import List, Optional

from fastapi import FastAPI
from pydantic import BaseModel

from LightRAG.lightrag import QueryParam
from LightRAG.lightrag.utils import logger
from lumos.light_rag import rag, get_related_nodes_edges

app = FastAPI()
#
# class QueryReqParamModeDto(str, Enum):
#     Hybrid: str = 'hybrid'
#     Local: str = 'local'
#     Global: str = 'global'
#     Naive: str = 'naive'
#     Mix: str = 'mix'
#
#     def __str__(self):
#         return self.value
#     @classmethod
#     def _missing_(cls, value):
#         return cls.Global
#
# class QueryReqParamDto(BaseModel):
#     mode: Optional[QueryReqParamModeDto] = QueryReqParamModeDto.Global
#     need_context_graph: Optional[bool] = False
#     need_context: Optional[bool] = False
#     top_k: Optional[int] = 20

class QueryReqDto(BaseModel):
    query: str
    param: Optional[QueryParam] = QueryParam(mode="global", need_context_graph=False, need_context=False, top_k=20)

class QueryNodeDto(BaseModel):
    id: str
    entity_name: str
    distance: float
    created_at: float

class QueryEdgeDto(BaseModel):
    id: str
    src_id: str
    tgt_id: str
    distance: float
    created_at: float

class QueryRespDto(BaseModel):
    response: str
    nodes: Optional[List[QueryNodeDto|str]] = []
    edges: Optional[List[QueryEdgeDto|str]] = []
    kg_context: Optional[str] = None
    vector_context: Optional[str] = None


@app.post("/query/seg", response_model=QueryRespDto, response_model_exclude_none=True)
def query(query_req: QueryReqDto):
    query_req.query = f"""
[Background]
I am an customer support engineer.
Please help me with the following customer question.
Make sure to provide the accurate, definite(most important), detailed information.
If you think the question is not clear, please ask for clarification.
[Question]
{query_req.query}
"""
    logger.debug(query_req)
    response = QueryRespDto.model_validate(rag.query(query_req.query, param=query_req.param))
    response.nodes, response.edges = get_related_nodes_edges(response.nodes, response.edges)
    return response

@app.post("/query", response_model=QueryRespDto, response_model_exclude_none=True)
def query(query_req: QueryReqDto) -> QueryRespDto:
    logger.debug(query_req)
    response = QueryRespDto.model_validate(rag.query(query_req.query, param=query_req.param))
    response.nodes, response.edges = get_related_nodes_edges(response.nodes, response.edges)
    return response