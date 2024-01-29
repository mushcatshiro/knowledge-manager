"""
source: https://github.com/Geralt-TYH/obsidian-zhihu-crawler/tree/master
goal is to pre-scrap urls into database and access through admin route
to execute content scrap
"""
import random
import re
import os
import time
import requests as r
from bs4 import BeautifulSoup
import markdown


md = markdown.Markdown()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
    "Connection": "keep-alive",
    "Accept": "text/html,application/json,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.8",
}


def filter_title_str(str):
    filterStr = re.sub('[\/\\\\"<>\|]', " ", str)
    filterStr = re.sub("\?", "？", filterStr)
    filterStr = re.sub(":", "：", filterStr)
    return filterStr


def get_article_urls_in_collection(collection_id):
    collection_id = collection_id.replace("\n", "")

    offset = 0
    limit = 20

    collection_url = f"https://www.zhihu.com/api/v4/collections/{collection_id}/items"
    html = r.get(collection_url, headers=headers)
    html.raise_for_status()
    article_nums = html.json()["paging"].get("totals")
    if article_nums <= 0:
        raise

    url_list = []
    title_list = []
    while offset < article_nums:
        collection_url = (
            "https://www.zhihu.com/api/v4/collections"
            f"/{collection_id}/items?offset={offset}&limit={limit}"
        )
        try:
            html = r.get(collection_url, headers=headers)
            content = html.json()
        except:
            return None

        for el in content["data"]:
            url_list.append(el["content"]["url"])
            if el["content"]["type"] == "answer":
                title_list.append(el["content"]["question"]["title"])
            else:
                title_list.append(el["content"]["title"])

        offset += limit

    return url_list, title_list


def get_single_answer_content(answer_url):
    # all_content = {}
    # question_id, answer_id = re.findall('https://www.zhihu.com/question/(\d+)/answer/(\d+)', answer_url)[0]

    html_content = r.get(answer_url, headers=headers)
    soup = BeautifulSoup(html_content.text, "lxml")
    answer_content = soup.find("div", class_="AnswerCard").find(
        "div", class_="RichContent-inner"
    )
    # remove style element
    for el in answer_content.find_all("style"):
        el.extract()

    for el in answer_content.select('img[src*="data:image/svg+xml"]'):
        el.extract()

    return answer_content


def get_single_post_content(paper_url):
    html_content = r.get(paper_url, headers=headers)
    soup = BeautifulSoup(html_content.text, "lxml")
    post_content = soup.find("div", class_="Post-RichText")
    # remove style element
    if post_content:
        for el in post_content.find_all("style"):
            el.extract()

        for el in post_content.select('img[src*="data:image/svg+xml"]'):
            el.extract()
    else:
        post_content = "404 no access to pose"

    return post_content


if __name__ == "__main__":
    collection_id = []
    urls, titles = get_article_urls_in_collection(collection_id)

    for i in range(len(urls)):
        content = None
        url = urls[i]
        title = titles[i]

        if url.find("zhuanlan") != -1:
            content = get_single_post_content(url)
        else:
            content = get_single_answer_content(url)

        md_content = md(content, heading_style="ATX")
        id = url.split("/")[-1]

        downloadDir = os.path.join(os.path.expanduser("~"), "Downloads")

        with open(
            os.path.join(downloadDir, filter_title_str(title) + ".md"),
            "w",
            encoding="utf-8",
        ) as md_file:
            md_file.write(md_content)
        time.sleep(random.randint(1, 5))
