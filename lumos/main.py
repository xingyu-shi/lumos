import os
import pickle

from LightRAG.lightrag import LightRAG, QueryParam
from LightRAG.lightrag.llm import gpt_4o_mini_complete, openai_embedding
from LightRAG.lightrag.utils import EmbeddingFunc, compute_mdhash_id

from dotenv import load_dotenv
load_dotenv('../.env')

WORKING_DIR = "workspace_extracted_entity_types"
# TEXT_EMBEDDING_CACHE = "kv_store_embedding_func_cache.pkl"
#
# if not os.path.exists(WORKING_DIR):
#     os.mkdir(WORKING_DIR)
#
# def load_embedding_cache():
#     if not os.path.exists(os.path.join(WORKING_DIR, TEXT_EMBEDDING_CACHE)):
#         return dict()
#     else:
#         with open(os.path.join(WORKING_DIR, TEXT_EMBEDDING_CACHE), 'rb') as f:
#             _text_embedding_cached = pickle.load(f)
#     return _text_embedding_cached
#
# def save_embedding_cache(_text_embedding_cached):
#     with open(os.path.join(WORKING_DIR, TEXT_EMBEDDING_CACHE), 'wb') as f:
#         pickle.dump(_text_embedding_cached, f)
#
# text_embedding_cached = load_embedding_cache()
#
# def get_embedding_cached(texts):
#     embed = []
#     for text in texts:
#         key = compute_mdhash_id(text)
#
#         if key not in text_embedding_cached:
#             return None
#         else:
#             embed.append(text_embedding_cached[key])
#     return embed
#
#
# def set_embedding_cached(texts, embeddings):
#     assert len(texts) == len(embeddings)
#     for idx, text in enumerate(texts):
#         key = compute_mdhash_id(text)
#         text_embedding_cached[key] = embeddings[idx]
#
#     return embeddings
#
# async def embedding_func(texts):
#     return get_embedding_cached(texts) or set_embedding_cached(texts, await openai_embedding(texts, base_url=os.environ.get("OPENAI_API_BASE_URL")))

rag = LightRAG(
    working_dir=WORKING_DIR,
    llm_model_func=lambda *args, **kwargs: gpt_4o_mini_complete(*args, **kwargs, base_url=os.environ.get("OPENAI_API_BASE_URL")),
    embedding_func=EmbeddingFunc(embedding_dim=1536, max_token_size=8192,
                                 func=lambda texts:openai_embedding(texts, base_url=os.environ.get("OPENAI_API_BASE_URL"))),
    addon_params={
        "language": "English or Chinese",
        "entity_types": ["organization", "person", "geo", "event", "category", "technical-term"],
    }

    # llm_model_func=gpt_4o_complete
)
rag.pre_load_embeddings()
rag.merge()

# query = "mitigation api目前有什么问题呢？"
# query = "mitigation api 和response app有啥关系"
query = "gmail listener的功能是什么？"
print(rag.query(query, param=QueryParam(mode="hybrid")))
print("============================= hybrid =======================")
print(rag.query(query, param=QueryParam(mode="local")))
print("============================= local =======================")
print(rag.query(query, param=QueryParam(mode="global")))
print("============================= global =======================")
print(rag.query(query, param=QueryParam(mode="naive")))
print("============================= native =======================")

# folder_path = "/Users/xingyushi/.notable"
# for root, dirs, files in os.walk(folder_path):
#     for name in files:
#         if name.endswith(".md") or name.endswith(".txt"):
#             print("文件:", os.path.join(root, name))
#             with open(os.path.join(root, name), "r", encoding="utf-8") as f:
#                 print("inset:", os.path.join(root, name))
#                 rag.insert(f.read())


