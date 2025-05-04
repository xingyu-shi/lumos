import os

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Document
from llama_index.core.postprocessor import SentenceTransformerRerank, LLMRerank

from lumos.utils import iter_documents
import logging
import sys
from dotenv import load_dotenv
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
from llama_index.extractors.entity import EntityExtractor
Settings.chunk_size = 512

documents = [Document(text=document.text, metadata=document.meta_data) for document in iter_documents('/Users/xingyushi/.notable/notes/CAS Feature - Mitigation API.md')]
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()
response = query_engine.query("现在每个公司，每分钟最大可以发送多少个mitigation action？")
print(response)