"""
自动获取servicehall cookie - 用户手动登录版本
打开浏览器，等待用户手动登录，自动捕获cookie后调用main.py
需要先安装: pip install selenium
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import base64
import json
import requests
import sys

def decrypt_aes_ecb(encrypted_data: str) -> str:
    """AES ECB解密"""
    key = encrypted_data[:16].encode('utf-8')
    encrypted_data = encrypted_data[16:]
    encrypted_data_bytes = base64.b64decode(encrypted_data)
    
    cipher = AES.new(key, AES.MODE_ECB)
    decrypted_data = unpad(cipher.decrypt(encrypted_data_bytes), AES.block_size)
    
    return decrypted_data.decode('utf-8')

def get_canteen_data(idserial, servicehall):
    """
    获取食堂消费数据
    
    Args:
        idserial: 学号
        servicehall: servicehall cookie值
    
    Returns:
        dict: 包含状态和数据的字典
    """
    try:
        # 发送请求
        url = f"https://card.tsinghua.edu.cn/business/querySelfTradeList?pageNumber=0&pageSize=5000&starttime=2024-01-01&endtime=2024-12-31&idserial={idserial}&tradetype=-1"
        cookie = {
            "servicehall": servicehall,
        }
        response = requests.post(url, cookies=cookie)
        
        # 检查响应状态
        if response.status_code != 200:
            return {
                "success": False,
                "error": f"HTTP请求失败，状态码: {response.status_code}"
            }
        
        # 解析响应
        response_data = json.loads(response.text)
        if "data" not in response_data:
            return {
                "success": False,
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
                "error": "解密后数据格式错误"
            }
        
        # 按食堂统计
        canteen_data = {}
        for item in data["resultData"]["rows"]:
            try:
                mername = item["mername"]
                # 提取食堂名称:取"_"或"-"之前的部分
                if "_" in mername:
                    canteen_name = mername.split("_")[0]
                elif "-" in mername:
                    canteen_name = mername.split("-")[0]
                else:
                    canteen_name = mername
                
                if canteen_name in canteen_data:
                    canteen_data[canteen_name] += item["txamt"]
                else:
                    canteen_data[canteen_name] = item["txamt"]
            except Exception:
                pass
        
        # 将分转换为元
        canteen_data = {k: round(v / 100, 2) for k, v in canteen_data.items()}
        
        # 按消费金额排序
        sorted_canteen_data = dict(sorted(canteen_data.items(), key=lambda x: x[1], reverse=True))
        
        return {
            "success": True,
            "data": {
                "idserial": idserial,
                "total_amount": round(sum(canteen_data.values()), 2),
                "canteen_count": len(canteen_data),
                "canteens": sorted_canteen_data
            }
        }
        
    except json.JSONDecodeError as e:
        return {
            "success": False,
            "error": f"JSON解析错误: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"数据获取失败: {str(e)}"
        }
        

def get_servicehall_cookie(idserial):
    """
    打开浏览器，等待用户手动登录，获取servicehall cookie
    
    Args:
        idserial: 学号
    
    Returns:
        servicehall cookie值
    """
    # 配置Chrome选项
    chrome_options = Options()
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    driver = None
    try:
        # 启动浏览器
        print("正在启动浏览器...")
        driver = webdriver.Chrome(options=chrome_options)
        
        # 打开清华大学一卡通网站
        print("正在打开清华大学一卡通网站...")
        driver.get("https://card.tsinghua.edu.cn/userselftrade")
        
        # 等待用户登录并检测cookie
        max_wait_time = 300  # 最多等待5分钟
        start_time = time.time()
        servicehall = None
        
        check_count = 0
        while time.time() - start_time < max_wait_time:
            # 每2秒检查一次cookie
            time.sleep(2)
            check_count += 1
            
            # 获取所有cookie
            cookies = driver.get_cookies()
            
            # 查找servicehall cookie
            for cookie in cookies:
                if cookie['name'] == 'servicehall':
                    servicehall = cookie['value']
                    break
            
            if servicehall:
                print(f"Cookie值: {servicehall}")
                break
        
        if not servicehall:
            return {
                "success": False,
                "error": "超时：未能获取servicehall cookie，请确保已成功登录网站"
            }
        
        # 保持浏览器打开2秒让用户看到成功提示
        # time.sleep(2)
        
        return {
            "success": True,
            "servicehall": servicehall
        }
        
    except Exception as e:
       return {
            "success": False,
            "error": f"浏览器操作失败: {str(e)}"
        }
    
    finally:
        if driver:
            print("\n关闭浏览器")
            driver.quit()

if __name__ == "__main__":
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        # print("用法: python auto_login.py <学号> [servicehall]")
        # print("\n说明:")
        # print("  只提供学号: 打开浏览器，等待用户登录，自动获取cookie和消费数据")
        # print("  提供学号和servicehall: 跳过浏览器登录，直接获取消费数据")
        # print("\n示例:")
        # print("  python auto_login.py 2021012345")
        # print("  python auto_login.py 2021012345 ZTQ0YjMzMzktOTk0Yi00ZTliLWI3ZmEtZmZlNzdjNTk4YWE3")
        sys.exit(1)
    
    idserial = sys.argv[1]
    
    result = None
    
    if len(sys.argv) == 3:
        # 直接使用提供的servicehall
        servicehall = sys.argv[2]
        print(f"学号: {idserial}")
        print(f"servicehall: {servicehall}")
        
        # 直接获取数据
        result = get_canteen_data(idserial, servicehall)
    else:
        # 需要通过浏览器获取servicehall
        print(f"学号: {idserial}\n")
        
        # 获取servicehall cookie
        cookie_result = get_servicehall_cookie(idserial)
        
        if not cookie_result["success"]:
            result = cookie_result
        else:
            servicehall = cookie_result["servicehall"]
            # 获取消费数据
            result = get_canteen_data(idserial, servicehall)
    
    # 输出JSON结果
    print("\n" + "="*60)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("="*60)
    
    # 根据结果设置退出码
    sys.exit(0 if result.get("success") else 1)
