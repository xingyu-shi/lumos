import os

import dotenv
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_ollama import ChatOllama
from langchain_ollama import OllamaEmbeddings

dotenv.load_dotenv()

llm = ChatOllama(
    model=os.environ["CHAT_MODEL"],
)
llm_with_vision = ChatOllama(
    model=os.environ["CHAT_VISION_MODEL"],
)
embeddings = OllamaEmbeddings(
    model=os.environ["EMBEDDING_MODEL"],
)

# llm = ChatOpenAI(
#     model=os.environ["CHAT_MODEL"],
#     api_key=os.environ["CHAT_API_TOKEN"],
#     base_url=os.environ["CHAT_API_BASE_URL"],
# )
# embeddings = OpenAIEmbeddings(
#     model=os.environ["EMBEDDING_MODEL"],
#     api_key=os.environ["EMBEDDING_API_TOKEN"],
#     base_url=os.environ["EMBEDDING_API_BASE_URL"],
#     dimensions=1024,
#     embedding_ctx_length=8192,
#     check_embedding_ctx_length=False
# )

# URI = "./milvus_example.db"
#
# vector_store = Milvus(
#     embedding_function=embeddings,
#     connection_args={"uri": URI, "token": os.environ["MILVUS_TOKEN"]},
#     index_params={"index_type": "FLAT", "metric_type": "L2"},
# )


vector_store = InMemoryVectorStore(embeddings)

if __name__ == '__main__':
    print(llm.invoke("what's the capital of canada"))
