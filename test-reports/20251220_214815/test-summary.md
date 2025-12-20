# 测试报告摘要

**生成时间**: Sat Dec 20 21:48:29 CST 2025

## 后端测试结果

```
login/tests/test_authentication.py::UserInfoTest::test_get_user_info_by_nonexistent_id PASSED [ 88%]
login/tests/test_authentication.py::UserInfoTest::test_get_user_info_with_invalid_jwt PASSED [ 90%]
login/tests/test_authentication.py::UserInfoTest::test_login_empty_credentials PASSED [ 92%]
login/tests/test_authentication.py::UserInfoTest::test_logout_without_auth PASSED [ 93%]
login/tests/test_authentication.py::UserInfoTest::test_register_invalid_password_format PASSED [ 95%]
login/tests/test_authentication.py::UserInfoTest::test_register_invalid_username_format PASSED [ 96%]
login/tests/test_authentication.py::UserInfoTest::test_register_missing_nickname PASSED [ 98%]
login/tests/test_authentication.py::UserInfoTest::test_register_missing_username PASSED [100%]
================================ tests coverage ================================
_______________ coverage: platform linux, python 3.11.14-final-0 _______________
TOTAL                             1966   1241  36.88%
Coverage HTML written to dir /reports/backend-coverage-html
Coverage XML written to file /reports/backend-coverage.xml
============================== 63 passed in 4.42s ==============================
```

## 前端测试结果

```
无法读取前端测试结果
```

## 覆盖率报告位置

- 后端 HTML 覆盖率报告: `backend-coverage-html/index.html`
- 后端 XML 覆盖率报告: `backend-coverage.xml`
- 前端覆盖率报告: `frontend-coverage/index.html`

## 详细测试结果

- 后端测试详细结果: `backend-test-results.txt`
- 前端测试详细结果: `frontend-test-results.txt`
