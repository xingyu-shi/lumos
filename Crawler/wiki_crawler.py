import os
import pickle

import requests
from bs4 import BeautifulSoup
import re

from dotenv import load_dotenv

load_dotenv()

WORKING_DIR = "workspace"
BASEDIR = os.path.dirname(os.path.abspath(__file__))
if not os.path.exists(os.path.join(BASEDIR, WORKING_DIR)):
    os.mkdir(os.path.join(BASEDIR, WORKING_DIR))

if not os.path.exists(os.path.join(BASEDIR, WORKING_DIR, "_crawled.pkl")):
    crawled = set()
    with open(os.path.join(BASEDIR, WORKING_DIR, "_crawled.pkl"), "wb") as f:
        pickle.dump(crawled, f)
else:
    with open(os.path.join(BASEDIR, WORKING_DIR, "_crawled.pkl"), "rb") as f:
        crawled = pickle.load(f)


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
    max_length = 255  # 一般文件名最大长度为 255 字符
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]

    return sanitized


def wiki_scraper(url):
    # 发送 HTTP GET 请求
    response = requests.get(url, cookies=parse_cookie_str(os.environ.get("COOKIE")))
    response.raise_for_status()  # 如果请求失败，抛出异常

    # 使用 BeautifulSoup 解析 HTML 内容
    soup = BeautifulSoup(response.text, 'html.parser')

    # 获取页面标题
    title = soup.title.string if soup.title else url
    print(f"title: {title}\n")

    # 移除 <style> 标签
    for style_tag in soup.find_all('style'):
        style_tag.decompose()

    # 移除所有 style 属性
    for script_tag in soup.find_all('script'):
        script_tag.decompose()

    # 移除所有 style 属性
    for tag in soup.find_all(style=True):
        del tag['style']

    # 移除所有 class 属性
    for tag in soup.find_all(class_=True):
        del tag['class']

    hrefs = []
    for a in soup.find_all('a'):
        # 获取链接的文本和 href 属性
        link_text = a.get_text()
        link_href = a['href']
        hrefs.append(link_href)
        # 替换为原始超链接
        a.replace_with(f'{link_text} ({link_href})')

    # 展开收起来的文本块
    for div in soup.find_all('div', class_='collapsed'):
        div['style'] = ''

    contents = []
    # 获取页面内容
    for content in soup.find_all('div', attrs={'id': 'content-body'}):
        for tag in content.find_all('div', attrs={'data-testid': 'content-header-container'}):
            tag.decompose()
        for tag in content.find_all('h1', attrs={'id': 'title-text'}):
            contents.append(tag.get_text())
            tag.decompose()
        contents.append(content.get_text().replace('\xa0', ' '))

    with open(os.path.join(BASEDIR, WORKING_DIR, f"{sanitize_filename(title)}.txt"), "w", encoding="utf-8") as f:
        f.write(f'link: {url}\n\n')
        f.write("\n".join(contents))


rd_feature_matrix_bigtable_related_urls = [
    "https://trendmicro.atlassian.net/wiki/spaces/TMCASP/pages/348264837/aad+gmail+user+info",
    "https://trendmicro.atlassian.net/wiki/spaces/TMCASP/pages/348271820/bigtable-delegator",
    "https://trendmicro.atlassian.net/wiki/spaces/TMCASP/pages/348271834/feature+set",
    "https://trendmicro.atlassian.net/wiki/spaces/TMCASP/pages/348264959/hpu+high+profile+domain+others",
    "https://trendmicro.atlassian.net/wiki/spaces/TMCASP/pages/348271803/trigger+condition"
]

# 使用爬虫抓取一个目标网站
if __name__ == "__main__":
    target_urls = rd_feature_matrix_bigtable_related_urls
    for target_url in target_urls:
        if target_url in crawled:
            continue
        print(f"processing {target_url}")
        try:
            wiki_scraper(target_url)
            crawled.add(target_url)
            with open(os.path.join(BASEDIR, WORKING_DIR, "_crawled.pkl"), "wb") as f:
                pickle.dump(crawled, f)
        except Exception as e:
            print(f"{target_url} error: {e}")
