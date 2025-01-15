import os

from LightRAG.lightrag import LightRAG, QueryParam
from LightRAG.lightrag.llm import gpt_4o_mini_complete, openai_embedding
from LightRAG.lightrag.utils import EmbeddingFunc

from dotenv import load_dotenv

from lumos import config

load_dotenv('../.env')


rag = LightRAG(
    working_dir=config.WORKING_DIR,
    llm_model_func=lambda *args, **kwargs: gpt_4o_mini_complete(*args, **kwargs, base_url=os.environ.get("OPENAI_API_BASE_URL")),
    embedding_func=EmbeddingFunc(embedding_dim=1536, max_token_size=8192,
                                 func=lambda texts:openai_embedding(texts, base_url=os.environ.get("OPENAI_API_BASE_URL"))),
    addon_params={
        "language": "English or Chinese",
        "entity_types": ["organization", "person", "geo", "event", "category", "technical-term"],
    },
    chunk_token_size=config.CHUNK_TOKEN_SIZE
    # llm_model_func=gpt_4o_complete
)

query = "mitigation api目前有什么问题呢？"
# query = "mitigation api 和response app有啥关系"
# query = "gmail listener的功能是什么？"
print(rag.query(query, param=QueryParam(mode="hybrid")))
print("============================= hybrid =======================")
print(rag.query(query, param=QueryParam(mode="local")))
print("============================= local =======================")
print(rag.query(query, param=QueryParam(mode="global")))
print("============================= global =======================")
print(rag.query(query, param=QueryParam(mode="naive")))
print("============================= native =======================")