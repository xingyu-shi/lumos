import os
import re

import dotenv
from langchain_core.messages import AIMessage
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_ollama import ChatOllama
from langchain_ollama import OllamaEmbeddings

from lumos_small_lc import samples

dotenv.load_dotenv()

llm = ChatOllama(
    model=os.environ["CHAT_MODEL"],
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


def qwen3_remove_think_parse(ai_message: AIMessage) -> str:
    return re.sub(r"<think>.*?</think>", "", ai_message.text(), flags=re.DOTALL).strip()


llm_without_thought = llm | qwen3_remove_think_parse

if __name__ == '__main__':
    print(llm.invoke("what's the capital of canada"))
    print(
        llm.invoke([{
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Describe this image:",
                },
                {
                    "type": "image",
                    "source_type": "base64",
                    "data": samples.CAT_IMAGE_BASE64,
                    "mime_type": "image/jpeg",
                },
            ],
        }]))
