from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import requests
import os
import time
import urllib.parse

def download_high_quality_from_bing(keyword, save_dir='./images', min_width=800):
    """
    从必应下载高质量图片的优化版本
    """
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    chrome_options = Options()
    # 暂时禁用无头模式以便调试
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # 1. 优化搜索关键词，添加质量相关词汇
        quality_keywords = ["高清", "高质量", "4K", "高分辨率"]
        enhanced_keyword = f"{keyword} {' '.join(quality_keywords)}"
        encoded_keyword = urllib.parse.quote(enhanced_keyword)
        
        # 2. 使用必应的尺寸筛选功能
        url = f"https://www.bing.com/images/search?q={encoded_keyword}&qft=+filterui:imagesize-large"
        
        print(f"搜索URL: {url}")
        driver.get(url)
        
        # 3. 等待更长时间确保页面完全加载
        wait = WebDriverWait(driver, 15)
        
        # 4. 等待图片网格加载完成
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".imgpt")))
        time.sleep(2)
        
        # 5. 找到所有图片元素，选择第一个
        image_elements = driver.find_elements(By.CSS_SELECTOR, ".imgpt .mimg")
        
        if not image_elements:
            print("未找到图片元素")
            return None
        
        print(f"找到 {len(image_elements)} 张图片")
        
        # 6. 点击第一张图片打开详情页获取高质量版本
        first_image = image_elements[0]
        driver.execute_script("arguments[0].click();", first_image)
        time.sleep(2)
        
        # 7. 等待详情页加载并获取高质量图片URL
        try:
            # 尝试获取高质量图片元素
            high_quality_img = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".mainImage.current.active, .imgContainer img, [data-fancybox-href]"))
            )
            
            # 优先获取高质量图片URL
            img_url = high_quality_img.get_attribute('data-fancybox-href') or \
                     high_quality_img.get_attribute('data-src') or \
                     high_quality_img.get_attribute('src')
            
            # 如果还是没有高质量URL，尝试获取原始大图
            if not img_url or 'th?' in img_url:
                # 获取图片的原始链接
                img_url = high_quality_img.get_attribute('src')
                # 尝试将缩略图URL转换为原图URL
                if 'th?id=' in img_url:
                    img_url = img_url.replace('th?id=', 'th/id/')
                    img_url = img_url.split('&')[0]  # 移除尺寸参数获取原图
        
        except Exception as e:
            print(f"获取高质量图片失败: {e}")
            # 回退到原始方法
            img_url = first_image.get_attribute('src')
        
        if not img_url:
            print("未找到图片URL")
            return None
        
        print(f"图片URL: {img_url}")
        
        # 8. 下载图片
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://www.bing.com/',
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
        }
        
        # 添加重试机制
        max_retries = 3
        for attempt in range(max_retries):
            try:
                img_response = requests.get(img_url, headers=headers, timeout=30)
                img_response.raise_for_status()
                
                # 检查图片尺寸（如果可能）
                if len(img_response.content) < 50000:  # 如果图片太小（小于50KB）
                    print(f"图片可能太小 ({len(img_response.content)} bytes)，尝试第 {attempt + 1} 次重试")
                    if attempt < max_retries - 1:
                        time.sleep(1)
                        continue
                
                break
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                print(f"下载失败，第 {attempt + 1} 次重试: {e}")
                time.sleep(1)
        
        # 9. 生成高质量文件名
        file_extension = 'jpg'
        content_type = img_response.headers.get('content-type', '')
        if 'png' in content_type:
            file_extension = 'png'
        elif 'webp' in content_type:
            file_extension = 'webp'
        
        filename = f"{keyword}_high_quality_{int(time.time())}.{file_extension}"
        filepath = os.path.join(save_dir, filename)
        
        with open(filepath, 'wb') as f:
            f.write(img_response.content)
        
        # 10. 验证文件大小
        file_size = os.path.getsize(filepath)
        print(f"图片下载成功: {filepath} ({file_size} bytes)")
        
        if file_size < 50000:  # 小于50KB可能是低质量图片
            print("警告: 下载的图片文件较小，可能不是最高质量版本")
        
        return filepath
        
    except Exception as e:
        print(f"高质量图片下载失败: {e}")
        # 保存页面截图用于调试
        if driver:
            screenshot_path = os.path.join(save_dir, f"error_screenshot_{int(time.time())}.png")
            driver.save_screenshot(screenshot_path)
            print(f"错误截图已保存: {screenshot_path}")
        return None
    finally:
        if driver:
            driver.quit()

def download_multiple_qualities(keyword, save_dir='./images'):
    """
    尝试下载多个质量版本的图片
    """
    qualities = [
        ("超大图", "imagesize-wallpaper"),
        ("大图", "imagesize-large"), 
        ("中图", "imagesize-medium")
    ]
    
    for quality_name, quality_filter in qualities:
        print(f"尝试下载{quality_name}版本...")
        try:
            result = download_with_quality_filter(keyword, save_dir, quality_filter, quality_name)
            if result and os.path.getsize(result) > 100000:  # 大于100KB认为是高质量
                print(f"成功下载高质量图片: {result}")
                return result
        except Exception as e:
            print(f"{quality_name}下载失败: {e}")
            continue
    
    print("所有质量版本下载失败，尝试基础版本")
    return download_from_bing(keyword, save_dir)

def download_with_quality_filter(keyword, save_dir, quality_filter, quality_name):
    """使用特定质量筛选器下载"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    
    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)
        
        encoded_keyword = urllib.parse.quote(keyword)
        url = f"https://www.bing.com/images/search?q={encoded_keyword}&qft=+filterui:{quality_filter}"
        
        driver.get(url)
        time.sleep(3)
        
        # 获取第一张图片
        img_element = driver.find_element(By.CSS_SELECTOR, '.mimg')
        img_url = img_element.get_attribute('src')
        
        if not img_url:
            return None
        
        # 下载图片
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://www.bing.com/'
        }
        
        img_response = requests.get(img_url, headers=headers, timeout=30)
        img_response.raise_for_status()
        
        filename = f"{keyword}_{quality_name}_{int(time.time())}.jpg"
        filepath = os.path.join(save_dir, filename)
        
        with open(filepath, 'wb') as f:
            f.write(img_response.content)
        
        print(f"{quality_name}图片下载成功: {filepath}")
        return filepath
        
    except Exception as e:
        raise e
    finally:
        if driver:
            driver.quit()

# 你原来的函数（保留）
def download_from_bing(keyword, save_dir='./images'):
    """原始函数作为备选"""
    # ... 你原来的代码 ...

# 使用示例
if __name__ == "__main__":
    keyword = "可乐鸡翅"
    
    # 方法1: 尝试高质量版本
    print("方法1: 尝试下载高质量版本...")
    result = download_high_quality_from_bing(keyword)
    
    if not result:
        # 方法2: 尝试多个质量版本
        print("方法2: 尝试多个质量版本...")
        result = download_multiple_qualities(keyword)
    
    if result:
        print(f"最终下载成功: {result}")
    else:
        print("所有方法都失败了")