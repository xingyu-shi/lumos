import os
from dotenv import load_dotenv
from lumos.rag import rag

load_dotenv('../.env')

def remove_ext(filename):
    _name, _ext = os.path.splitext(filename)
    return _name

folder_path = "/Users/xingyushi/.notable"
for root, dirs, files in os.walk(folder_path):
    for name in files:
        if name.endswith(".md") or name.endswith(".txt"):
            print("文件:", os.path.join(root, name))
            if "mitigation" in name.lower():
                with open(os.path.join(root, name), "r", encoding="utf-8") as f:
                    print("inset:", os.path.join(root, name))
                    # rag.insert(f.read(), remove_ext(name))
                    rag.insert(f.read(), meta_data={"source": remove_ext(name)})


