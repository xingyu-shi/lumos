import os
import pickle

import requests
from bs4 import BeautifulSoup
import re

from dotenv import load_dotenv

from Crawler.utils import parse_cookie_str, sanitize_filename

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
