from langchain_community.document_loaders import UnstructuredMarkdownLoader

loader = UnstructuredMarkdownLoader(
    "D:\Storage\\Notable\\Notable-Repository\\notes\CAS Feature - Small Feature Collection.md", mode="elements")

data = loader.load()
print(1)

class NotableLoader