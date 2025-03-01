from lumos.light_rag import rag, config
from lumos.utils import iter_documents


def build_rag(folder_path: str, include_exts=['.txt', '.md']):
    for document in iter_documents(folder_path, include_exts):
        print(f"inset meta_data={document.meta_data}")
        rag.insert(document.text, meta_data=document.meta_data)


if __name__=='__main__':
    build_rag('/Users/xingyushi/.notable/notes/CAS Feature - Mitigation API.md')
