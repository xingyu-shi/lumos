import os

import logging
import sys
from dotenv import load_dotenv
from llama_index.core.query_engine import KnowledgeGraphQueryEngine

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

load_dotenv(os.path.join(BASE_DIR, "../.env"))

from lumos.utils import iter_documents

logging.basicConfig(
    stream=sys.stdout, level=logging.INFO
)  # logging.DEBUG for more verbose output


# define LLM
from llama_index.llms.openai import OpenAI
from llama_index.core import Settings, Document, PropertyGraphIndex, KnowledgeGraphIndex
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding

Settings.llm = Ollama(temperature=0,
                      model=os.environ.get("CHAT_MODEL"),
                      keep_alive=True)
Settings.embed_model = OllamaEmbedding(model_name=os.environ.get("EMBEDDING_MODEL"),
                                      keep_alive=True)
Settings.chunk_size = 512

os.environ["NEBULA_USER"] = "root"
os.environ["NEBULA_PASSWORD"] = "nebula"  # default is "nebula"
os.environ[
    "NEBULA_ADDRESS"
] = "127.0.0.1:9669"  # assumed we have NebulaGraph installed locally

space_name = "llamaindex"
edge_types, rel_prop_names = ["relationship"], [
    "relationship"
]  # default, could be omit if create from an empty kg
tags = ["entity"]  # default, could be omit if create from an empty kg


from llama_index.core import StorageContext
from llama_index.graph_stores.nebula import NebulaGraphStore

graph_store = NebulaGraphStore(
    space_name=space_name,
    edge_types=edge_types,
    rel_prop_names=rel_prop_names,
    tags=tags,
)
storage_context = StorageContext.from_defaults(graph_store=graph_store)

query_engine = KnowledgeGraphQueryEngine(
    storage_context=storage_context,
    verbose=True,
)

response = query_engine.query(
    "现在每个公司，每分钟最大可以发送多少个mitigation action？",
)
print(f"<b>{response}</b>")