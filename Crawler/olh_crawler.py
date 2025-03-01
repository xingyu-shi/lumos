import os
import pickle
import queue
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import List, Optional
from urllib.parse import urljoin
import logging

import requests
from bs4 import BeautifulSoup, PageElement
import re

from dotenv import load_dotenv
from pydantic import BaseModel

from Crawler.utils import parse_cookie_str, sanitize_filename, LocalQueue, LocalQueueMessage, UrlWithParents, \
    remove_fragment_from_url
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

load_dotenv()

lock = threading.Lock()
TREND_DOC_URL_PREFIX = 'https://docs.trendmicro.com'
WORKING_DIR = "workspace_cas"
BASEDIR = os.path.dirname(os.path.abspath(__file__))
if not os.path.exists(os.path.join(BASEDIR, WORKING_DIR)):
    os.mkdir(os.path.join(BASEDIR, WORKING_DIR))

logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.FileHandler(os.path.join(BASEDIR, WORKING_DIR, "crawler.log")),
        logging.StreamHandler()
    ]
)

if not os.path.exists(os.path.join(BASEDIR, WORKING_DIR, "_crawled.pkl")):
    crawled = set()
    with open(os.path.join(BASEDIR, WORKING_DIR, "_crawled.pkl"), "wb") as f:
        pickle.dump(crawled, f)
else:
    with open(os.path.join(BASEDIR, WORKING_DIR, "_crawled.pkl"), "rb") as f:
        crawled = pickle.load(f)

to_crawl_list = LocalQueue()
if not os.path.exists(os.path.join(BASEDIR, WORKING_DIR, "_to_crawl.pkl")):
    with open(os.path.join(BASEDIR, WORKING_DIR, "_to_crawl.pkl"), "wb") as f:
        pickle.dump(to_crawl_list.dump(), f)
else:
    with open(os.path.join(BASEDIR, WORKING_DIR, "_to_crawl.pkl"), "rb") as f:
        to_crawl_list.load(pickle.load(f))

crawling = set()
def mark_crawling(url):
    with lock:
       crawling.add(url)

def is_crawling(url):
    with lock:
        return url in crawling

def mark_crawled(url):
    with lock:
        crawled.add(url)
        crawling.remove(url)
        with open(os.path.join(BASEDIR, WORKING_DIR, "_crawled.pkl"), "wb") as f:
            pickle.dump(crawled, f)

def is_crawled(url):
    with lock:
        return url in crawled

def extract_plain_contents(content: BeautifulSoup) -> List[str]:
    contents = []
    # 移除 <style> 标签
    # 获取页面内容
    for style_tag in content.find_all('style'):
        style_tag.decompose()

    # 移除所有 style 属性
    for script_tag in content.find_all('script'):
        script_tag.decompose()

    # 移除所有 style 属性
    for tag in content.find_all(style=True):
        del tag['style']

    # 移除所有 class 属性
    for tag in content.find_all(class_=True):
        del tag['class']

    for a in content.find_all('a'):
        if not "href" in a.attrs:
            continue
        # 获取链接的文本和 href 属性
        link_text = a.get_text()
        link_href = a['href']
        # 替换为原始超链接
        a.replace_with(f'{link_text} ({link_href})')

    # 展开收起来的文本块
    for div in content.find_all('div', class_='collapsed'):
        div['style'] = ''

    for tag in content.find_all('div', attrs={'data-testid': 'content-header-container'}):
        tag.decompose()

    for tag in content.find_all('h1', attrs={'id': 'title-text'}):
        contents.append(tag.get_text())
        tag.decompose()

    contents.append(content.get_text().replace('\xa0', ' '))
    return contents

def extract_sub_links_from_olh(soup: BeautifulSoup, parent_url: str) -> List[str]:
    hrefs = []
    for card in soup.find_all('article', attrs={"class": "OLH-card"}):
        for a_tag in card.find_all('a'):
            if not 'href' in a_tag.attrs:
                continue
            if not a_tag['href'].startswith('http'):
                a_tag['href'] = urljoin(parent_url, a_tag['href'])
            hrefs.append(a_tag['href'])

    for main in soup.find_all('div', attrs={"id": "wh-content"}):
        for a_tag in main.find_all('a'):
            if not 'href' in a_tag.attrs:
                continue
            if not a_tag['href'].startswith('http'):
                a_tag['href'] = urljoin(parent_url, a_tag['href'])
            hrefs.append(a_tag['href'])

    for main in soup.find_all('div', attrs={"class": "article-menu"}):
        for a_tag in main.find_all('a'):
            if not 'href' in a_tag.attrs:
                continue
            if not a_tag['href'].startswith('http'):
                a_tag['href'] = urljoin(parent_url, a_tag['href'])
            hrefs.append(a_tag['href'])
    hrefs = [remove_fragment_from_url(href) for href in hrefs]
    return list(set(hrefs))

def scrape_url(url: str):
    # 发送 HTTP GET 请求
    # 初始化浏览器
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # 无头模式
    driver = webdriver.Chrome(options=options)

    driver.get(url)
    # WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "article-menu")))
    # WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "article-main")))
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()
    # response = requests.get(url, headers=headers)
    # response.raise_for_status()  # 如果请求失败，抛出异常

    # 使用 BeautifulSoup 解析 HTML 内容
    # soup = BeautifulSoup(response.text, 'html.parser')

    # 获取页面标题
    title = soup.title.string if soup.title else url
    logging.info(f"title: {sanitize_filename(title)}\n")
    contents = []
    sub_links = []
    if url.startswith(TREND_DOC_URL_PREFIX):
        sub_links = extract_sub_links_from_olh(soup, url)

        for content in soup.find_all('div', attrs={'id': 'wh-content'}):
            contents.extend(extract_plain_contents(content))
    else:
        contents.extend(extract_plain_contents(soup))

    plain_content = "\n".join(contents).strip()

    return title, plain_content, sub_links

def scraper_worker(message: LocalQueueMessage):
    url = message.data
    try:
        if is_crawled(url.url):
            to_crawl_list.delete(message.message_id)
            return
        if is_crawling(url.url):
            return
        mark_crawling(url.url)
        title, plain_content, sub_links  = scrape_url(url.url)
        filename_url = str(url.url).rstrip("/").removeprefix(TREND_DOC_URL_PREFIX)
        filename = f"{sanitize_filename(title + "_" + filename_url)}"
        parents = url.parents if url.parents else []
        parents = [parent for parent in parents]
        if not os.path.exists(os.path.join(BASEDIR, WORKING_DIR, "/".join(parents))):
            os.mkdir(os.path.join(BASEDIR, WORKING_DIR, "/".join(parents)))

        parents.append(filename)
        parents_path = "/".join(parents)

        if plain_content != "":
            with open(os.path.join(BASEDIR, WORKING_DIR, f"{parents_path}.txt"), "w", encoding="utf-8") as f:
                f.write(f'link: {url.url}\n\n')
                f.write(plain_content)

        for sub_link in sub_links:
            if not is_crawled(sub_link):
                to_crawl_list.enqueue(UrlWithParents(url=sub_link, parents=parents))

        with open(os.path.join(BASEDIR, WORKING_DIR, "_to_crawl.pkl"), "wb") as f:
            pickle.dump(to_crawl_list.dump(), f)

        mark_crawled(url.url)
        to_crawl_list.delete(message.message_id)
        logging.info(f"completed {message.data}, total: {to_crawl_list.count}")
    except Exception as e:
        logging.error(f"{url} error: {e}")
        mark_crawled(url.url)
        to_crawl_list.delete(message.message_id)

# 使用爬虫抓取一个目标网站
if __name__ == "__main__":
    logging.info(f"Starting crawler, crawled: {len(crawled)}, to crawl: {to_crawl_list.count}")
    exit()
    # to_crawl_list.enqueue(UrlWithParents(url="https://docs.trendmicro.com/en-us/documentation/cloud-app-security/"))
    # to_crawl_list.enqueue(UrlWithParents(url="https://docs.trendmicro.com/en-us/documentation/email-security/"))
    max_workers = 10
    task_queue = queue.Queue(maxsize=max_workers)  # 控制队列大小
    def worker():
        while True:
            _msg = task_queue.get()
            if _msg is None:
                break
            scraper_worker(_msg)
            task_queue.task_done()

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for _ in range(max_workers):
            futures.append(executor.submit(worker))

        while (msg := to_crawl_list.peek_lock()) is not None:
            logging.info(f"processing {msg.data}, total: {to_crawl_list.count}")
            task_queue.put(msg)  # 如果队列已满，这里会阻塞

        # 等待所有任务完成
        task_queue.join()

        # 停止工作线程
        for _ in range(max_workers):
            task_queue.put(None)
        for future in futures:
            future.result()

