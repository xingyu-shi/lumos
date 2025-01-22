from dotenv import load_dotenv
from lumos.light_rag import rag, config

load_dotenv(config.ENV_DIR)

rag.pre_load_embeddings()
rag.merge(similar_threshold=0.8)

