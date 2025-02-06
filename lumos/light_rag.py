import os

from LightRAG.lightrag import LightRAG
from LightRAG.lightrag.llm import openai_embedding, openai_complete_if_cache, GPTKeywordExtractionFormat
from LightRAG.lightrag.utils import EmbeddingFunc
from dotenv import load_dotenv

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
load_dotenv(config.ENV_DIR)

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
    enable_embedding_func_cache = True,
    # enable_llm_cache = False,
    # llm_model_func=gpt_4o_complete
)