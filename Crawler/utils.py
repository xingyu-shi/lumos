import re


def parse_cookie_str(cookie_str):
    cookies = {}
    for cookie in cookie_str.split(";"):
        key, value = cookie.split("=")
        cookies[key] = value
    return cookies


def sanitize_filename(filename, replacement="_"):
    """
    将字符串转换为合法的文件名，去除或替换非法字符。

    :param filename: 原始字符串
    :param replacement: 替换非法字符的字符串，默认为 "_"
    :return: 转换后的合法文件名
    """
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