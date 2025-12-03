from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import requests
import os
import time

# 更简单的备选方案 - 使用必应图片搜索
def download_from_bing(keyword, save_dir='./images'):
    """
    使用必应图片搜索（通常更稳定）
    """
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    
    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)
        
        # 访问必应图片
        encoded_keyword = requests.utils.quote(keyword)
        url = f"https://www.bing.com/images/search?q={encoded_keyword}"
        driver.get(url)
        
        # 等待图片加载
        time.sleep(3)
        
        # 查找图片元素
        img_element = driver.find_element(By.CSS_SELECTOR, '.mimg')
        img_url = img_element.get_attribute('src')
        
        if not img_url:
            print("未找到图片URL")
            return None
        
        # 下载图片
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://www.bing.com/'
        }
        
        img_response = requests.get(img_url, headers=headers)
        filename = f"{keyword}.jpg"
        filepath = os.path.join(save_dir, filename)
        
        with open(filepath, 'wb') as f:
            f.write(img_response.content)
        
        print(f"必应图片下载成功: {filepath}")
        return filepath
        
    except Exception as e:
        print(f"必应下载失败: {e}")
        return None
    finally:
        if driver:
            driver.quit()

# 使用示例
if __name__ == "__main__":
    keyword = "可乐鸡翅"  # 替换成你想要搜索的关键词
    download_from_bing(keyword)