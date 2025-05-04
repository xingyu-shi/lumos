from typing import List, Optional

from fastapi import FastAPI, APIRouter
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware

from LightRAG.lightrag import QueryParam
from LightRAG.lightrag.utils import logger, csv_string_to_list
from lumos.light_rag import rag, get_related_nodes_edges, QueryResp, QueryKGContext

app = FastAPI()
router = APIRouter(prefix='/api')

class QueryReqDto(BaseModel):
    query: str
    param: Optional[QueryParam] = QueryParam(mode="global", need_context_graph=False, need_context=False, top_k=10)

class QueryRespVectorContextDto(BaseModel):
    id: str
    title: str
    text: str

class QueryRespDto(BaseModel):
    response: str = None
    nodes: Optional[List[dict]] = []
    edges: Optional[List[dict]] = []
    kg_context: Optional[QueryKGContext] = None
    vector_context: Optional[List[QueryRespVectorContextDto]] = None

def _format_vector_context(vector_context: List):
    """
    :param vector_context: List[dict] of vector context with keys (content, created_at)
    :return:
    """
    return [
        QueryRespVectorContextDto(
            title=ctx['content'][:80].replace("\n", ""),
            id=str(idx),
            text=ctx['content']
        ) for idx, ctx in enumerate(vector_context)]

def _csv_list_to_dict(csv_list: List):
    if not csv_list:
        return []

    keys = csv_list[0]
    values = csv_list[1:]
    return [dict(zip(keys, value)) for value in values]

async def _query(query_req: QueryReqDto):
    q_response = await rag.aquery(query_req.query, param=query_req.param)
    q_response = QueryResp.model_validate(q_response)
    nodes, edges = get_related_nodes_edges(q_response.nodes, q_response.edges)
    vector_context = q_response.vector_context if q_response.vector_context else []
    vector_context = _format_vector_context(vector_context)

    if q_response.kg_context:
        q_response.kg_context.entities = _csv_list_to_dict(q_response.kg_context.entities)
        q_response.kg_context.relations = _csv_list_to_dict(q_response.kg_context.relations)
        q_response.kg_context.text_units = _csv_list_to_dict(q_response.kg_context.text_units)

    if q_response.kg_context and len(q_response.kg_context.text_units) != 0:
        vector_context.extend(_format_vector_context(q_response.kg_context.text_units))

    response = QueryRespDto(
        response=q_response.response,
        nodes=nodes,
        edges=edges,
        kg_context=q_response.kg_context,
        vector_context=vector_context,
    )
    return response

@router.post("/query/seg", response_model=QueryRespDto, response_model_exclude_none=True)
async def query(query_req: QueryReqDto):
    query_req.query = f"""
[Background]
I am an customer support engineer.
Please help me with the following customer question.
Make sure to provide the accurate, definite(most important), detailed information.
If you think the question is not clear, please ask for clarification.
[Question]
{query_req.query}
"""
    return await _query(query_req)

@router.post("/query", response_model=QueryRespDto, response_model_exclude_none=True)
async def query(query_req: QueryReqDto) -> QueryRespDto:
    logger.debug(query_req)
    f"""
[Background]
Please help me with the following question.
Make sure to provide the most Accurate, Definite information.
If you think the question is not clear, please ask for clarification.
[Question]
{query_req.query}
    """
    return await _query(query_req)

app.add_middleware(CORSMiddleware, allow_origins="*", allow_methods="*")
app.include_router(router)

if __name__=="__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)