# 测试报告摘要

**生成时间**: Sat Dec 20 22:05:18 CST 2025
**报告目录**: test-reports/20251220_220503

## 后端测试结果

### 测试统计
============================== 63 passed in 4.41s ==============================

### 代码覆盖率
TOTAL                             1966   1241  36.88%

### 详细结果
```
canteen/services.py                423    402   4.96%
canteen/tests.py                     0      0 100.00%
canteen/urls.py                      3      0 100.00%
canteen/views.py                   110     69  37.27%
list/__init__.py                     0      0 100.00%
list/admin.py                       92     22  76.09%
list/apps.py                         4      0 100.00%
list/models.py                     145     25  82.76%
list/serializers.py                191     75  60.73%
list/tests.py                        1      1   0.00%
list/urls.py                         4      0 100.00%
list/views.py                      592    503  15.03%
login/__init__.py                    0      0 100.00%
login/admin.py                       8      0 100.00%
login/apps.py                        4      0 100.00%
login/controllers.py                32      6  81.25%
login/models.py                      9      0 100.00%
login/tests.py                       1      1   0.00%
login/urls.py                        3      0 100.00%
login/views.py                      73      9  87.67%
utils/__init__.py                    0      0 100.00%
utils/audit.py                      69     69   0.00%
utils/authentication.py             21      1  95.24%
utils/jwt.py                        55      3  94.55%
utils/register_params_check.py      18      2  88.89%
TOTAL                             1966   1241  36.88%
Coverage HTML written to dir /reports/backend-coverage-html
Coverage XML written to file /reports/backend-coverage.xml
============================== 63 passed in 4.41s ==============================
```

## 前端测试结果

 FAIL  src/api/__tests__/profileApi.test.js [ src/api/__tests__/profileApi.test.js ]
 FAIL  src/router/__tests__/router.test.js [ src/router/__tests__/router.test.js ]
 FAIL  src/components/ui/__tests__/EmptyState.test.js [ src/components/ui/__tests__/EmptyState.test.js ]
 FAIL  src/utils/__tests__/formatters.test.js [ src/utils/__tests__/formatters.test.js ]
 FAIL  src/views/__tests__/DishDetail.test.js [ src/views/__tests__/DishDetail.test.js ]
 Test Files  9 failed (9)
      Tests  no tests

### 详细结果
```

 FAIL  src/components/__tests__/DishCard.test.js [ src/components/__tests__/DishCard.test.js ]
Error: Failed to load url /app/src/frontend/src/test-setup.js (resolved id: /app/src/frontend/src/test-setup.js). Does the file exist?
 ❯ loadAndTransform node_modules/vitest/node_modules/vite/dist/node/chunks/dep-BK3b2jBa.js:51969:17

⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯[1/9]⎯

 FAIL  src/components/__tests__/ImageUploader.test.js [ src/components/__tests__/ImageUploader.test.js ]
 FAIL  src/components/__tests__/TopBar.test.js [ src/components/__tests__/TopBar.test.js ]
 FAIL  src/api/__tests__/listApi.test.js [ src/api/__tests__/listApi.test.js ]
 FAIL  src/api/__tests__/profileApi.test.js [ src/api/__tests__/profileApi.test.js ]
 FAIL  src/router/__tests__/router.test.js [ src/router/__tests__/router.test.js ]
 FAIL  src/components/ui/__tests__/EmptyState.test.js [ src/components/ui/__tests__/EmptyState.test.js ]
Error: Failed to load url /app/src/frontend/src/test-setup.js (resolved id: /app/src/frontend/src/test-setup.js). Does the file exist?
 ❯ loadAndTransform node_modules/vitest/node_modules/vite/dist/node/chunks/dep-BK3b2jBa.js:51969:17

⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯[2/9]⎯

 FAIL  src/utils/__tests__/formatters.test.js [ src/utils/__tests__/formatters.test.js ]
 FAIL  src/views/__tests__/DishDetail.test.js [ src/views/__tests__/DishDetail.test.js ]
Error: Failed to load url /app/src/frontend/src/test-setup.js (resolved id: /app/src/frontend/src/test-setup.js). Does the file exist?
 ❯ loadAndTransform node_modules/vitest/node_modules/vite/dist/node/chunks/dep-BK3b2jBa.js:51969:17

⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯[3/9]⎯

 Test Files  9 failed (9)
      Tests  no tests
   Start at  14:05:15
   Duration  2.94s (transform 53ms, setup 0ms, collect 0ms, tests 0ms, environment 14.77s, prepare 3.06s)
```

## 覆盖率报告位置

- **后端 HTML 覆盖率报告**: `backend-coverage-html/index.html`
- **后端 XML 覆盖率报告**: `backend-coverage.xml`
- **前端覆盖率报告**: `frontend-coverage/index.html` (如果存在)

## 详细测试结果文件

- **后端测试详细结果**: `backend-test-results.txt`
- **前端测试详细结果**: `frontend-test-results.txt`

## 查看报告

### 在浏览器中查看后端覆盖率
```bash
open test-reports/20251220_220503/backend-coverage-html/index.html
```

### 在浏览器中查看前端覆盖率（如果存在）
```bash
open test-reports/20251220_220503/frontend-coverage/index.html
```
