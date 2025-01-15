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

def remove_ext(filename):
    _name, _ext = os.path.splitext(filename)
    return _name

folder_path = "/Users/xingyushi/.notable"
for root, dirs, files in os.walk(folder_path):
    for name in files:
        if name.endswith(".md") or name.endswith(".txt"):
            print("文件:", os.path.join(root, name))
            if "mitigation" in name.lower():
                with open(os.path.join(root, name), "r", encoding="utf-8") as f:
                    print("inset:", os.path.join(root, name))
                    # rag.insert(f.read(), remove_ext(name))
                    rag.insert(f.read())


