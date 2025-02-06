import os
from dotenv import load_dotenv
from lumos.light_rag import rag, config

load_dotenv(config.ENV_DIR)

def remove_ext(filename):
    _name, _ext = os.path.splitext(filename)
    return _name

def build_rag(folder_path: str, include_exts=['.txt', '.md']):
    if os.path.isfile(folder_path):
        with open(folder_path, "r", encoding="utf-8") as f:
            # get file name from path
            name = os.path.basename(folder_path)
            meta_data = {"source": remove_ext(name)}
            content = f.read()
            if content.startswith("link:"):
                meta_data["link"] = content.split("\n")[0].partition(":")[2].strip()
                content = content.partition("\n")[2]
            print(f"inset={name}, meta_data={meta_data}")
            rag.insert(content, meta_data=meta_data)
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
                            print(f"inset={os.path.join(root, name)}, meta_data={meta_data}")
                            rag.insert(content, meta_data=meta_data)
                        break


if __name__=='__main__':
    build_rag('/Users/xingyushi/.notable/notes/CAS Feature - Mitigation API.md')
