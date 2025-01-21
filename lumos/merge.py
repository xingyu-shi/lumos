from dotenv import load_dotenv

load_dotenv('../.env')

from lumos.rag import rag

rag.pre_load_embeddings()
rag.merge(similar_threshold=0.8)

