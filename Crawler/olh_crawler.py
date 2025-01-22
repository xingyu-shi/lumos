import os
import pickle
import threading
from concurrent.futures import ThreadPoolExecutor

import requests
from bs4 import BeautifulSoup
import re

from dotenv import load_dotenv

from Crawler.utils import parse_cookie_str, sanitize_filename
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

load_dotenv()

lock = threading.Lock()
WORKING_DIR = "olh_workspace_v2"
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

def mark_crawled(url):
    with lock:
        crawled.add(url)
        with open(os.path.join(BASEDIR, WORKING_DIR, "_crawled.pkl"), "wb") as f:
            pickle.dump(crawled, f)

def is_crawled(url):
    return url in crawled

if not os.path.exists(os.path.join(BASEDIR, WORKING_DIR, "_to_crawl.pkl")):
    crawl_list = set()
    with open(os.path.join(BASEDIR, WORKING_DIR, "_to_crawl.pkl"), "wb") as f:
        pickle.dump(crawl_list, f)
else:
    with open(os.path.join(BASEDIR, WORKING_DIR, "_to_crawl.pkl"), "rb") as f:
        crawl_list = pickle.load(f)

def add_to_crawler_waitlist(urls):
    with lock:
        for url in urls if isinstance(urls, list) else [urls]:
            if not is_crawled(url) and not url in crawl_list:
                crawl_list.add(url)
        with open(os.path.join(BASEDIR, WORKING_DIR, "_to_crawl.pkl"), "wb") as f:
            pickle.dump(crawl_list, f)

def scraper(url: str):
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
    print(f"title: {sanitize_filename(title)}\n")
    contents = []

    if url.startswith('https://docs.trendmicro.com'):
        hrefs = []
        for card in soup.find_all('article', attrs={"class": "OLH-card"}):
            for a_tag in card.find_all('a'):
                if not 'href' in a_tag.attrs:
                    continue
                if not a_tag['href'].startswith('http'):
                    a_tag['href'] = f"{url.rpartition('/')[0]}/{a_tag['href']}"
                hrefs.append(a_tag['href'])

        for main in soup.find_all('div', attrs={"id": "wh-content"}):
            for a_tag in main.find_all('a'):
                if not 'href' in a_tag.attrs:
                    continue
                if not a_tag['href'].startswith('http'):
                    a_tag['href'] = f"{url.rpartition('/')[0]}/{a_tag['href']}"
                hrefs.append(a_tag['href'])

        for main in soup.find_all('div', attrs={"class": "article-menu"}):
            for a_tag in main.find_all('a'):
                if not 'href' in a_tag.attrs:
                    continue
                if not a_tag['href'].startswith('http'):
                    a_tag['href'] = f"{url.rpartition('/')[0]}/{a_tag['href']}"
                hrefs.append(a_tag['href'])

        add_to_crawler_waitlist(hrefs)

        # 移除 <style> 标签
        # 获取页面内容
        for content in soup.find_all('div', attrs={'id': 'wh-content'}):
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
    else:
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

        for a in soup.find_all('a'):
            if not "href" in a.attrs:
                continue
            # 获取链接的文本和 href 属性
            link_text = a.get_text()
            link_href = a['href']
            # 替换为原始超链接
            a.replace_with(f'{link_text} ({link_href})')

        # 展开收起来的文本块
        for div in soup.find_all('div', class_='collapsed'):
            div['style'] = ''

        for tag in soup.find_all('div', attrs={'data-testid': 'content-header-container'}):
            tag.decompose()

        for tag in soup.find_all('h1', attrs={'id': 'title-text'}):
            contents.append(tag.get_text())
            tag.decompose()

        contents.append(soup.get_text().replace('\xa0', ' '))
    if "\n".join(contents).strip() == "":
        return

    with open(os.path.join(BASEDIR, WORKING_DIR, f"{sanitize_filename(title+"_"+url)}.txt"), "w", encoding="utf-8") as f:
        f.write(f'link: {url}\n\n')
        f.write("\n".join(contents))


def scraper_(url):
    try:
        scraper(url)
        mark_crawled(url)
    except Exception as e:
        print(f"{url} error: {e}")
        add_to_crawler_waitlist(url)

# 使用爬虫抓取一个目标网站
if __name__ == "__main__":
    add_to_crawler_waitlist("https://docs.trendmicro.com/en-us/documentation/cloud-app-security/")
    with ThreadPoolExecutor(max_workers=3) as executor:
        while len(crawl_list) > 0:
            target_url = crawl_list.pop()
            print(f"processing {target_url}, total: {len(crawl_list)}")
            executor.submit(scraper_, target_url)

