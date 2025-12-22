"""
食堂消费数据爬取服务
从清华大学一卡通系统获取消费数据
"""
import base64
import json
import uuid
import threading
from typing import Dict, Optional

import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

# 全局登录会话管理
LOGIN_SESSIONS = {}
SESSION_LOCK = threading.Lock()


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
        from datetime import datetime, timedelta

        # 计算近三个月的日期范围
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)  # 近三个月

        start_time = start_date.strftime('%Y-%m-%d')
        end_time = end_date.strftime('%Y-%m-%d')

        # 发送请求到清华一卡通系统（近三个月数据）
        url = (
            f"https://card.tsinghua.edu.cn/business/querySelfTradeList"
            f"?pageNumber=0&pageSize=5000"
            f"&starttime={start_time}&endtime={end_time}"
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

        # 按食堂统计消费金额（只统计食堂，即名称以"园"结尾的）
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

                # 只统计食堂（以"园"结尾的商户，如"紫荆园"、"桃李园"等）
                if not canteen_name.endswith("园"):
                    continue

                # 确保txamt是数字类型
                txamt = item["txamt"]
                if not isinstance(txamt, (int, float)):
                    continue

                # 累加该食堂的消费金额
                if canteen_name in canteen_data:
                    canteen_data[canteen_name] += txamt
                else:
                    canteen_data[canteen_name] = txamt
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
    idserial: Optional[str] = None,
    browser_type: str = 'chrome',
    max_wait_time: int = 300
) -> Dict:
    """
    打开浏览器，等待用户手动登录，自动获取servicehall cookie和学号

    Args:
        idserial: 学号（可选，如果为None则从网页自动获取）
        browser_type: 浏览器类型 ('chrome', 'firefox', 'edge', 'safari')
        max_wait_time: 最大等待时间（秒），默认300秒（5分钟）

    Returns:
        {
            "success": bool,
            "servicehall": str 或 None,
            "idserial": str 或 None,  # 新增：自动获取的学号
            "error": str 或 None
        }
    """
    import time
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    driver = None
    try:
        # 获取对应浏览器的WebDriver
        driver = get_browser_driver(browser_type)

        # 打开清华大学一卡通网站
        driver.get("https://card.tsinghua.edu.cn/userselftrade")

        # 等待用户登录并检测cookie
        start_time = time.time()
        servicehall = None
        extracted_idserial = idserial  # 保存传入的学号或提取的学号

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
                "idserial": None,
                "error": "超时：未能获取servicehall cookie，请确保已成功登录网站"
            }

        # 如果未提供学号，尝试从 userinfo 页面自动获取
        if not extracted_idserial:
            try:
                # 访问 userinfo 页面
                driver.get("https://card.tsinghua.edu.cn/userinfo")

                # 等待页面加载完成并查找学号元素
                # 使用WebDriverWait等待元素出现（最多等待10秒）
                wait = WebDriverWait(driver, 10)
                idserial_element = wait.until(
                    EC.presence_of_element_located((By.ID, "idserial"))
                )

                # 等待页面渲染完成
                import time
                # time.sleep(1)

                # 获取学号文本
                extracted_idserial = idserial_element.text.strip()

                # 如果.text为空,尝试其他方式
                if not extracted_idserial:
                    extracted_idserial = idserial_element.get_attribute('textContent').strip()

                if not extracted_idserial:
                    extracted_idserial = idserial_element.get_attribute('innerHTML').strip()

                if not extracted_idserial:
                    return {
                        "success": False,
                        "servicehall": None,
                        "idserial": None,
                        "error": "获取学号失败：页面中找到了学号元素但内容为空"
                    }

            except Exception as e:
                return {
                    "success": False,
                    "servicehall": None,
                    "idserial": None,
                    "error": f"自动获取学号失败: {str(e)}"
                }

        return {
            "success": True,
            "servicehall": servicehall,
            "idserial": extracted_idserial,  # 返回提取的学号
            "error": None
        }

    except ValueError as e:
        return {
            "success": False,
            "servicehall": None,
            "idserial": None,
            "error": str(e)
        }
    except ImportError as e:
        return {
            "success": False,
            "servicehall": None,
            "idserial": None,
            "error": str(e)
        }
    except Exception as e:
        return {
            "success": False,
            "servicehall": None,
            "idserial": None,
            "error": f"浏览器操作失败: {str(e)}"
        }

    finally:
        if driver:
            driver.quit()


def fetch_and_parse_consumption(
    idserial: Optional[str] = None,
    servicehall: Optional[str] = None,
    browser_type: str = 'chrome'
) -> Dict:
    """
    获取并解析食堂消费数据
    如果未提供servicehall，则自动打开浏览器获取
    如果未提供学号，则从网页自动提取

    Args:
        idserial: 学号（可选，如果为None则自动获取）
        servicehall: servicehall cookie（可选）
        browser_type: 浏览器类型（当需要获取cookie时使用）

    Returns:
        {
            "success": bool,
            "data": dict 或 None,
            "servicehall": str 或 None,
            "idserial": str 或 None,  # 新增：返回使用的学号
            "error": str 或 None
        }
    """
    # 如果没有提供servicehall，则通过浏览器获取（同时也会获取学号）
    if not servicehall:
        cookie_result = fetch_servicehall_cookie(idserial, browser_type)
        if not cookie_result["success"]:
            return {
                "success": False,
                "data": None,
                "servicehall": None,
                "idserial": None,
                "error": cookie_result["error"]
            }
        servicehall = cookie_result["servicehall"]
        # 如果没有提供学号，使用自动获取的学号
        if not idserial:
            idserial = cookie_result["idserial"]

    # 检查是否有学号
    if not idserial:
        return {
            "success": False,
            "data": None,
            "servicehall": servicehall,
            "idserial": None,
            "error": "未能获取学号，请手动提供或确保网页中包含学号信息"
        }

    # 获取消费数据
    data_result = fetch_canteen_data(idserial, servicehall)

    return {
        "success": data_result["success"],
        "data": data_result["data"],
        "servicehall": servicehall if data_result["success"] else None,
        "idserial": idserial if data_result["success"] else None,
        "error": data_result["error"]
    }


def auto_login_and_fetch_cookie(
    idserial: str,
    password: str,
    headless: bool = True,
    browser_type: str = 'chrome'
) -> Dict:
    """
    自动登录清华一卡通并获取cookie

    工作流程：
    1. 打开登录页面
    2. 填写学号密码
    3. 点击发送验证码按钮
    4. 暂停并等待外部提供验证码（通过 submit_verification_code 函数）
    5. 验证码输入后自动提交登录
    6. 提取 servicehall cookie

    Args:
        idserial: 学号
        password: 密码
        headless: 是否使用无头模式
        browser_type: 浏览器类型

    Returns:
        {
            "success": bool,
            "session_id": str,  # 会话ID，用于后续提交验证码
            "status": str,  # waiting_verification | completed | failed
            "servicehall": str 或 None,
            "idserial": str 或 None,
            "error": str 或 None
        }
    """
    session_id = str(uuid.uuid4())

    # 在新线程中执行登录流程
    thread = threading.Thread(
        target=_auto_login_thread,
        args=(session_id, idserial, password, headless, browser_type)
    )
    thread.daemon = True
    thread.start()

    # 等待初始化完成（最多60秒）
    import time
    max_wait = 60
    waited = 0
    while waited < max_wait:
        with SESSION_LOCK:
            if session_id in LOGIN_SESSIONS:
                session = LOGIN_SESSIONS[session_id]
                # 检查是否完成（成功、需要验证码、或失败）
                if session['status'] in ['waiting_verification', 'failed', 'completed']:
                    if session['status'] == 'completed':
                        # 直接登录成功，无需验证码
                        return {
                            "success": True,
                            "session_id": session_id,
                            "status": session['status'],
                            "servicehall": session.get('servicehall'),
                            "idserial": idserial,
                            "error": None
                        }
                    else:
                        # 需要验证码或失败
                        return {
                            "success": session['status'] == 'waiting_verification',
                            "session_id": session_id,
                            "status": session['status'],
                            "servicehall": None,
                            "idserial": idserial,
                            "error": session.get('error')
                        }
        time.sleep(0.5)
        waited += 0.5

    return {
        "success": False,
        "session_id": None,
        "status": "failed",
        "servicehall": None,
        "idserial": None,
        "error": "初始化登录流程超时"
    }


def _auto_login_thread(
    session_id: str,
    idserial: str,
    password: str,
    headless: bool,
    browser_type: str
):
    """
    自动登录的线程函数
    """
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    import time

    driver = None

    try:
        # 初始化会话
        with SESSION_LOCK:
            LOGIN_SESSIONS[session_id] = {
                'status': 'initializing',
                'driver': None,
                'error': None,
                'servicehall': None
            }

        # 获取浏览器驱动
        driver = _get_browser_driver_for_login(browser_type, headless)

        with SESSION_LOCK:
            LOGIN_SESSIONS[session_id]['driver'] = driver

        # 打开登录页面
        driver.get("https://card.tsinghua.edu.cn/userselftrade")

        # 等待页面加载
        wait = WebDriverWait(driver, 15)

        # 查找学号输入框（使用精确的XPath）
        try:
            username_input = wait.until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="i_user"]'))
            )
            username_input.clear()
            username_input.send_keys(idserial)

        except Exception as e:
            with SESSION_LOCK:
                LOGIN_SESSIONS[session_id]['status'] = 'failed'
                LOGIN_SESSIONS[session_id]['error'] = f"填写学号失败: {str(e)}"
            return

        # 查找密码输入框（使用精确的XPath）
        try:
            password_input = driver.find_element(By.XPATH, '//*[@id="i_pass"]')
            password_input.clear()
            password_input.send_keys(password)

        except Exception as e:
            with SESSION_LOCK:
                LOGIN_SESSIONS[session_id]['status'] = 'failed'
                LOGIN_SESSIONS[session_id]['error'] = f"填写密码失败: {str(e)}"
            return

        # 点击登录按钮（使用精确的XPath）
        try:
            login_button = driver.find_element(By.XPATH, '//*[@id="theform"]/div[5]/a')
            login_button.click()
            time.sleep(3)  # 等待登录响应

        except Exception as e:
            with SESSION_LOCK:
                LOGIN_SESSIONS[session_id]['status'] = 'failed'
                LOGIN_SESSIONS[session_id]['error'] = f"点击登录按钮失败: {str(e)}"
            return

        # 检查是否有用户名或密码错误提示
        try:
            error_msg = driver.find_element(By.XPATH, '//*[@id="msg_note"]')
            if error_msg and error_msg.is_displayed():
                error_text = error_msg.text.strip()
                if error_text:
                    with SESSION_LOCK:
                        LOGIN_SESSIONS[session_id]['status'] = 'failed'
                        LOGIN_SESSIONS[session_id]['error'] = f"登录失败: {error_text}"
                    return
        except:
            # 没有找到错误提示元素，说明没有错误，继续执行
            pass

        # 检查是否直接登录成功（情况2：无需验证码）
        servicehall = None
        cookies = driver.get_cookies()
        for cookie in cookies:
            if cookie['name'] == 'servicehall':
                servicehall = cookie['value']
                break

        if servicehall:
            # 直接登录成功，无需验证码
            with SESSION_LOCK:
                LOGIN_SESSIONS[session_id]['status'] = 'completed'
                LOGIN_SESSIONS[session_id]['servicehall'] = servicehall
            return

        # 情况1：需要验证码，查找验证界面
        try:
            # 等待验证界面加载（最多等待10秒）
            wait = WebDriverWait(driver, 10)

            # 尝试查找验证界面的单选按钮（使用元素属性定位）
            try:
                # 查找 <input name="type" type="radio" class="form-check-input" value="mobile">
                verification_method_input = wait.until(
                    EC.presence_of_element_located(
                        (By.XPATH, '//input[@name="type" and @type="radio" and @value="mobile"]')
                    )
                )

                # 找到验证界面，点击选择验证码发送方式（手机）
                verification_method_input.click()
                time.sleep(0.5)

                # 查找并点击确定按钮 <button type="submit" class="btn btn-info">确定</button>
                confirm_button = driver.find_element(
                    By.XPATH, '//button[@type="submit" and contains(@class, "btn-info")]'
                )
                confirm_button.click()
                time.sleep(2)  # 等待验证码发送

                # 成功处理验证界面
                print("成功点击验证界面按钮")

            except Exception as e:
                # 没有找到验证界面，可能页面结构不同
                # 尝试查找其他可能的发送验证码按钮
                print(f"未找到验证界面: {str(e)}")
                send_code_button = None
                selectors = [
                    (By.XPATH, "//button[contains(text(), '发送验证码')]"),
                    (By.XPATH, "//button[contains(text(), '获取验证码')]"),
                    (By.XPATH, "//a[contains(text(), '发送验证码')]"),
                    (By.ID, "sendCode"),
                    (By.CLASS_NAME, "send-code"),
                ]

                for by, selector in selectors:
                    try:
                        send_code_button = driver.find_element(by, selector)
                        if send_code_button:
                            send_code_button.click()
                            time.sleep(1)
                            print(f"找到并点击发送验证码按钮: {selector}")
                            break
                    except:
                        continue

                if not send_code_button:
                    # 既没有验证界面，也没有发送验证码按钮
                    # 保存页面源码用于调试
                    page_source = driver.page_source
                    with SESSION_LOCK:
                        LOGIN_SESSIONS[session_id]['status'] = 'failed'
                        LOGIN_SESSIONS[session_id]['error'] = '未找到验证界面或发送验证码按钮'
                    return

        except Exception as e:
            with SESSION_LOCK:
                LOGIN_SESSIONS[session_id]['status'] = 'failed'
                LOGIN_SESSIONS[session_id]['error'] = f"处理验证界面失败: {str(e)}"
            return

        # 更新状态为等待验证码
        with SESSION_LOCK:
            LOGIN_SESSIONS[session_id]['status'] = 'waiting_verification'

        # 等待验证码输入（最多5分钟）
        max_wait = 300
        waited = 0
        while waited < max_wait:
            with SESSION_LOCK:
                session = LOGIN_SESSIONS[session_id]
                if 'verification_code' in session:
                    verification_code = session['verification_code']
                    break
            time.sleep(1)
            waited += 1
        else:
            with SESSION_LOCK:
                LOGIN_SESSIONS[session_id]['status'] = 'failed'
                LOGIN_SESSIONS[session_id]['error'] = '等待验证码超时'
            return

        # 输入验证码
        try:
            # 使用精确的 XPath 定位验证码输入框
            code_input = driver.find_element(By.XPATH, '//*[@id="vericode"]')
            code_input.clear()
            code_input.send_keys(verification_code)

        except Exception as e:
            with SESSION_LOCK:
                LOGIN_SESSIONS[session_id]['status'] = 'failed'
                LOGIN_SESSIONS[session_id]['error'] = f"填写验证码失败: {str(e)}"
            return

        # 查找并点击登录按钮
        try:
            login_button = None
            selectors = [
                (By.XPATH, "//button[contains(text(), '登录')]"),
                (By.XPATH, "//button[@type='submit']"),
                (By.ID, "login"),
                (By.CLASS_NAME, "login-btn"),
            ]

            for by, selector in selectors:
                try:
                    login_button = driver.find_element(by, selector)
                    if login_button:
                        break
                except:
                    continue

            if not login_button:
                raise Exception("未找到登录按钮")

            login_button.click()
            time.sleep(3)  # 等待页面跳转

        except Exception as e:
            with SESSION_LOCK:
                LOGIN_SESSIONS[session_id]['status'] = 'failed'
                LOGIN_SESSIONS[session_id]['error'] = f"点击登录按钮失败: {str(e)}"
            return

        # 检查验证码是否错误
        try:
            error_feedback = driver.find_element(
                By.XPATH, '//div[@class="invalid-feedback" and contains(text(), "校验码错误")]'
            )
            if error_feedback and error_feedback.is_displayed():
                with SESSION_LOCK:
                    LOGIN_SESSIONS[session_id]['status'] = 'failed'
                    LOGIN_SESSIONS[session_id]['error'] = '验证码错误，请重试'
                print("检测到验证码错误")
                return
        except:
            # 没有找到错误提示，说明验证码正确，继续执行
            pass

        # 处理验证码提交后的确认界面
        try:
            # 等待确认界面加载
            wait = WebDriverWait(driver, 10)

            # 尝试查找"否"的单选按钮
            try:
                no_radio_button = wait.until(
                    EC.presence_of_element_located(
                        (By.XPATH, '//input[@name="type" and @type="radio" and @value="否"]')
                    )
                )
                # 点击"否"按钮
                no_radio_button.click()
                time.sleep(0.5)

                # 点击确定按钮
                confirm_button = driver.find_element(
                    By.XPATH, '//button[@type="button" and contains(@class, "btn-info")]'
                )
                confirm_button.click()
                time.sleep(2)  # 等待页面跳转

                print("成功处理验证码提交后的确认界面")

            except Exception as e:
                # 可能没有这个确认界面，直接跳过
                print(f"未找到确认界面（可能已直接跳转）: {str(e)}")
                pass

        except Exception as e:
            # 如果处理确认界面失败，不影响主流程，继续获取cookie
            print(f"处理确认界面时出错: {str(e)}")
            pass

        # 等待登录完成并获取cookie（最多20秒）
        time.sleep(1)  # 短暂等待页面跳转
        max_wait = 20
        waited = 0
        servicehall = None

        while waited < max_wait:
            cookies = driver.get_cookies()
            for cookie in cookies:
                if cookie['name'] == 'servicehall':
                    servicehall = cookie['value']
                    break

            if servicehall:
                # 立即更新状态
                with SESSION_LOCK:
                    LOGIN_SESSIONS[session_id]['status'] = 'completed'
                    LOGIN_SESSIONS[session_id]['servicehall'] = servicehall
                print(f"成功获取servicehall cookie: {servicehall[:50]}...")
                break

            time.sleep(0.5)  # 缩短等待间隔
            waited += 0.5

        if not servicehall:
            with SESSION_LOCK:
                LOGIN_SESSIONS[session_id]['status'] = 'failed'
                LOGIN_SESSIONS[session_id]['error'] = '登录失败：未能获取servicehall cookie'

    except Exception as e:
        with SESSION_LOCK:
            LOGIN_SESSIONS[session_id]['status'] = 'failed'
            LOGIN_SESSIONS[session_id]['error'] = f"登录过程出错: {str(e)}"

    finally:
        # 关闭浏览器
        if driver:
            try:
                driver.quit()
            except:
                pass


def _get_browser_driver_for_login(browser_type: str, headless: bool):
    """
    获取用于自动登录的浏览器驱动
    """
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options as ChromeOptions
        from selenium.webdriver.firefox.options import Options as FirefoxOptions
        from selenium.webdriver.edge.options import Options as EdgeOptions
    except ImportError:
        raise ImportError("未安装selenium库，请运行: pip install selenium")

    browser_type = browser_type.lower()

    if browser_type == 'chrome':
        options = ChromeOptions()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        return webdriver.Chrome(options=options)

    elif browser_type == 'firefox':
        options = FirefoxOptions()
        if headless:
            options.add_argument('--headless')
        options.set_preference("dom.webdriver.enabled", False)
        return webdriver.Firefox(options=options)

    elif browser_type == 'edge':
        options = EdgeOptions()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        return webdriver.Edge(options=options)

    else:
        raise ValueError(f"不支持的浏览器类型: {browser_type}")


def submit_verification_code(session_id: str, verification_code: str) -> Dict:
    """
    提交验证码到指定的登录会话

    Args:
        session_id: 登录会话ID
        verification_code: 验证码

    Returns:
        {
            "success": bool,
            "message": str
        }
    """
    with SESSION_LOCK:
        if session_id not in LOGIN_SESSIONS:
            return {
                "success": False,
                "message": "会话不存在或已过期"
            }

        session = LOGIN_SESSIONS[session_id]

        if session['status'] != 'waiting_verification':
            return {
                "success": False,
                "message": f"会话状态错误: {session['status']}"
            }

        # 设置验证码
        session['verification_code'] = verification_code

    return {
        "success": True,
        "message": "验证码已提交，正在登录..."
    }


def check_login_status(session_id: str) -> Dict:
    """
    检查登录会话的状态

    Args:
        session_id: 登录会话ID

    Returns:
        {
            "success": bool,
            "status": str,  # waiting_verification | completed | failed
            "servicehall": str 或 None,
            "error": str 或 None
        }
    """
    with SESSION_LOCK:
        if session_id not in LOGIN_SESSIONS:
            return {
                "success": False,
                "status": "not_found",
                "servicehall": None,
                "error": "会话不存在或已过期"
            }

        session = LOGIN_SESSIONS[session_id]

        return {
            "success": session['status'] == 'completed',
            "status": session['status'],
            "servicehall": session.get('servicehall'),
            "error": session.get('error')
        }


def cleanup_login_session(session_id: str):
    """
    清理登录会话
    """
    with SESSION_LOCK:
        if session_id in LOGIN_SESSIONS:
            session = LOGIN_SESSIONS[session_id]
            driver = session.get('driver')
            if driver:
                try:
                    driver.quit()
                except:
                    pass
            del LOGIN_SESSIONS[session_id]

