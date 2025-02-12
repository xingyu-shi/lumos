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
    return [
        QueryRespVectorContextDto(
            title=ctx[:80].replace("\n", ""),
            id=str(idx),
            text=ctx
        ) for idx, ctx in enumerate(vector_context)]

async def _query(query_req: QueryReqDto):
    q_response = await rag.aquery(query_req.query, param=query_req.param)
    q_response = QueryResp.model_validate(q_response)
    nodes, edges = get_related_nodes_edges(q_response.nodes, q_response.edges)
    vector_context = q_response.vector_context.split("--New Chunk--") if q_response.vector_context else []
    vector_context = _format_vector_context(vector_context)

    if len(q_response.kg_context.text_units) != 0:
        vector_context.extend(_format_vector_context([line[1] for line in q_response.kg_context.text_units[1:]]))

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
    return await _query(query_req)

app.add_middleware(CORSMiddleware, allow_origins="*", allow_methods="*")
app.include_router(router)

if __name__=="__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)