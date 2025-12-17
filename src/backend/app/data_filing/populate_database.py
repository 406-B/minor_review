"""
数据库填充脚本
自动生成食堂的楼层、窗口、菜品数据
支持清空和重新填充模式
"""

import os
import sys
import django
import argparse
import random
import time
import urllib.parse
from pathlib import Path
from decimal import Decimal

# 设置 Django 环境
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

from list.models import Canteen, Floor, Window, Dish, Tag
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from openai import OpenAI

# DeepSeek API 配置
DEEPSEEK_API_KEY = "sk-1b99a2e2a88441239e2988bdda668e63"
DEEPSEEK_BASE_URL = "https://api.deepseek.com"

# 基础标签列表 - 用于tags(管理员审核后的)
BASE_TAG_NAMES = [
    "辣", "微辣", "特辣", "不辣",
    "素菜", "荤菜", "半荤半素",
    "热菜", "凉菜", "汤",
    "主食", "小吃", "饮料", "甜品",
    "川菜", "湘菜", "粤菜", "鲁菜", "苏菜", "浙菜", "闽菜", "徽菜",
    "清淡", "重口味", "酸", "甜", "咸", "鲜",
    "油炸", "蒸", "煮", "炒", "烤", "炖", "煎",
    "高蛋白", "低脂", "高纤维", "低糖",
    "早餐", "午餐", "晚餐", "夜宵",
    "快餐", "套餐", "单点",
]

# Pending标签列表 - 用于pending_tags(用户提交,待审核)
PENDING_TAG_NAMES = [
    "营养丰富", "开胃", "下饭", "养生",
    "学生最爱", "教师推荐", "人气菜品", "特色菜",
    "经济实惠", "物美价廉", "性价比高",
    "新品推荐", "经典菜品", "家常菜",
]

# 菜品与标签的映射关系
DISH_TAG_MAPPING = {
    # 辣度标签
    "辣": ["麻辣烫", "水煮鱼", "水煮牛肉", "辣子鸡丁", "香辣鸡翅", "香辣蟹", "干锅鱿鱼", "麻辣香锅", "酸辣粉", "酸辣汤",
          "麻辣火锅", "香辣鱿鱼", "辣炒花甲", "小炒肉", "小炒黄牛肉", "干锅牛肉", "干锅土豆片", "干锅包菜", "麻辣鱼片",
          "泡菜汤", "泡菜炒饭", "冬阴功汤", "泰式炒河粉", "酸汤鱼", "烤辣椒", "虎皮尖椒"],
    "微辣": ["宫保鸡丁", "鱼香肉丝", "回锅肉", "鱼香茄子", "虎皮尖椒", "宫保虾球", "京酱肉丝", "孜然羊肉", "孜然牛肉",
            "椒盐排骨", "椒盐虾", "椒盐鱿鱼", "铁板鱿鱼", "避风塘炒蟹", "咖喱鸡", "咖喱牛肉", "咖喱虾"],
    "不辣": ["白切鸡", "清蒸鱼", "白灼虾", "清炒时蔬", "盐水鸭", "盐水虾", "清蒸螃蟹", "清蒸鲈鱼", "蒜蓉生蚝",
            "日本豆腐", "小葱拌豆腐", "皮蛋豆腐", "上汤娃娃菜", "白菜豆腐汤", "白灼芥兰"],
    
    # 荤素标签
    "素菜": ["麻婆豆腐", "家常豆腐", "红烧豆腐", "清炒时蔬", "蒜蓉油菜", "上汤娃娃菜", "炝炒圆白菜",
            "鱼香茄子", "红烧茄子", "西红柿炒鸡蛋", "地三鲜", "醋溜土豆丝", "蒜蓉西兰花", "干锅花菜",
            "手撕包菜", "虎皮尖椒", "凉拌黄瓜", "拍黄瓜", "老醋花生", "凉拌木耳", "锅塌豆腐", "皮蛋豆腐",
            "日本豆腐", "客家酿豆腐", "煎豆腐", "炸豆腐", "白菜炖粉条", "油焖茄子", "蒜泥茄子", "茄子煲",
            "蒜蓉生菜", "蚝油生菜", "清炒菠菜", "蒜蓉菠菜", "菠菜豆腐汤", "酸辣藕片", "糖醋藕片", "炸藕盒",
            "蒜蓉油麦菜", "清炒芦笋", "白灼芥兰", "蚝油芥兰", "炒豆芽", "炒芹菜", "凉拌芹菜", "炒苦瓜",
            "烤蔬菜", "烤茄子", "烤韭菜", "烤金针菇", "烤香菇", "烤玉米", "烤土豆", "烤红薯", "烤南瓜",
            "金针菇", "平菇", "香菇", "木耳", "海带", "土豆片", "莲藕片", "冬瓜", "白萝卜", "娃娃菜"],
    "荤菜": ["红烧肉", "梅菜扣肉", "东坡肉", "糖醋里脊", "糖醋排骨", "宫保鸡丁", "可乐鸡翅",
            "北京烤鸭", "红烧牛肉", "红烧鱼", "油焖大虾", "回锅肉", "京酱肉丝", "青椒肉丝", "木须肉",
            "红烧排骨", "蒜香排骨", "豉汁排骨", "粉蒸排骨", "排骨炖豆角", "排骨煲", "辣子鸡丁", "口水鸡",
            "叫花鸡", "大盘鸡", "三杯鸡", "盐焗鸡", "手撕鸡", "红烧鸡翅", "盐焗鸡翅", "蒜香鸡翅",
            "啤酒鸭", "酱板鸭", "香酥鸭", "黑椒牛柳", "孜然牛肉", "牛腩煲", "番茄牛腩", "土豆炖牛肉",
            "葱爆羊肉", "手抓羊肉", "羊肉串", "红烧狮子头", "四喜丸子", "酱牛肉", "卤牛肉", "红烧猪蹄",
            "叉烧", "蜜汁叉烧", "锅包肉", "溜肉段", "熘肝尖", "爆炒腰花", "九转大肠"],
    "半荤半素": ["麻婆豆腐", "肉末茄子", "木耳炒鸡蛋", "韭菜炒鸡蛋", "青椒炒鸡蛋", "洋葱炒鸡蛋", "苦瓜炒鸡蛋",
                "丝瓜炒鸡蛋", "芹菜炒肉", "芹菜炒香干", "苦瓜炒肉", "芦笋炒虾仁", "芦笋培根"],
    "海鲜": ["红烧鱼", "清蒸鱼", "糖醋鱼", "酸菜鱼", "水煮鱼", "剁椒鱼头", "松鼠鳜鱼", "西湖醋鱼", "烤鱼",
            "红烧大虾", "油焖大虾", "白灼虾", "盐水虾", "椒盐虾", "蒜蓉虾", "油爆虾", "龙井虾仁", "凤尾虾",
            "蒜蓉扇贝", "粉丝扇贝", "烤扇贝", "清蒸螃蟹", "香辣蟹", "咖喱蟹", "避风塘炒蟹", "葱姜炒蟹",
            "鱿鱼圈", "铁板鱿鱼", "干锅鱿鱼", "爆炒鱿鱼", "清蒸鲈鱼", "红烧鲤鱼", "糖醋黄花鱼", "椒盐多宝鱼",
            "海鲜烩", "海鲜粥", "海鲜炒饭", "海鲜火锅", "海鲜汤", "蒜蓉生蚝", "烤生蚝", "花甲", "爆炒花甲",
            "刺身", "三文鱼刺身", "金枪鱼刺身", "寿司", "三文鱼寿司", "海鲜意面", "海鲜焗饭", "海鲜披萨"],
    
    # 主食类
    "主食": ["米饭", "炒饭", "蛋炒饭", "扬州炒饭", "酱油炒饭", "菠萝炒饭", "虾仁炒饭", "叉烧炒饭", "福建炒饭", "泰式炒饭",
            "面条", "炒面", "拉面", "刀削面", "牛肉面", "鸡丝凉面", "担担面", "炸酱面", "热干面", "臊子面", "油泼面",
            "馒头", "花卷", "包子", "肉包", "菜包", "豆沙包", "叉烧包", "流沙包", "小笼包",
            "饺子", "水饺", "煎饺", "蒸饺", "馄饨", "云吞", "抄手", "锅贴", "煎包", "生煎包",
            "粥", "白粥", "皮蛋瘦肉粥", "海鲜粥", "八宝粥", "小米粥", "南瓜粥", "红豆粥", "绿豆粥",
            "米粉", "桂林米粉", "螺蛳粉", "酸辣粉", "过桥米线", "重庆小面", "肠粉", "河粉", "炒河粉",
            "日式拉面", "豚骨拉面", "味增拉面", "酱油拉面", "乌冬面", "炒乌冬", "荞麦面", "意大利面",
            "紫菜包饭", "饭团", "石锅拌饭", "煲仔饭", "盖浇饭", "烧腊饭", "卤肉饭"],
    "面食": ["面条", "炒面", "拉面", "刀削面", "牛肉面", "担担面", "炸酱面", "热干面", "阳春面", "葱油拌面",
            "日式拉面", "豚骨拉面", "乌冬面", "荞麦面", "意大利面", "越南河粉", "泰式炒河粉"],
    
    # 中式菜系
    "川菜": ["麻辣烫", "水煮鱼", "水煮牛肉", "宫保鸡丁", "鱼香肉丝", "回锅肉", "麻婆豆腐", "夫妻肺片", "担担面",
            "酸辣粉", "重庆小面", "毛血旺", "麻辣香锅", "麻辣火锅"],
    "粤菜": ["白切鸡", "烧鸭", "烧鹅", "叉烧", "蜜汁叉烧", "烧排骨", "脆皮烤肉", "煲仔饭", "肠粉", "虾饺",
            "烧卖", "叉烧包", "流沙包", "凤爪", "排骨", "上汤娃娃菜", "蚝油生菜", "白灼芥兰"],
    "湘菜": ["剁椒鱼头", "小炒肉", "辣椒炒肉", "湘西外婆菜", "口味虾", "口味蟹"],
    "鲁菜": ["九转大肠", "糖醋鲤鱼", "葱爆羊肉", "德州扒鸡", "四喜丸子"],
    "苏菜": ["松鼠鳜鱼", "水晶肴肉", "狮子头", "盐水鸭", "鸭血粉丝汤"],
    "浙菜": ["西湖醋鱼", "东坡肉", "龙井虾仁", "叫花鸡", "宋嫂鱼羹"],
    "徽菜": ["臭鳜鱼", "红烧划水", "毛豆腐", "问政山笋"],
    "闽菜": ["佛跳墙", "荔枝肉", "醉排骨", "沙茶面"],
    
    # 国际料理
    "日料": ["寿司", "刺身", "天妇罗", "拉面", "乌冬面", "荞麦面", "饭团", "铁板烧", "章鱼烧", "鳗鱼饭"],
    "韩餐": ["韩式烤肉", "石锅拌饭", "泡菜", "泡菜汤", "泡菜炒饭", "海鲜煎饼", "部队锅", "参鸡汤"],
    "西餐": ["牛排", "猪排", "鸡排", "意大利面", "披萨", "汉堡", "三明治", "沙拉", "奶油蘑菇汤", "罗宋汤"],
    "东南亚": ["咖喱", "冬阴功汤", "椰汁咖喱", "泰式炒河粉", "越南春卷", "越南河粉", "印尼炒饭", "肉骨茶", "叻沙"],
    
    # 小吃饮料
    "小吃": ["煎饼果子", "肉夹馍", "生煎包", "锅贴", "春卷", "油条", "麻辣烫", "关东煮", "烤串", "炸鸡",
            "麻团", "芝麻球", "糖糕", "油饼", "鸡蛋灌饼", "手抓饼", "千层饼", "烧饼", "糖饼", "葱油饼",
            "豆腐脑", "油茶", "糊辣汤", "牛杂", "猪杂", "驴打滚", "艾窝窝", "热狗"],
    "饮料": ["豆浆", "牛奶", "酸奶", "果汁", "可乐", "雪碧", "奶茶", "咖啡", "绿豆汤", "酸梅汤", "柠檬水",
            "橙汁", "苹果汁", "葡萄汁", "西瓜汁", "芒果汁", "美式咖啡", "拿铁", "卡布奇诺", "摩卡",
            "珍珠奶茶", "红茶拿铁", "绿茶拿铁", "抹茶拿铁"],
    "甜品": ["豆沙包", "八宝粥", "银耳汤", "红枣汤", "蛋糕", "巧克力蛋糕", "芝士蛋糕", "提拉米苏", "冰淇淋",
            "布丁", "焦糖布丁", "双皮奶", "姜撞奶", "杨枝甘露", "红豆沙", "绿豆沙", "芝麻糊", "汤圆", "年糕",
            "糍粑", "粽子", "月饼", "青团", "桂花糕", "马蹄糕", "萝卜糕", "刨冰", "绵绵冰", "芒果冰"],
    
    # 烹饪方式
    "油炸": ["糖醋里脊", "炸鸡", "油条", "春卷", "鱿鱼圈", "炸猪排", "炸鸡排", "天妇罗", "炸虾", "炸豆腐",
            "可乐饼", "锅包肉", "炸藕盒", "炸薯条", "炸鸡块", "炸鱼", "炸洋葱圈", "炸蘑菇"],
    "蒸": ["清蒸鱼", "清蒸螃蟹", "蒸饺", "馒头", "花卷", "清蒸鲈鱼", "清蒸石斑鱼", "蒸扇贝", "粉蒸排骨",
          "小笼包", "蒸包子", "蒸生蚝", "蒸茄子"],
    "炒": ["炒饭", "炒面", "宫保鸡丁", "鱼香肉丝", "西红柿炒鸡蛋", "回锅肉", "青椒肉丝", "木须肉", "小炒肉",
          "爆炒腰花", "爆炒鱿鱼", "葱爆羊肉", "避风塘炒蟹", "炒河粉", "炒乌冬", "泰式炒河粉"],
    "烤": ["北京烤鸭", "烤鸡翅", "烤串", "烤鱼", "烤生蚝", "烤扇贝", "烤鱿鱼", "BBQ", "铁板烧", "韩式烤肉",
          "烤羊排", "烤牛排", "烤香肠", "烤蔬菜", "烤土豆", "烤玉米", "烤茄子", "烤韭菜", "烤面筋", "烤豆腐"],
    "红烧": ["红烧肉", "红烧鱼", "红烧排骨", "红烧豆腐", "红烧茄子", "红烧牛肉", "红烧羊肉", "红烧鸡翅",
            "红烧狮子头", "红烧大肠", "红烧鲤鱼"],
    "清炒": ["清炒时蔬", "清炒菠菜", "清炒芦笋", "清炒油菜", "清炒豆芽"],
    "凉拌": ["凉拌黄瓜", "拍黄瓜", "凉拌木耳", "凉拌海带", "凉拌豆芽", "凉拌三丝", "凉拌菠菜", "凉拌藕片",
            "凉拌芹菜", "凉拌茄子", "凉拌苦瓜", "老醋花生"],
    "煲/炖": ["排骨煲", "牛腩煲", "茄子煲", "老鸭煲", "猪肚鸡", "土豆炖牛肉", "白菜炖粉条", "排骨炖豆角",
             "炖土豆", "苦瓜炖鸡"],
    
    # 餐次
    "早餐": ["豆浆", "油条", "包子", "粥", "煎饼果子", "肉包", "菜包", "豆沙包", "馒头", "花卷", "小米粥",
            "皮蛋瘦肉粥", "鸡蛋灌饼", "手抓饼", "豆腐脑", "油茶", "牛奶", "面包", "三明治", "汉堡"],
    "午餐": ["米饭", "炒饭", "面条", "炒面", "盖浇饭", "煲仔饭", "黄焖鸡米饭", "咖喱饭", "烧腊饭", "卤肉饭"],
    "晚餐": ["米饭", "炒饭", "面条", "火锅", "烤肉", "海鲜", "牛排"],
    "夜宵": ["烧烤", "麻辣烫", "小龙虾", "烤串", "炸鸡", "汉堡", "关东煮", "火锅", "麻辣香锅"],
    
    # 价格区间
    "经济实惠": ["米饭", "炒饭", "面条", "炒面", "馒头", "包子", "饺子", "粥", "豆浆", "油条", "土豆丝", "炒青菜"],
    "中等价位": ["宫保鸡丁", "鱼香肉丝", "红烧肉", "糖醋排骨", "麻婆豆腐", "回锅肉", "可乐鸡翅", "炒河粉"],
    "高档菜品": ["北京烤鸭", "牛排", "龙虾", "鲍鱼", "海参", "佛跳墙", "刺身拼盘", "和牛", "战斧牛排"],
    
    # 特殊标签
    "火锅": ["麻辣火锅", "清汤火锅", "番茄火锅", "菌菇火锅", "三鲜火锅", "酸汤火锅", "椰子鸡火锅", "潮汕牛肉火锅",
            "羊蝎子火锅", "鱼头火锅", "海鲜火锅", "猪肚鸡火锅", "毛肚", "黄喉", "鸭肠", "肥牛", "羊肉卷"],
    "烧烤": ["羊肉串", "牛肉串", "猪肉串", "鸡肉串", "鸡翅串", "鸡腿串", "烤鱼", "烤虾", "烤鱿鱼", "烤生蚝",
            "烤扇贝", "烤蔬菜", "烤茄子", "烤韭菜", "烤金针菇", "烤玉米", "烤面筋", "烤豆腐"],
    "汤类": ["番茄蛋汤", "紫菜蛋汤", "酸辣汤", "玉米排骨汤", "冬瓜排骨汤", "莲藕排骨汤", "鸡汤", "老鸭汤",
            "牛肉汤", "羊肉汤", "鱼汤", "豆腐汤", "西湖牛肉羹", "三鲜汤", "冬阴功汤", "奶油蘑菇汤", "罗宋汤"],
}

# 常见菜品列表 (扩充至近1000个)
DISH_NAMES = [
    # 中式主食类 (60个)
    "米饭", "炒饭", "蛋炒饭", "扬州炒饭", "酱油炒饭", "菠萝炒饭", "虾仁炒饭", "叉烧炒饭", "福建炒饭", "泰式炒饭",
    "面条", "炒面", "拉面", "刀削面", "牛肉面", "鸡丝凉面", "担担面", "炸酱面", "热干面", "臊子面", "油泼面", "阳春面", "葱油拌面", "炒刀削面",
    "馒头", "花卷", "包子", "肉包", "菜包", "豆沙包", "叉烧包", "流沙包", "奶黄包", "小笼包",
    "饺子", "水饺", "煎饺", "蒸饺", "馄饨", "云吞", "抄手", "锅贴", "煎包", "生煎包",
    "粥", "白粥", "皮蛋瘦肉粥", "海鲜粥", "八宝粥", "小米粥", "南瓜粥", "红豆粥", "绿豆粥",
    "粉", "米粉", "桂林米粉", "螺蛳粉", "酸辣粉", "过桥米线", "重庆小面", "肠粉", "河粉", "炒河粉",
    
    # 中式肉类菜品 (120个)
    "红烧肉", "梅菜扣肉", "东坡肉", "回锅肉", "京酱肉丝", "鱼香肉丝", "青椒肉丝", "蒜苗肉丝", "木须肉", "小炒肉",
    "糖醋里脊", "糖醋排骨", "红烧排骨", "蒜香排骨", "椒盐排骨", "豉汁排骨", "粉蒸排骨", "排骨炖豆角", "排骨煲", "酱排骨",
    "宫保鸡丁", "辣子鸡丁", "口水鸡", "白切鸡", "叫花鸡", "大盘鸡", "三杯鸡", "盐焗鸡", "手撕鸡", "汽锅鸡",
    "可乐鸡翅", "红烧鸡翅", "烤鸡翅", "盐焗鸡翅", "香辣鸡翅", "蒜香鸡翅", "奥尔良鸡翅", "柠檬鸡翅", "蜜汁鸡翅", "茄汁鸡翅",
    "北京烤鸭", "盐水鸭", "啤酒鸭", "酱板鸭", "香酥鸭", "老鸭煲", "鸭血粉丝汤", "烤鸭", "板栗鸭", "冬瓜鸭",
    "红烧牛肉", "黑椒牛柳", "孜然牛肉", "小炒黄牛肉", "水煮牛肉", "牛腩煲", "番茄牛腩", "土豆炖牛肉", "咖喱牛肉", "干锅牛肉",
    "红烧羊肉", "孜然羊肉", "葱爆羊肉", "手抓羊肉", "羊肉串", "羊肉泡馍", "羊肉汤", "羊肉火锅", "烤羊排", "羊蝎子",
    "红烧狮子头", "四喜丸子", "珍珠丸子", "糯米丸子", "炸肉丸", "萝卜丸子", "豆腐丸子", "清蒸肉丸",
    "酱牛肉", "卤牛肉", "五香牛肉", "牛肉干", "牛肉粒", "铁板牛肉", "滑蛋牛肉", "芦笋牛柳",
    "红烧猪蹄", "卤猪蹄", "酱猪蹄", "花生猪蹄", "黄豆猪蹄", "莲藕猪蹄", "海带猪蹄", "木瓜猪蹄",
    "叉烧", "蜜汁叉烧", "脆皮叉烧", "叉烧肉", "烧鸭", "烧鹅", "烧鸡", "烧排骨", "烧五花肉", "脆皮烤肉",
    "锅包肉", "溜肉段", "熘肝尖", "爆炒腰花", "熘三样", "九转大肠", "红烧大肠", "卤煮", "爆肚", "炒肝",
    
    # 中式海鲜类 (80个)
    "红烧鱼", "清蒸鱼", "糖醋鱼", "酸菜鱼", "水煮鱼", "剁椒鱼头", "松鼠鳜鱼", "西湖醋鱼", "豆瓣鱼", "烤鱼",
    "红烧大虾", "油焖大虾", "白灼虾", "盐水虾", "椒盐虾", "蒜蓉虾", "油爆虾", "龙井虾仁", "宫保虾球", "凤尾虾",
    "蒜蓉扇贝", "粉丝扇贝", "烤扇贝", "蒸扇贝", "芝士焗扇贝", "蒜蓉粉丝蒸扇贝",
    "清蒸螃蟹", "香辣蟹", "咖喱蟹", "避风塘炒蟹", "葱姜炒蟹", "年糕炒蟹", "蟹黄豆腐", "蟹粉小笼",
    "鱿鱼圈", "铁板鱿鱼", "干锅鱿鱼", "爆炒鱿鱼", "香辣鱿鱼", "椒盐鱿鱼", "烤鱿鱼", "水煮鱿鱼",
    "清蒸鲈鱼", "红烧鲤鱼", "糖醋黄花鱼", "椒盐多宝鱼", "清蒸石斑鱼", "剁椒鱼头", "麻辣鱼片", "酸汤鱼",
    "海鲜烩", "海鲜粥", "海鲜炒饭", "海鲜豆腐煲", "海鲜火锅", "海鲜汤", "海鲜面", "海鲜意面",
    "蒜蓉生蚝", "烤生蚝", "炭烧生蚝", "芝士焗生蚝", "蒸生蚝", "生蚝煲", "生蚝炒蛋", "生蚝粥",
    "花甲", "爆炒花甲", "蒜蓉花甲", "辣炒花甲", "花甲粉", "花甲米线", "酒蒸蛤蜊", "姜葱炒蛏子",
    "海带汤", "海带炖排骨", "凉拌海带丝", "海带豆腐汤", "紫菜蛋汤", "紫菜包饭", "海苔卷", "裙带菜汤",
    
    # 中式蔬菜豆腐类 (100个)
    "麻婆豆腐", "家常豆腐", "红烧豆腐", "锅塌豆腐", "皮蛋豆腐", "小葱拌豆腐", "日本豆腐", "客家酿豆腐", "煎豆腐", "炸豆腐",
    "清炒时蔬", "蒜蓉油菜", "上汤娃娃菜", "炝炒圆白菜", "干锅包菜", "醋溜白菜", "白菜炖粉条", "白菜豆腐汤",
    "鱼香茄子", "红烧茄子", "肉末茄子", "蒜泥茄子", "油焖茄子", "烧茄子", "蒸茄子", "凉拌茄子", "酱焖茄子", "茄子煲",
    "西红柿炒鸡蛋", "黄瓜炒鸡蛋", "木耳炒鸡蛋", "韭菜炒鸡蛋", "青椒炒鸡蛋", "洋葱炒鸡蛋", "苦瓜炒鸡蛋", "丝瓜炒鸡蛋",
    "地三鲜", "醋溜土豆丝", "酸辣土豆丝", "干锅土豆片", "炸土豆条", "土豆泥", "土豆饼", "炖土豆", "孜然土豆", "狼牙土豆",
    "蒜蓉西兰花", "干锅花菜", "手撕包菜", "虎皮尖椒", "青椒土豆丝", "尖椒干豆腐", "炒青椒", "酿青椒",
    "凉拌黄瓜", "拍黄瓜", "老醋花生", "凉拌木耳", "凉拌海带", "凉拌豆芽", "凉拌三丝", "凉拌菠菜",
    "蒜蓉生菜", "蚝油生菜", "清炒菠菜", "蒜蓉菠菜", "奶油菠菜", "菠菜豆腐汤", "菠菜蛋汤", "菠菜粥",
    "酸辣藕片", "糖醋藕片", "炸藕盒", "藕饼", "桂花糯米藕", "莲藕排骨汤", "凉拌藕片", "炒藕丁",
    "蒜蓉油麦菜", "清炒芦笋", "芦笋炒虾仁", "芦笋培根", "芦笋沙拉", "白灼芥兰", "蚝油芥兰", "秋葵炒蛋",
    "炒豆芽", "豆芽炒粉", "韭菜炒豆芽", "银芽炒肉", "豆芽汤", "凉拌豆芽", "豆芽拌菠菜", "豆芽炒韭菜",
    "炒芹菜", "芹菜炒肉", "芹菜炒香干", "芹菜炒鱿鱼", "芹菜花生", "凉拌芹菜", "芹菜汁", "芹菜粥",
    "炒苦瓜", "苦瓜炒肉", "凉拌苦瓜", "苦瓜煎蛋", "苦瓜汁", "酿苦瓜", "苦瓜排骨汤", "苦瓜炖鸡",
    
    # 中式汤类 (40个)
    "番茄蛋汤", "紫菜蛋汤", "酸辣汤", "玉米排骨汤", "冬瓜排骨汤", "莲藕排骨汤", "山药排骨汤", "海带排骨汤",
    "鸡汤", "老鸭汤", "牛肉汤", "羊肉汤", "排骨汤", "猪蹄汤", "鱼汤", "豆腐汤",
    "西湖牛肉羹", "三鲜汤", "酸菜汤", "白菜豆腐汤", "丝瓜汤", "黄瓜汤", "冬瓜汤", "南瓜汤",
    "银耳莲子汤", "木瓜雪耳汤", "绿豆汤", "红豆汤", "花生汤", "莲子汤", "百合汤", "雪梨汤",
    "鱼头豆腐汤", "鲫鱼汤", "鲢鱼汤", "鳝鱼汤", "泥鳅汤", "黄骨鱼汤", "鱼丸汤", "鱼片汤",
    
    # 中式小吃饮料 (60个)
    "煎饼果子", "肉夹馍", "生煎包", "锅贴", "春卷", "油条", "麻团", "芝麻球", "糖糕", "油饼",
    "麻辣烫", "关东煮", "烤串", "炸鸡", "汉堡", "三明治", "热狗", "披萨", "可丽饼", "华夫饼",
    "豆浆", "牛奶", "酸奶", "果汁", "可乐", "雪碧", "奶茶", "咖啡", "柠檬水", "酸梅汤",
    "绿豆汤", "银耳汤", "红枣汤", "莲子羹", "杏仁茶", "豆花", "龟苓膏", "烧仙草", "凉粉", "凉皮",
    "鸡蛋灌饼", "手抓饼", "千层饼", "烧饼", "糖饼", "葱油饼", "馅饼", "盒子", "驴打滚", "艾窝窝",
    "豆腐脑", "油茶", "糊辣汤", "羊汤", "牛杂", "猪杂", "鸭血粉丝", "牛肉粉", "肥肠粉", "担担面",
    
    # 盖浇饭/套餐 (40个)
    "黄焖鸡米饭", "香菇滑鸡饭", "咖喱牛肉饭", "咖喱鸡肉饭", "番茄牛腩饭", "红烧牛肉饭", "梅菜扣肉饭", "木须肉饭",
    "麻辣香锅", "石锅拌饭", "煲仔饭", "盖浇饭", "烧腊饭", "卤肉饭", "牛肉盖浇饭", "鸡排饭",
    "猪排饭", "炸鸡饭", "烤肉饭", "铁板饭", "蛋包饭", "炒饭套餐", "面条套餐", "水饺套餐",
    "鱼香肉丝饭", "宫保鸡丁饭", "麻婆豆腐饭", "回锅肉饭", "青椒肉丝饭", "鱼香茄子饭", "地三鲜饭", "酸辣土豆丝饭",
    "双拼饭", "三拼饭", "四宝饭", "五福饭", "六合饭", "七彩饭", "八珍饭", "九转饭",
    
    # 日韩料理 (80个)
    "寿司", "三文鱼寿司", "金枪鱼寿司", "鳗鱼寿司", "虾寿司", "蟹籽寿司", "玉子烧寿司", "加州卷", "手卷", "军舰寿司",
    "刺身", "三文鱼刺身", "金枪鱼刺身", "八爪鱼刺身", "北极贝刺身", "甜虾刺身", "鱿鱼刺身", "扇贝刺身",
    "天妇罗", "炸虾天妇罗", "炸蔬菜天妇罗", "炸鱿鱼圈", "炸猪排", "炸鸡排", "可乐饼", "炸豆腐",
    "拉面", "日式拉面", "豚骨拉面", "味增拉面", "酱油拉面", "盐味拉面", "担担拉面", "冷面",
    "乌冬面", "炒乌冬", "汤乌冬", "天妇罗乌冬", "咖喱乌冬", "炸酱乌冬", "海鲜乌冬", "牛肉乌冬",
    "荞麦面", "冷荞麦面", "热荞麦面", "鸭肉荞麦面", "天妇罗荞麦面", "月见荞麦面",
    "饭团", "三角饭团", "鲑鱼饭团", "梅子饭团", "金枪鱼饭团", "炸虾饭团", "海苔饭团", "烤肉饭团",
    "铁板烧", "牛肉铁板烧", "鸡肉铁板烧", "海鲜铁板烧", "什锦铁板烧", "铁板炒面", "铁板炒饭",
    "韩式烤肉", "牛五花", "猪五花", "烤牛舌", "烤鸡腿", "烤猪排", "韩式拌饭", "石锅拌饭",
    "泡菜", "韩式泡菜", "泡菜汤", "泡菜炒饭", "泡菜煎饼", "海鲜煎饼", "土豆饼", "南瓜饼",
    
    # 西餐 (100个)
    "牛排", "菲力牛排", "西冷牛排", "肋眼牛排", "T骨牛排", "战斧牛排", "牛排套餐", "黑椒牛排", "红酒牛排", "蒜香牛排",
    "猪排", "炸猪排", "烤猪排", "猪排套餐", "蜜汁猪排", "BBQ猪排", "柠檬猪排", "香草猪排",
    "鸡排", "炸鸡排", "烤鸡排", "照烧鸡排", "奥尔良鸡排", "柠檬鸡排", "香草鸡排", "黑椒鸡排",
    "意大利面", "番茄肉酱意面", "奶油培根意面", "海鲜意面", "青酱意面", "蒜香意面", "黑椒牛柳意面", "奶油蘑菇意面", "千层面",
    "披萨", "玛格丽特披萨", "夏威夷披萨", "海鲜披萨", "培根披萨", "香肠披萨", "蔬菜披萨", "芝士披萨", "四季披萨",
    "汉堡", "牛肉汉堡", "鸡肉汉堡", "猪肉汉堡", "鱼肉汉堡", "素食汉堡", "双层汉堡", "芝士汉堡", "培根汉堡",
    "三明治", "火腿三明治", "鸡蛋三明治", "金枪鱼三明治", "培根三明治", "烤鸡三明治", "BLT三明治", "俱乐部三明治", "热狗",
    "沙拉", "凯撒沙拉", "水果沙拉", "蔬菜沙拉", "鸡肉沙拉", "金枪鱼沙拉", "土豆沙拉", "意面沙拉", "希腊沙拉",
    "汤", "奶油蘑菇汤", "南瓜汤", "玉米浓汤", "海鲜汤", "洋葱汤", "番茄汤", "西班牙海鲜汤", "罗宋汤",
    "烤肉", "烤鸡腿", "烤鸡翅", "烤羊排", "烤牛排", "烤香肠", "烤蔬菜", "烤土豆", "烤玉米",
    "炸物", "炸薯条", "炸鸡块", "炸鱼", "炸虾", "炸洋葱圈", "炸鱿鱼圈", "炸蘑菇", "炸芝士条",
    "焗饭", "芝士焗饭", "奶油焗饭", "海鲜焗饭", "鸡肉焗饭", "牛肉焗饭", "蔬菜焗饭", "培根焗饭", "意式焗饭",
    "千层饼", "肉酱千层饼", "芝士千层饼", "蔬菜千层饼", "海鲜千层饼",
    
    # 东南亚料理 (60个)
    "咖喱", "咖喱鸡", "咖喱牛肉", "咖喱羊肉", "咖喱虾", "咖喱蔬菜", "咖喱土豆", "咖喱饭", "咖喱面", "绿咖喱",
    "泰式炒河粉", "泰式炒面", "泰式春卷", "泰式炸春卷", "泰式沙拉", "泰式烤鸡", "泰式烤肉", "泰式海鲜",
    "冬阴功汤", "椰汁咖喱", "椰汁鸡", "椰汁虾", "椰汁饭", "椰汁糕", "芒果糯米饭", "榴莲糯米饭",
    "越南春卷", "越南米粉", "越南河粉", "越南法棍", "越南咖啡", "越南炸春卷", "越南烤肉", "越南炒面",
    "印尼炒饭", "印尼炒面", "印尼沙爹", "印尼烤鸡", "印尼咖喱", "印尼煎饼", "印尼汤面", "印尼春卷",
    "马来西亚炒粿条", "马来西亚叻沙", "马来西亚椰浆饭", "马来西亚肉骨茶", "马来西亚煎饼", "马来西亚咖喱",
    "新加坡炒面", "新加坡海南鸡饭", "新加坡肉骨茶", "新加坡叻沙", "新加坡炒粿条", "新加坡咖喱",
    "菲律宾烤乳猪", "菲律宾炖肉", "菲律宾春卷", "菲律宾炒面",
    
    # 甜品饮品 (80个)
    "蛋糕", "巧克力蛋糕", "芝士蛋糕", "提拉米苏", "黑森林蛋糕", "慕斯蛋糕", "水果蛋糕", "奶油蛋糕", "海绵蛋糕", "戚风蛋糕",
    "冰淇淋", "香草冰淇淋", "巧克力冰淇淋", "草莓冰淇淋", "抹茶冰淇淋", "芒果冰淇淋", "香蕉冰淇淋", "蓝莓冰淇淋", "薄荷冰淇淋",
    "布丁", "焦糖布丁", "巧克力布丁", "芒果布丁", "椰奶布丁", "鸡蛋布丁", "牛奶布丁", "水果布丁", "抹茶布丁",
    "奶茶", "珍珠奶茶", "红茶拿铁", "绿茶拿铁", "抹茶拿铁", "乌龙奶茶", "港式奶茶", "泰式奶茶", "阿萨姆奶茶",
    "咖啡", "美式咖啡", "拿铁", "卡布奇诺", "摩卡", "焦糖玛奇朵", "白咖啡", "冰咖啡", "越南咖啡",
    "果汁", "橙汁", "苹果汁", "葡萄汁", "西瓜汁", "芒果汁", "菠萝汁", "柠檬汁", "猕猴桃汁", "火龙果汁",
    "奶昔", "草莓奶昔", "香蕉奶昔", "巧克力奶昔", "芒果奶昔", "蓝莓奶昔", "牛油果奶昔", "奥利奥奶昔",
    "甜点", "双皮奶", "姜撞奶", "杨枝甘露", "红豆沙", "绿豆沙", "芝麻糊", "核桃糊", "花生糊",
    "冰品", "刨冰", "绵绵冰", "雪花冰", "芒果冰", "草莓冰", "红豆冰", "绿豆冰", "仙草冰",
    "中式甜品", "汤圆", "年糕", "糍粑", "粽子", "月饼", "青团", "桂花糕", "马蹄糕", "萝卜糕",
    
    # 烧烤烤肉 (50个)
    "羊肉串", "牛肉串", "猪肉串", "鸡肉串", "鸡心串", "鸡胗串", "鸡翅串", "鸡腿串", "五花肉串", "里脊肉串",
    "烤鱼", "烤虾", "烤鱿鱼", "烤生蚝", "烤扇贝", "烤海螺", "烤蛤蜊", "烤青口", "烤龙虾", "烤螃蟹",
    "烤蔬菜", "烤茄子", "烤韭菜", "烤金针菇", "烤香菇", "烤玉米", "烤土豆", "烤红薯", "烤南瓜", "烤辣椒",
    "烤面筋", "烤豆腐", "烤年糕", "烤馒头", "烤花卷", "烤饼", "烤包子", "烤饺子",
    "烤鸡爪", "烤猪蹄", "烤羊排", "烤牛排", "烤培根", "烤香肠", "烤火腿", "烤肉丸", "烤鱼丸", "烤虾丸",
    "烤冷面", "烤冰激凌",
    
    # 火锅类 (40个)
    "麻辣火锅", "清汤火锅", "番茄火锅", "菌菇火锅", "三鲜火锅", "酸汤火锅", "椰子鸡火锅", "潮汕牛肉火锅",
    "羊蝎子火锅", "鱼头火锅", "鱼片火锅", "海鲜火锅", "猪肚鸡火锅", "鸡汤火锅", "排骨火锅", "牛肉火锅",
    "毛肚", "黄喉", "鸭肠", "郡肝", "鹅肠", "牛百叶", "猪脑花", "嫩牛肉", "肥牛", "羊肉卷",
    "虾滑", "鱼滑", "鱼丸", "牛肉丸", "撒尿牛丸", "墨鱼丸", "蟹棒", "鱼豆腐", "豆腐泡", "冻豆腐",
    "金针菇", "平菇", "香菇", "木耳", "海带", "土豆片", "莲藕片", "冬瓜", "白萝卜", "娃娃菜",
]


class DatabasePopulator:
    """数据库填充器"""
    
    def __init__(self, clear_mode=False):
        self.clear_mode = clear_mode
        self.deepseek_client = None
        self.driver = None
        self.media_root = BASE_DIR / 'media' / 'dishes'
        self.media_root.mkdir(parents=True, exist_ok=True)
        
        # 初始化 DeepSeek 客户端
        if DEEPSEEK_API_KEY:
            self.deepseek_client = OpenAI(
                api_key=DEEPSEEK_API_KEY,
                base_url=DEEPSEEK_BASE_URL
            )
            print("✓ DeepSeek API 已初始化")
        else:
            print("⚠ 警告: DEEPSEEK_API_KEY 未设置，将跳过菜品描述生成")
    
    def init_selenium(self):
        """初始化 Selenium WebDriver"""
        if self.driver:
            return
        
        print("正在初始化 Selenium WebDriver...")
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            print("✓ Selenium WebDriver 初始化成功")
        except Exception as e:
            print(f"⚠ 警告: Selenium 初始化失败: {e}")
            print("将使用Unsplash和占位图片")
    
    def cleanup_selenium(self):
        """清理 Selenium 资源"""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def clear_data(self):
        """清空除食堂以外的所有数据"""
        print("\n开始清空数据...")
        
        # 清空菜品
        dish_count = Dish.objects.count()
        Dish.objects.all().delete()
        print(f"✓ 已删除 {dish_count} 个菜品")
        
        # 清空窗口
        window_count = Window.objects.count()
        Window.objects.all().delete()
        print(f"✓ 已删除 {window_count} 个窗口")
        
        # 清空楼层
        floor_count = Floor.objects.count()
        Floor.objects.all().delete()
        print(f"✓ 已删除 {floor_count} 个楼层")
        
        # 清空标签
        tag_count = Tag.objects.count()
        Tag.objects.all().delete()
        print(f"✓ 已删除 {tag_count} 个标签")
        
        print("数据清空完成！\n")
    
    def create_tags(self):
        """创建标签(基础标签 + Pending标签)"""
        print("\n创建标签...")
        created_tags = []
        
        # 创建基础标签
        for tag_name in BASE_TAG_NAMES:
            tag, created = Tag.objects.get_or_create(name=tag_name)
            if created:
                created_tags.append(tag)
        
        # 创建pending标签
        for tag_name in PENDING_TAG_NAMES:
            tag, created = Tag.objects.get_or_create(name=tag_name)
            if created:
                created_tags.append(tag)
        
        print(f"✓ 已创建 {len(created_tags)} 个标签(总计 {Tag.objects.count()} 个)")
        print(f"  - 基础标签: {len(BASE_TAG_NAMES)} 个")
        print(f"  - Pending标签: {len(PENDING_TAG_NAMES)} 个")
        return Tag.objects.all()
    
    def get_tags_for_dish(self, dish_name):
        """为菜品获取合适的基础标签(tags) - 只返回BASE_TAG_NAMES中的标签"""
        tags = []
        
        # 根据映射关系添加标签,但必须在 BASE_TAG_NAMES 中
        for tag_name, dish_list in DISH_TAG_MAPPING.items():
            if dish_name in dish_list and tag_name in BASE_TAG_NAMES:
                try:
                    tag = Tag.objects.get(name=tag_name)
                    tags.append(tag)
                except Tag.DoesNotExist:
                    pass
        
        return tags
    
    def get_pending_tags_for_dish(self, dish_name):
        """为菜品获取pending标签(模拟用户提交) - 只返回PENDING_TAG_NAMES中的标签"""
        pending_tags = []
        
        # 随机从 PENDING_TAG_NAMES 标签中选择 1-3 个,确保不与BASE_TAG_NAMES重复
        available_pending = list(Tag.objects.filter(name__in=PENDING_TAG_NAMES))
        if available_pending:
            count = random.randint(1, min(3, len(available_pending)))
            pending_tags = random.sample(available_pending, count)
        
        return pending_tags
    
    def create_floors_and_windows(self, canteen):
        """为食堂创建楼层和窗口"""
        floor_count = random.randint(1, 3)  # 1-3层
        floors = []
        
        for i in range(floor_count):
            floor = Floor.objects.create(
                name=f"{i+1}楼",
                canteen=canteen,
                order=i
            )
            floors.append(floor)
            
            # 每层创建随机数量的窗口
            window_count = random.randint(3, 10)  # 3-10个窗口
            for j in range(window_count):
                Window.objects.create(
                    name=f"{j+1}号窗口",
                    floor=floor,
                    order=j
                )
        
        return floors
    
    def get_dish_description(self, dish_name):
        """使用 DeepSeek API 生成菜品描述"""
        if not self.deepseek_client:
            return f"{dish_name}，美味可口，营养丰富，是食堂的特色菜品之一。采用新鲜食材精心烹制，色香味俱全，深受广大师生喜爱。"
        
        try:
            response = self.deepseek_client.chat.completions.create(
                model="deepseek-reasoner",
                messages=[
                    {"role": "system", "content": "你是一个专业的美食文案编辑，擅长撰写简洁、吸引人的菜品描述。"},
                    {"role": "user", "content": f"请为菜品「{dish_name}」撰写一段60-100字的描述，要求：1）突出菜品特色和口感；2）描述食材和烹饪方法；3）语言生动诱人。直接输出描述内容，不要有其他多余的话。"}
                ],
                stream=False,
                temperature=0.8
            )
            description = response.choices[0].message.content.strip()
            # 移除可能的引号
            description = description.strip('"').strip('"').strip("'")
            return description
        except Exception as e:
            print(f"  ⚠ DeepSeek API 调用失败: {e}")
            return f"{dish_name}，美味可口，营养丰富，是食堂的特色菜品之一。采用新鲜食材精心烹制，色香味俱全，深受广大师生喜爱。"
    
    def download_dish_image(self, dish_name):
        """使用多种方法下载菜品图片"""
        filename = f"{dish_name}.jpg"
        filepath = self.media_root / filename
        
        # 方法1: 百度图片API (最稳定)
        try:
            print("  尝试百度图片API...")
            session = requests.Session()
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Referer": "https://image.baidu.com/",
                "X-Requested-With": "XMLHttpRequest",
                "X-Forwarded-For": f"1.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}",
            }
            
            session.get("https://image.baidu.com", headers=headers, timeout=5)
            
            url = "https://image.baidu.com/search/acjson"
            params = {
                "tn": "resultjson_com",
                "ipn": "rj",
                "ct": "201326592",
                "cl": "2",
                "lm": "-1",
                "word": dish_name,
                "queryWord": dish_name,
                "pn": "0",
                "rn": "30",
            }
            
            resp = session.get(url, params=params, headers=headers, timeout=10)
            data = resp.json()
            
            if "data" in data:
                for item in data.get("data", []):
                    if isinstance(item, dict) and "thumbURL" in item:
                        img_url = item["thumbURL"]
                        try:
                            img_content = session.get(img_url, timeout=10).content
                            if len(img_content) > 5000:
                                with open(filepath, "wb") as f:
                                    f.write(img_content)
                                print(f"  ✓ 图片已下载 (百度API): {filename}")
                                return f"dishes/{filename}"
                        except Exception:
                            continue
        except Exception as e:
            print(f"  ⚠ 百度API下载失败: {e}")
        
        # 方法2: 必应图片 (使用Selenium)
        if self.driver:
            try:
                print("  尝试必应图片...")
                encoded_keyword = urllib.parse.quote(dish_name)
                url = f"https://www.bing.com/images/search?q={encoded_keyword}&qft=+filterui:imagesize-large"
                
                self.driver.get(url)
                time.sleep(3)
                
                img_element = self.driver.find_element(By.CSS_SELECTOR, '.mimg')
                img_url = img_element.get_attribute('src')
                
                if img_url:
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                        'Referer': 'https://www.bing.com/'
                    }
                    img_response = requests.get(img_url, headers=headers, timeout=10)
                    
                    if img_response.status_code == 200 and len(img_response.content) > 5000:
                        with open(filepath, 'wb') as f:
                            f.write(img_response.content)
                        print(f"  ✓ 图片已下载 (必应): {filename}")
                        return f"dishes/{filename}"
            except Exception as e:
                print(f"  ⚠ 必应下载失败: {e}")
        
        # 方法3: Unsplash API
        try:
            print("  尝试 Unsplash API...")
            keywords_map = {
                "红烧肉": "braised pork",
                "宫保鸡丁": "kung pao chicken",
                "麻婆豆腐": "mapo tofu",
                "西红柿炒鸡蛋": "tomato egg",
                "糖醋里脊": "sweet sour pork",
                "可乐鸡翅": "cola chicken wings",
                "清蒸鱼": "steamed fish",
                "炒饭": "fried rice",
                "牛肉面": "beef noodles",
                "小笼包": "xiaolongbao",
            }
            
            keyword = keywords_map.get(dish_name, "chinese food")
            unsplash_url = f"https://source.unsplash.com/800x600/?{keyword},food,dish"
            
            response = requests.get(unsplash_url, timeout=15, allow_redirects=True, verify=False)
            
            if response.status_code == 200 and len(response.content) > 10000:
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                print(f"  ✓ 图片已下载 (Unsplash): {filename}")
                return f"dishes/{filename}"
        except Exception as e:
            print(f"  ⚠ Unsplash下载失败: {e}")
        
        # 方法4: 占位图片服务（最后备选）
        try:
            print("  使用占位图片...")
            placeholder_url = f"https://via.placeholder.com/800x600/FF6B6B/FFFFFF?text={urllib.parse.quote(dish_name)}"
            response = requests.get(placeholder_url, timeout=10)
            
            if response.status_code == 200:
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                print(f"  ✓ 占位图片已生成: {filename}")
                return f"dishes/{filename}"
        except Exception as e:
            print(f"  ⚠ 占位图片生成失败: {e}")
        
        print(f"  ✗ 所有方法均失败: {dish_name}")
        return None
    
    def create_dishes_for_canteen(self, canteen, dish_count=100):
        """为食堂创建菜品"""
        windows = Window.objects.filter(floor__canteen=canteen)
        if not windows.exists():
            print(f"  ⚠ 食堂 {canteen.name} 没有窗口，跳过")
            return 0
        
        created_count = 0
        available_dishes = DISH_NAMES.copy()
        random.shuffle(available_dishes)
        
        for i in range(min(dish_count, len(available_dishes))):
            dish_name = available_dishes[i]
            
            # 随机选择窗口
            window = random.choice(windows)
            
            # 生成随机价格
            price = Decimal(random.uniform(5.0, 30.0)).quantize(Decimal('0.01'))
            
            # 生成描述
            print(f"  正在生成描述: {dish_name}...")
            description = self.get_dish_description(dish_name)
            time.sleep(0.5)  # 避免 API 调用过快
            
            # 下载图片
            print(f"  正在下载图片: {dish_name}...")
            image_path = self.download_dish_image(dish_name)
            
            # 创建菜品
            dish = Dish.objects.create(
                name=dish_name,
                description=description,
                price=price,
                canteen=canteen,
                window=window,
                image=image_path,
                rating=Decimal(random.uniform(3.5, 5.0)).quantize(Decimal('0.01')),
                view_count=random.randint(0, 10000)  # 随机初始化浏览量
            )
            
            # 为菜品添加基础标签(tags) - 确保只来自BASE_TAG_NAMES
            tags = self.get_tags_for_dish(dish_name)
            if tags:
                dish.tags.set(tags)
            
            # 为菜品添加pending标签(模拟用户提交) - 确保只来自PENDING_TAG_NAMES
            pending_tags = self.get_pending_tags_for_dish(dish_name)
            if pending_tags:
                dish.pending_tags.set(pending_tags)
            
            created_count += 1
            tag_names = [tag.name for tag in tags]
            pending_tag_names = [tag.name for tag in pending_tags]
            print(f"  ✓ 已创建菜品 ({created_count}/{dish_count}): {dish_name} - ¥{price}")
            print(f"    标签: {', '.join(tag_names) if tag_names else '无'} | Pending: {', '.join(pending_tag_names) if pending_tag_names else '无'}")
        
        return created_count
    
    def populate(self):
        """执行填充"""
        print("\n" + "="*60)
        print("数据库填充脚本")
        print("="*60)
        
        # 清空模式
        if self.clear_mode:
            self.clear_data()
            print("清空完成，退出程序")
            return
        
        # 检查食堂
        canteens = Canteen.objects.all()
        if not canteens.exists():
            print("错误: 数据库中没有食堂数据，请先创建食堂")
            return
        
        print(f"\n找到 {canteens.count()} 个食堂")
        
        # 创建标签
        self.create_tags()
        
        # 初始化 Selenium
        self.init_selenium()
        
        total_dishes = 0
        target_total = 1000
        dishes_per_canteen = target_total // canteens.count()
        
        try:
            for idx, canteen in enumerate(canteens, 1):
                print(f"\n[{idx}/{canteens.count()}] 正在处理食堂: {canteen.name}")
                print("-" * 60)
                
                # 创建楼层和窗口
                print("创建楼层和窗口...")
                floors = self.create_floors_and_windows(canteen)
                floor_count = len(floors)
                window_count = Window.objects.filter(floor__canteen=canteen).count()
                print(f"✓ 已创建 {floor_count} 个楼层，{window_count} 个窗口")
                
                # 创建菜品
                print(f"开始创建约 {dishes_per_canteen} 个菜品...")
                created = self.create_dishes_for_canteen(canteen, dishes_per_canteen)
                total_dishes += created
                print(f"✓ 食堂 {canteen.name} 完成，共创建 {created} 个菜品")
        
        finally:
            # 清理 Selenium
            self.cleanup_selenium()
        
        print("\n" + "="*60)
        print(f"填充完成！共创建 {total_dishes} 个菜品")
        print("="*60 + "\n")


def main():
    parser = argparse.ArgumentParser(description='数据库填充脚本')
    parser.add_argument(
        '--clear',
        action='store_true',
        help='清空除食堂以外的所有数据（楼层、窗口、菜品、标签）'
    )
    
    args = parser.parse_args()
    
    populator = DatabasePopulator(clear_mode=args.clear)
    populator.populate()


if __name__ == '__main__':
    main()
