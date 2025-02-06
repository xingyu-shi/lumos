from LightRAG.lightrag import LightRAG, QueryParam

from dotenv import load_dotenv

from lumos.light_rag import rag, config

load_dotenv(config.ENV_DIR)

# query = "mitigation api目前有什么问题呢？"
query = "现在每个公司，每分钟最大可以发送多少个mitigation action？"
# query = "mitigation api 和response app有啥关系"
# query = "gmail listener的功能是什么？"
# query="""
# [Background]
# The customer is using Outlook (Classic version).
# They intend to use the features of the Cloud Email and Collaboration Protection Add-in for Outlook.
#
# [Question]
# Is add-in for Outlook (classic version) supported?
# """

# query="""
# [Background]
# I am an customer support engineer.
# Please help me with the following customer question.
# Make sure to provide the accurate, definite(most important), detailed information.
# If you think the question is not clear, please ask for clarification.
#
# [Question]
# Our customer is asking us about the integration of CAS and SIEM.
# They would like to aggregate email logs into SIEM and are wondering if it is possible to retrieve the following email logs from CAS and integrate them with another SIEM (NG-SIEM):
# Information they would like to reference when integrating with SIEM:
#
# When (date and time)
# From which email address
# To which email address
# What subject line the email had
# Whether it was sent or received
# Summary of email body
#
# [Answer Request]
# Is CAS able to the above information sync with SIEM?
# """
print(rag.query(query, param=QueryParam(mode="hybrid", need_context_graph=True, need_context=True))['response'])
# print("============================= hybrid =======================")
# print(rag.query(query, param=QueryParam(mode="local")))
# print("============================= local =======================")
# print(rag.query(query, param=QueryParam(mode="global")))
# print("============================= global =======================")
# print(rag.query(query, param=QueryParam(mode="naive", need_context_graph=True, need_context=True)))
# print("============================= native =======================")
print(rag.query(query, param=QueryParam(mode="mix", need_context_graph=True, need_context=True, top_k=10))['response'])
# print(rag.query("", param=QueryParam(mode="mix")))
print("============================= mix =======================")