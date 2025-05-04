import os
from typing import Optional

from pydantic import BaseModel


def remove_ext(filename):
    _name, _ext = os.path.splitext(filename)
    return _name

class Document(BaseModel):
    id: str
    text: str
    meta_data: Optional[dict] = {}

def iter_documents(folder_path: str, include_exts=['.txt', '.md']):
    if os.path.isfile(folder_path):
        with open(folder_path, "r", encoding="utf-8") as f:
            # get file name from path
            name = os.path.basename(folder_path)
            meta_data = {"source": remove_ext(name)}
            content = f.read()
            if content.startswith("link:"):
                meta_data["link"] = content.split("\n")[0].partition(":")[2].strip()
                content = content.partition("\n")[2]
            yield Document(text=content, meta_data=meta_data, id=folder_path)
    else:
        for root, dirs, files in os.walk(folder_path):
            for name in files:
                for ext in include_exts:
                    if name.endswith(ext):
                        with open(os.path.join(root, name), "r", encoding="utf-8") as f:
                            # rag.insert(f.read(), remove_ext(name))
                            meta_data = {"source": remove_ext(name)}
                            content = f.read()
                            if content.startswith("link:"):
                                meta_data["link"] = content.split("\n")[0].partition(":")[2].strip()
                                content = content.partition("\n")[2]
                            yield Document(text=content, meta_data=meta_data, id=meta_data["link"] if "link" in meta_data else os.path.join(root, name))
                        break