import os

from LightRAG.lightrag import LightRAG
from LightRAG.lightrag.llm import gpt_4o_mini_complete, openai_embedding, gpt_4o_complete
from LightRAG.lightrag.utils import EmbeddingFunc

# ================ config ====================
class CFG:
    WORKSPACE = "workspace_cas_ems_gpt4o_mini"
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    ENV_DIR = os.path.join(BASE_DIR, "../.env")
    WORKING_DIR = os.path.join(BASE_DIR, "../" , WORKSPACE)

    if not os.path.exists(WORKING_DIR):
        os.mkdir(WORKING_DIR)
    CHUNK_TOKEN_SIZE = 1200

# ================ end config ====================
config = CFG()
# llm_complete = gpt_4o_complete
llm_complete = gpt_4o_mini_complete

rag = LightRAG(
    working_dir=config.WORKING_DIR,
    llm_model_func=lambda *args, **kwargs: llm_complete(*args, **kwargs, base_url=os.environ.get("OPENAI_API_BASE_URL")),
    embedding_func=EmbeddingFunc(embedding_dim=1536, max_token_size=8192,
                                 func=lambda texts:openai_embedding(texts, base_url=os.environ.get("OPENAI_API_BASE_URL"))),
    addon_params={
        "language": "English or Chinese",
        "entity_types": ["organization", "person", "geo", "event", "category", "technical-term"],
    },
    chunk_token_size=config.CHUNK_TOKEN_SIZE,
    enable_embedding_func_cache = True,
    # enable_llm_cache = False,
    # llm_model_func=gpt_4o_complete
)