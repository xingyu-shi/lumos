import os
from typing import List, Optional

from fastapi import FastAPI, APIRouter
from llama_index.core import VectorStoreIndex
from llama_index.llms.openai import OpenAI
from llama_index.vector_stores.milvus import MilvusVectorStore
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware

from LightRAG.lightrag.utils import logger
from dotenv import load_dotenv


BASE_DIR = os.path.abspath(os.path.dirname(__file__))

load_dotenv(os.path.join(BASE_DIR, "./.env"))

vector_store = MilvusVectorStore(
    uri="./milvus_demo.db",
    dim=1024,
    token=os.environ.get("MILVUS_TOKEN"),
    enable_sparse=True,
    hybrid_ranker="RRFRanker",
    hybrid_ranker_params={"k": 60},
)
index = VectorStoreIndex.from_vector_store(vector_store)

app = FastAPI()
router = APIRouter(prefix='/api')

class QueryReqDto(BaseModel):
    query: str

class QueryModelConfig(BaseModel):
    model: str = os.environ.get("OPENAI_MODEL")
    api_key: str = os.environ.get("OPENAI_API_KEY")
    api_base: str = os.environ.get("OPENAI_API_BASE_URL")

class QueryRespVectorContextDto(BaseModel):
    id: str
    title: str
    text: str

def nodes_to_vector_context(nodes: List[dict]) -> List[QueryRespVectorContextDto]:
    vector_context = []
    for node in nodes:
        vector_context.append(QueryRespVectorContextDto(
            id=node["id"],
            title=node["title"],
            text=node["text"]
        ))
    return vector_context

class QueryRespDto(BaseModel):
    response: str = None
    nodes: Optional[List[dict]] = []
    edges: Optional[List[dict]] = []
    vector_context: Optional[List[QueryRespVectorContextDto]] = None

async def _query(query_req: QueryReqDto, config: QueryModelConfig):
    llm = OpenAI(model=config.model, api_key=config.api_key, api_base=config.api_base)
    query_engine = index.as_query_engine(llm)
    resp = query_engine.query(query_req.query)

    response = QueryRespDto(
        response=resp.text,
        vector_context=nodes_to_vector_context(resp.nodes),
    )
    return response

@router.post("/query", response_model=QueryRespDto, response_model_exclude_none=True)
async def query(query_req: QueryReqDto) -> QueryRespDto:
    logger.debug(query_req)
    f"""
[Background]
Make sure to provide the accurate, definite and detailed information.
Do not provide any information that you are not sure about.
If you think the question is not clear, please ask for clarification.
[Question]
{query_req.query}
    """
    return await _query(query_req, QueryModelConfig())

app.add_middleware(CORSMiddleware, allow_origins="*", allow_methods="*")
app.include_router(router)

if __name__=="__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)