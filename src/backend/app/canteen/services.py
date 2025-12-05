"""
食堂消费数据爬取服务
从清华大学一卡通系统获取消费数据
"""
import base64
import json
from typing import Dict, Optional

import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad


def decrypt_aes_ecb(encrypted_data: str) -> str:
    """
    AES ECB模式解密
    
    Args:
        encrypted_data: 加密的数据字符串
        
    Returns:
        解密后的字符串
    """
    key = encrypted_data[:16].encode('utf-8')
    encrypted_data = encrypted_data[16:]
    encrypted_data_bytes = base64.b64decode(encrypted_data)
    
    cipher = AES.new(key, AES.MODE_ECB)
    decrypted_data = unpad(cipher.decrypt(encrypted_data_bytes), AES.block_size)
    
    return decrypted_data.decode('utf-8')


def fetch_canteen_data(idserial: str, servicehall: str) -> Dict:
    """
    从清华一卡通系统获取食堂消费数据
    
    Args:
        idserial: 学号
        servicehall: servicehall cookie值
        
    Returns:
        包含成功状态和数据的字典
        {
            "success": bool,
            "data": {
                "idserial": str,
                "total_amount": float,
                "canteen_count": int,
                "canteens": dict
            } 或 None,
            "error": str 或 None
        }
    """
    try:
        # 发送请求到清华一卡通系统
        url = (
            f"https://card.tsinghua.edu.cn/business/querySelfTradeList"
            f"?pageNumber=0&pageSize=5000"
            f"&starttime=2024-01-01&endtime=2024-12-31"
            f"&idserial={idserial}&tradetype=-1"
        )
        cookie = {"servicehall": servicehall}
        response = requests.post(url, cookies=cookie, timeout=10)
        
        # 检查HTTP响应状态
        if response.status_code != 200:
            return {
                "success": False,
                "data": None,
                "error": f"HTTP请求失败，状态码: {response.status_code}"
            }
        
        # 解析响应JSON
        response_data = json.loads(response.text)
        if "data" not in response_data:
            return {
                "success": False,
                "data": None,
                "error": "响应数据格式错误，未找到data字段"
            }
        
        # 解密数据
        encrypted_string = response_data["data"]
        decrypted_string = decrypt_aes_ecb(encrypted_string)
        
        # 解析消费数据
        data = json.loads(decrypted_string)
        
        if "resultData" not in data or "rows" not in data["resultData"]:
            return {
                "success": False,
                "data": None,
                "error": "解密后数据格式错误，缺少resultData或rows字段"
            }
        
        # 按食堂统计消费金额
        canteen_data = {}
        for item in data["resultData"]["rows"]:
            try:
                mername = item["mername"]
                # 提取食堂名称: 取"_"或"-"之前的部分
                if "_" in mername:
                    canteen_name = mername.split("_")[0]
                elif "-" in mername:
                    canteen_name = mername.split("-")[0]
                else:
                    canteen_name = mername
                
                # 累加该食堂的消费金额
                if canteen_name in canteen_data:
                    canteen_data[canteen_name] += item["txamt"]
                else:
                    canteen_data[canteen_name] = item["txamt"]
            except (KeyError, TypeError):
                # 忽略格式错误的记录
                continue
        
        # 将分转换为元
        canteen_data = {k: round(v / 100, 2) for k, v in canteen_data.items()}
        
        # 按消费金额降序排序
        sorted_canteen_data = dict(
            sorted(canteen_data.items(), key=lambda x: x[1], reverse=True)
        )
        
        return {
            "success": True,
            "data": {
                "idserial": idserial,
                "total_amount": round(sum(canteen_data.values()), 2),
                "canteen_count": len(canteen_data),
                "canteens": sorted_canteen_data
            },
            "error": None
        }
        
    except json.JSONDecodeError as e:
        return {
            "success": False,
            "data": None,
            "error": f"JSON解析错误: {str(e)}"
        }
    except requests.RequestException as e:
        return {
            "success": False,
            "data": None,
            "error": f"网络请求失败: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "error": f"数据获取失败: {str(e)}"
        }


def get_browser_driver(browser_type: str = 'chrome'):
    """
    根据浏览器类型获取对应的WebDriver
    
    Args:
        browser_type: 浏览器类型，支持 'chrome', 'firefox', 'edge', 'safari'
        
    Returns:
        配置好的WebDriver实例
        
    Raises:
        ValueError: 不支持的浏览器类型
        ImportError: 未安装selenium或对应浏览器驱动
    """
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options as ChromeOptions
        from selenium.webdriver.firefox.options import Options as FirefoxOptions
        from selenium.webdriver.edge.options import Options as EdgeOptions
    except ImportError:
        raise ImportError(
            "未安装selenium库，请运行: pip install selenium"
        )
    
    browser_type = browser_type.lower()
    
    if browser_type == 'chrome':
        options = ChromeOptions()
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        return webdriver.Chrome(options=options)
    
    elif browser_type == 'firefox':
        options = FirefoxOptions()
        options.set_preference("dom.webdriver.enabled", False)
        return webdriver.Firefox(options=options)
    
    elif browser_type == 'edge':
        options = EdgeOptions()
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        return webdriver.Edge(options=options)
    
    elif browser_type == 'safari':
        # Safari需要在系统偏好设置中启用远程自动化
        return webdriver.Safari()
    
    else:
        raise ValueError(
            f"不支持的浏览器类型: {browser_type}。"
            f"支持的类型: chrome, firefox, edge, safari"
        )


def fetch_servicehall_cookie(
    idserial: str,
    browser_type: str = 'chrome',
    max_wait_time: int = 300
) -> Dict:
    """
    打开浏览器，等待用户手动登录，自动获取servicehall cookie
    
    Args:
        idserial: 学号
        browser_type: 浏览器类型 ('chrome', 'firefox', 'edge', 'safari')
        max_wait_time: 最大等待时间（秒），默认300秒（5分钟）
        
    Returns:
        {
            "success": bool,
            "servicehall": str 或 None,
            "error": str 或 None
        }
    """
    import time
    
    driver = None
    try:
        # 获取对应浏览器的WebDriver
        driver = get_browser_driver(browser_type)
        
        # 打开清华大学一卡通网站
        driver.get("https://card.tsinghua.edu.cn/userselftrade")
        
        # 等待用户登录并检测cookie
        start_time = time.time()
        servicehall = None
        
        while time.time() - start_time < max_wait_time:
            # 每2秒检查一次cookie
            time.sleep(2)
            
            # 获取所有cookie
            cookies = driver.get_cookies()
            
            # 查找servicehall cookie
            for cookie in cookies:
                if cookie['name'] == 'servicehall':
                    servicehall = cookie['value']
                    break
            
            if servicehall:
                break
        
        if not servicehall:
            return {
                "success": False,
                "servicehall": None,
                "error": "超时：未能获取servicehall cookie，请确保已成功登录网站"
            }
        
        return {
            "success": True,
            "servicehall": servicehall,
            "error": None
        }
        
    except ValueError as e:
        return {
            "success": False,
            "servicehall": None,
            "error": str(e)
        }
    except ImportError as e:
        return {
            "success": False,
            "servicehall": None,
            "error": str(e)
        }
    except Exception as e:
        return {
            "success": False,
            "servicehall": None,
            "error": f"浏览器操作失败: {str(e)}"
        }
    
    finally:
        if driver:
            driver.quit()


def fetch_and_parse_consumption(
    idserial: str,
    servicehall: Optional[str] = None,
    browser_type: str = 'chrome'
) -> Dict:
    """
    获取并解析食堂消费数据
    如果未提供servicehall，则自动打开浏览器获取
    
    Args:
        idserial: 学号
        servicehall: servicehall cookie（可选）
        browser_type: 浏览器类型（当需要获取cookie时使用）
        
    Returns:
        {
            "success": bool,
            "data": dict 或 None,
            "servicehall": str 或 None,
            "error": str 或 None
        }
    """
    # 如果没有提供servicehall，则通过浏览器获取
    if not servicehall:
        cookie_result = fetch_servicehall_cookie(idserial, browser_type)
        if not cookie_result["success"]:
            return {
                "success": False,
                "data": None,
                "servicehall": None,
                "error": cookie_result["error"]
            }
        servicehall = cookie_result["servicehall"]
    
    # 获取消费数据
    data_result = fetch_canteen_data(idserial, servicehall)
    
    return {
        "success": data_result["success"],
        "data": data_result["data"],
        "servicehall": servicehall if data_result["success"] else None,
        "error": data_result["error"]
    }
