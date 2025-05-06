import re

from langchain_core.messages import AIMessage


def remove_think_parse(ai_message: AIMessage) -> str:
    return re.sub(r"(<think>).*?(</think>)", "", ai_message.text(), flags=re.DOTALL).strip()
