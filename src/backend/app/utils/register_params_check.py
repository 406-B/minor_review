# -*- coding: utf-8 -*-
import re


def register_params_check(content: dict):
    # 用户名：5-12 位，以字母开头且包含数字
    if not 5 <= len(content["username"]) <= 12 or not re.match(
        r"^[a-zA-Z]+[0-9]+$", content["username"]
    ):
        return "username", False

    # 密码：8-15 位，需包含大小写/数字/特殊字符 -_*^
    password = content["password"]
    if not 8 <= len(password) <= 15:
        return "password", False
    has_upper = bool(re.search(r"[A-Z]", password))
    has_lower = bool(re.search(r"[a-z]", password))
    has_digit = bool(re.search(r"[0-9]", password))
    has_punct = bool(re.search(r"[-_*^]", password))
    if not re.match(r"^[a-zA-Z0-9\-_*^]+$", password):
        return "password", False
    if not (has_upper and has_lower and has_digit and has_punct):
        return "password", False

    # 昵称必填
    if not content.get("nickname"):
        return "nickname", False

    # 确认密码验证
    if content.get("confirm_password") != content.get("password"):
        return "confirm_password", False

    return "ok", True

