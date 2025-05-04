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

from llama_index.llms.openai import OpenAI

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

# Create your index
from llama_index.core import VectorStoreIndex

index = VectorStoreIndex.from_vector_store(vector_store)

query="""
[Background]
I am an customer support engineer.
Please help me with the following customer question.
Make sure to provide the accurate, definite and detailed information.
Do not provide any information that you are not sure about.
If you think the question is not clear, please ask for clarification.

[Question]
Our customer is asking us about the integration of CAS and SIEM.
They would like to aggregate email logs into SIEM and are wondering if it is possible to retrieve the following email logs from CAS and integrate them with another SIEM (NG-SIEM):
Information they would like to reference when integrating with SIEM:

When (date and time)
From which email address
To which email address
What subject line the email had
Whether it was sent or received
Summary of email body

[Answer Request]
Is CAS able to the above information sync with SIEM?
"""

retriever = index.as_retriever()
retrieved_res = retriever.retrieve(query)
for doc in retrieved_res:
    print(doc)

query_engine = index.as_query_engine(
    OpenAI(model=os.environ.get("OPENAI_MODEL"),
           api_key=os.environ.get("OPENAI_API_KEY"),
           api_base=os.environ.get("OPENAI_API_BASE_URL")
           )
)
res = query_engine.query(query)
print(res)
# index = load_index_from_storage(storage_context)
print(1)