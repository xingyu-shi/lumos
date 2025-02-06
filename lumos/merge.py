from lumos.light_rag import rag, config

if __name__ == '__main__':
    rag.pre_load_embeddings()
    rag.merge(similar_threshold=0.8)

