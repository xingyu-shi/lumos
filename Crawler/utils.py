import re
from urllib.parse import urlparse, urlunparse

from pydantic import BaseModel


def parse_cookie_str(cookie_str):
    cookies = {}
    for cookie in cookie_str.split(";"):
        key, value = cookie.split("=")
        cookies[key] = value
    return cookies

def remove_fragment_from_url(url):
    # 解析 URL
    parsed_url = urlparse(url)
    # 创建一个新的 URL 元组，将 fragment 设置为空字符串
    cleaned_url = parsed_url._replace(fragment="")
    # 重新组合 URL
    return urlunparse(cleaned_url)

def sanitize_filename(filename, replacement=""):
    """
    将字符串转换为合法的文件名，去除或替换非法字符。

    :param filename: 原始字符串
    :param replacement: 替换非法字符的字符串，默认为 "_"
    :return: 转换后的合法文件名
    """
    filename = str(filename).partition("|")[0]
    # 定义非法字符的正则表达式
    invalid_chars = r'[<>:"/\\|?*\x00-\x1F]'  # 包括 Windows 和 POSIX 中非法字符

    # 替换非法字符
    sanitized = re.sub(invalid_chars, replacement, filename)

    # 去除开头和结尾的空格或替换字符，避免文件名无效
    sanitized = sanitized.strip().strip(replacement)

    # 限制文件名长度（根据具体文件系统需求）
    max_length = 200  # 一般文件名最大长度为 255 字符
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]

    return sanitized


import threading
import time
import uuid
from collections import deque
from typing import Optional, Tuple, Any, List


class UrlWithParents(BaseModel):
    url: str
    parents: Optional[List[str]] = []

class LocalQueueMessage(BaseModel):
    message_id: str
    data: Any
    lock_expiry: Optional[float] = None

class LocalQueue:
    def __init__(self):
        self._messages = deque()
        self._lock = threading.Lock()

    def dump(self):
        return self._messages

    def load(self, messages):
        self._messages = messages

    def enqueue(self, message: any) -> str:
        """将消息加入队列，返回消息ID"""
        with self._lock:
            message_id = str(uuid.uuid4())
            self._messages.append(
                LocalQueueMessage(message_id=message_id, data=message, lock_expiry=None)
            )
            return message_id

    def peek_lock(self, lock_timeout: int = 30) -> Optional[LocalQueueMessage]:
        """锁定并返回队列中的下一条可用消息"""
        for i in range(3):
            with self._lock:
                current_time = time.time()

                # 查找第一个未锁定的消息
                for msg in self._messages:
                    if not msg.lock_expiry or msg.lock_expiry <= current_time:
                        msg.lock_expiry = current_time + lock_timeout
                        return msg
            time.sleep(3)
        return None

    def delete(self, message_id: str) -> bool:
        """删除已处理的消息"""
        with self._lock:
            for idx, msg in enumerate(self._messages):
                if msg.message_id == message_id:
                    del self._messages[idx]
                    return True
            return False

    def contains(self, message_id: str) -> bool:
        """检查消息是否在队列中"""
        with self._lock:
            for msg in self._messages:
                if msg.message_id == message_id:
                    return True
            return False

    def renew_lock(self, message_id: str, lock_timeout: int = 30) -> bool:
        """续订消息锁定时间"""
        with self._lock:
            current_time = time.time()
            for msg in self._messages:
                if msg.message_id == message_id:
                    # 只有仍在锁定状态的消息才能续订
                    if msg.lock_expiry and msg.lock_expiry > current_time:
                        msg.lock_expiry = current_time + lock_timeout
                        return True
            return False

    @property
    def count(self) -> int:
        """返回队列中的消息总数（包括已锁定的）"""
        with self._lock:
            return len(self._messages)