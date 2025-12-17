import os
import random
import requests

keyword = "可乐鸡翅"
save_dir = "downloads"
os.makedirs(save_dir, exist_ok=True)

session = requests.Session()

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Referer": "https://image.baidu.com/",
    "X-Requested-With": "XMLHttpRequest",
    "X-Forwarded-For": f"1.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}",
}

# 关键：先访问一次百度获得真实 Cookie
session.get("https://image.baidu.com", headers=headers)

url = "https://image.baidu.com/search/acjson"

params = {
    "tn": "resultjson_com",
    "ipn": "rj",
    "ct": "201326592",
    "cl": "2",
    "lm": "-1",
    "word": keyword,
    "queryWord": keyword,
    "pn": "0",
    "rn": "30",
}

resp = session.get(url, params=params, headers=headers)
data = resp.json()

if "data" not in data:
    print("仍然被屏蔽，返回：", data)
else:
    print("成功获取 data")

# 下载图片
index = 0
for item in data.get("data", []):
    if isinstance(item, dict) and "thumbURL" in item:
        img_url = item["thumbURL"]
        try:
            img = session.get(img_url, timeout=5).content
            with open(f"{save_dir}/{index}.jpg", "wb") as f:
                f.write(img)
            print("download:", img_url)
            index += 1
        except:
            pass
