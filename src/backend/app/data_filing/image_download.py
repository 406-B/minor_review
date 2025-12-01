import os
import requests
import json
from urllib.parse import quote


def duckduckgo_search_images(keyword, max_results=20):
    # 第一步：获取搜索 token
    search_url = f"https://duckduckgo.com/?q={quote(keyword)}&iax=images&ia=images"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    res = requests.get(search_url, headers=headers)
    token = res.text.split('vqd="')[1].split('"')[0]

    # 第二步：用 token 获取图片
    api_url = "https://duckduckgo.com/i.js"
    params = {
        "q": keyword,
        "vqd": token,
        "o": "json",
        "p": "1",
        "ia": "images"
    }

    image_urls = []
    while len(image_urls) < max_results:
        resp = requests.get(api_url, params=params, headers=headers)
        data = resp.json()
        for img in data.get("results", []):
            image_urls.append(img["image"])
            if len(image_urls) >= max_results:
                break

        if "next" not in data:
            break

        api_url = "https://duckduckgo.com/" + data["next"]

    return image_urls[:max_results]


def download_image(url, path):
    try:
        r = requests.get(url, timeout=10)
        ext = url.split(".")[-1]
        if len(ext) > 4:
            ext = "jpg"
        with open(f"{path}.{ext}", "wb") as f:
            f.write(r.content)
        print("✓ 下载成功:", path)
    except:
        print("× 下载失败:", url)


def download_for_keyword(keyword, num=20):
    folder = f"images/{keyword}"
    os.makedirs(folder, exist_ok=True)

    urls = duckduckgo_search_images(keyword, num)

    for i, url in enumerate(urls):
        download_image(url, f"{folder}/{keyword}_{i}")


def batch_download_from_file(keyword_file, num=20):
    with open(keyword_file, "r", encoding="utf-8") as f:
        keywords = [line.strip() for line in f if line.strip()]

    for k in keywords:
        print(f"\n===== 下载：{k} =====")
        download_for_keyword(k, num)


if __name__ == "__main__":
    batch_download_from_file("keywords.txt", num=20)
