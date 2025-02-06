import logging

from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv

from LightRAG.lightrag import QueryParam
from lumos.light_rag import rag, config

load_dotenv(config.ENV_DIR)

app = FastAPI()

class QueryReqDto(BaseModel):
    query: str
    param: QueryParam = QueryParam(mode="mix", need_context_graph=True, need_context=True, top_k=20)

@app.post("/query/seg")
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
    logging.debug(query_req)
    return rag.query(query_req.query, param=query_req.param)

@app.post("/query")
def query(query_req: QueryReqDto):
    logging.debug(query_req)
    return rag.query(query_req.query, param=query_req.param)