from LightRAG.lightrag import LightRAG, QueryParam

from dotenv import load_dotenv

from lumos.light_rag import rag, config

load_dotenv(config.ENV_DIR)

# query = "mitigation api目前有什么问题呢？"
query = "现在每个公司，每分钟最大可以发送多少个mitigation action？"
# query = "mitigation api 和response app有啥关系"
# query = "gmail listener的功能是什么？"
print(rag.query(query, param=QueryParam(mode="hybrid")))
print("============================= hybrid =======================")
print(rag.query(query, param=QueryParam(mode="local")))
print("============================= local =======================")
print(rag.query(query, param=QueryParam(mode="global")))
print("============================= global =======================")
print(rag.query(query, param=QueryParam(mode="naive")))
print("============================= native =======================")
print(rag.query(query, param=QueryParam(mode="mix")))
print("============================= native =======================")