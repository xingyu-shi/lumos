import os

from llama_index.core import Document, StorageContext, load_index_from_storage, VectorStoreIndex, Settings
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.extractors import TitleExtractor
from llama_index.core.ingestion import IngestionPipeline
from llama_index.llms.ollama import Ollama
from llama_index.llms.lmstudio import LMStudio
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.vector_stores.milvus import MilvusVectorStore
import chromadb
from llama_index.readers.web import SimpleWebPageReader

from dotenv import load_dotenv

from lumos.utils import iter_documents

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

load_dotenv(os.path.join(BASE_DIR, "./.env"))

documents = [Document(text=document.text, metadata={**document.meta_data}, id_=document.id)
             for document in iter_documents('/Users/xingyushi/code/personal/lumos/Crawler/workspace_cas')]

# db = chromadb.PersistentClient(path="./chroma_db")
# chroma_collection = db.get_or_create_collection("quickstart")
# vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

from llama_index.llms.openai import OpenAI
# Settings.llm = OpenAI(model=os.environ.get("OPENAI_MODEL"), api_key=os.environ.get("OPENAI_API_KEY"),
#                       api_base=os.environ.get("OPENAI_API_BASE_URL"))

Settings.embed_model = OpenAIEmbedding(model_name=os.environ.get("EMBEDDING_MODEL"),
                                       api_base=os.environ.get('EMBEDDING_API_BASE_URL'))

vector_store = MilvusVectorStore(
    uri="./milvus_demo.db",
    dim=1024,
    token=os.environ.get("MILVUS_TOKEN"),
    enable_sparse=True,
    hybrid_ranker="RRFRanker",
    hybrid_ranker_params={"k": 60},
)
storage_context = StorageContext.from_defaults(vector_store=vector_store)
index = VectorStoreIndex.from_documents(documents, storage_context)

# query_engine = index.as_query_engine()
# res = query_engine.query("What did the author learn?")

#
# pipeline = IngestionPipeline(
#     transformations=[
#         SentenceSplitter(chunk_size=512, chunk_overlap=128),
#         TitleExtractor(llm=Ollama(model=os.environ.get("CHAT_MODEL"))),
#         OllamaEmbedding(model_name=os.environ.get("EMBEDDING_MODEL")),
#     ],
#     vector_store=vector_store,
# )
#
# # Ingest directly into a vector db
# pipeline.run(documents=[Document.example()])

# Create your index
from llama_index.core import VectorStoreIndex

index = VectorStoreIndex.from_vector_store(vector_store)
# query_engine = index.as_query_engine()
# res = query_engine.query("What data connectors do you offer")
# print(res)
retriever = index.as_retriever()
retrieved_res = retriever.retrieve("What is CAS?")
print(retrieved_res)
# index = load_index_from_storage(storage_context)
print(1)