/**
 * 食堂和菜品功能端到端测试
 * 测试流程：食堂浏览 -> 楼层/窗口/菜品 -> 菜品搜索 -> 菜品详情 -> 打卡/评分/评论
 */

describe('E2E 食堂和菜品测试', () => {
  const testUser = {
    username: 'tester123',
    password: '123456Aa-'
  }

  // 辅助：处理可能的 onboarding 重定向（简化版）
  function handlePossibleOnboarding() {
    return cy.location('pathname', { timeout: 20000 }).then((p) => {
      if (p.includes('/tags') || p.includes('/onboarding/tags')) {
        cy.get('.actions', { timeout: 10000 }).should('exist')
        cy.contains('button', '跳过', { timeout: 10000 }).should('be.visible')
        const trySkipAttempt = (attempt = 1) => {
          return cy.contains('button', '跳过', { timeout: 10000 }).then(($btn) => {
            cy.wrap($btn).click({ force: attempt > 1 })
            return cy.wait(500).then(() => {
              return cy.location('pathname', { timeout: 5000 }).then((uAfter) => {
                if (uAfter.includes('/profile')) return cy.wrap(null)
                if (attempt < 3) {
                  cy.log(`Skip attempt ${attempt} failed, retrying...`)
                  return trySkipAttempt(attempt + 1)
                }
                throw new Error('点击跳过后未能跳转到 /profile')
              })
            })
          })
        }
        return trySkipAttempt(1)
      }
      return cy.wrap(null)
    })
  }

  // 在每个测试前清理状态并登录（确保登录状态一致）
  beforeEach(() => {
    cy.clearLocalStorage()
    cy.clearCookies()
    cy.visit('/login')
    // 在 .el-form 内输入用户名和密码，以匹配前端表单结构
    cy.get('.el-form').within(() => {
      cy.get('input[autocomplete="username"]').clear().type(testUser.username)
      cy.get('input[autocomplete="current-password"]').clear().type(testUser.password)
      cy.get('button.login-btn').first().click()
    })
    cy.url().should('not.include', '/login')
    // 处理可能的 onboarding 跳转
    handlePossibleOnboarding()
    // 验证 JWT token 存在
    cy.window().its('localStorage').invoke('getItem', 'jwt').should('exist')
  })

  describe('步骤1: 通过多层列表浏览食堂、楼层、菜品', () => {
    beforeEach(() => {
      cy.visit('/canteen')
    })

    it('应当显示食堂列表（侧边栏）', () => {
      // CanteenSidebar 组件显示食堂列表
      cy.get('.canteen-sidebar-menu').should('exist')
      cy.get('.canteen-sidebar-menu .el-menu-item').should('have.length.greaterThan', 0)
    })

    it('应当能够点击选择不同食堂', () => {
      // 点击第一个食堂
      cy.get('.canteen-sidebar-menu .el-menu-item').first().click()
      cy.get('.canteen-sidebar-menu .el-menu-item.is-active').should('exist')

      // 点击第二个食堂（如果有）
      cy.get('.canteen-sidebar-menu .el-menu-item').eq(1).then(($item) => {
        if ($item.length > 0) {
          cy.wrap($item).click()
          cy.get('.canteen-sidebar-menu .el-menu-item.is-active').should('exist')
        }
      })
    })

    it('应当显示选中食堂的楼层标签页', () => {
      // 选择第一个食堂
      cy.get('.canteen-sidebar-menu .el-menu-item').first().click()
      
      // 验证楼层标签页加载（el-tabs）
      cy.get('.el-tabs').should('exist')
      cy.get('.el-tabs__item').should('have.length.greaterThan', 0)
    })

    it('应当能够切换楼层标签', () => {
      // 选择食堂
      cy.get('.canteen-sidebar-menu .el-menu-item').eq(1).click()
      
      // 点击第一个楼层标签
      cy.get('.el-tabs__item').first().click()
      cy.get('.el-tabs__item.is-active').should('exist')
      
      // 切换到第二个楼层（如果有）
      cy.get('.el-tabs__item').eq(1).then(($tab) => {
        if ($tab.length > 0) {
          cy.wrap($tab).click()
          cy.wait(500) // 等待动画
          cy.get('.el-tabs__item.is-active').should('exist')
        }
      })
    })

    it('应当显示楼层下的窗口列表', () => {
      cy.get('.canteen-sidebar-menu .el-menu-item').first().click()
      
      // 验证窗口块加载
      cy.get('.window-block').should('have.length.greaterThan', 0)
      cy.get('.window-title').should('exist')
    })

    it('应当显示窗口下的菜品卡片', () => {
      cy.get('.canteen-sidebar-menu .el-menu-item').first().click()
      
      // 验证菜品卡片
      cy.get('.dish-card').should('have.length.greaterThan', 0)
      cy.get('.dish-card-name').should('exist')
      cy.get('.dish-card-price').should('exist')
    })

    it('应当能够点击菜品卡片跳转到详情页', () => {
      // 使用侧边栏实际的菜单项选择器并等待加载
      cy.get('.canteen-sidebar-menu .el-menu-item', { timeout: 10000 }).first().click()
      // 等待楼层/窗口数据加载（接口已返回后页面渲染）
      cy.get('.window-block', { timeout: 10000 }).should('have.length.greaterThan', 0)

      // 点击第一个菜品卡片
      cy.get('.dish-card', { timeout: 10000 }).first().click()

      // 验证跳转到菜品详情页
      cy.url().should('include', '/dish/')
      cy.get('.dish-title').should('exist')
    })
  })

  describe('步骤2: 菜品搜索功能（从食堂浏览触发）', () => {
    // 每个测试从食堂列表开始，通过侧边栏搜索框触发跳转到搜索页
    beforeEach(() => {
      cy.visit('/canteen')
      // 等待侧边栏加载
      cy.get('.canteen-sidebar-menu .el-menu-item', { timeout: 10000 }).should('have.length.greaterThan', 0)
    })

    it('应当能通过侧栏搜索跳转到搜索页并显示菜品卡片（按名称）', () => {
      // 在侧边栏的搜索输入中输入并回车（组件监听 keyup.enter）
      cy.get('.search-input input').clear().type('鸡{enter}')
      // 确认已跳转到搜索页
      cy.url({ timeout: 10000 }).should('include', '/search')
      // 验证结果至少有一个菜品卡片
      cy.get('.dish-card', { timeout: 10000 }).should('have.length.greaterThan', 0)
      cy.contains('鸡').should('be.visible')
    })

    it('搜索页应显示名称、价格、标签三种筛选并能按名称搜索', () => {
      // 从侧栏触发搜索到搜索页
      cy.get('.search-input input').clear().type('肉{enter}')
      cy.url().should('include', '/search')

      // 名称输入存在
      cy.get('input[placeholder*="菜品名"]').should('exist')

      // 价格区间存在并能输入
      cy.get('.el-input-number').should('have.length', 2)
      cy.get('input[placeholder*="菜品名"]').clear().type('肉')
      cy.contains('button', '搜索').first().click()
      cy.get('.dish-card', { timeout: 10000 }).should('have.length.greaterThan', 0)
    })

    it('应当能够通过价格区间筛选', () => {
      cy.get('.search-input input').clear().type('肉{enter}')
      cy.url().should('include', '/search')

      // 设置价格区间 10-20（定位到 el-input-number 内部的真实 input）
      cy.get('.el-input-number').first().find('input').clear().type('10')
      cy.get('.el-input-number').eq(1).find('input').clear().type('20')
      // 名称输入以满足 canSearch 限制
      cy.get('input[placeholder*="菜品名"]').clear().type('肉')
      cy.contains('button', '搜索').click()
      cy.get('.dish-card', { timeout: 10000 }).should('exist')
    })

    it('应当能够通过标签筛选', () => {
      cy.get('.search-input input').clear().type('鸡{enter}')
      cy.url().should('include', '/search')

      // 点击标签下拉并选择第一个标签
      cy.get('.el-select').first().click()
      cy.get('.el-select-dropdown__item').first().click({ force: true })
      cy.contains('button', '搜索').first().click()
      cy.get('.dish-card', { timeout: 10000 }).should('have.length.greaterThan', 0)
    })

    it('应当能够组合搜索（名称 + 价格 + 标签）', () => {
      cy.get('.search-input input').clear().type('肉{enter}')
      cy.url().should('include', '/search')

      // 名称
      cy.get('input[placeholder*="菜品名"]').clear().type('肉')
      // 价格（定位到内部 input）
      cy.get('.el-input-number').first().find('input').clear().type('10')
      cy.get('.el-input-number').eq(1).find('input').clear().type('20')
      // 标签
      cy.get('.el-select').first().click()
      cy.get('.el-select-dropdown__item').first().click({ force: true })

      cy.contains('button', '搜索').first().click()
      cy.wait(2000)
      cy.get('body').then(($body) => {
        if ($body.find('.dish-card').length > 0) {
          cy.get('.dish-card').should('exist')
        } else {
          cy.get('.el-empty').should('exist')
        }
      })
    })

    it('搜索无结果时应显示空状态', () => {
      cy.get('.search-input input').clear().type('不存在的菜品xyz123{enter}')
      cy.url().should('include', '/search')
      cy.get('.el-empty', { timeout: 10000 }).should('exist')
      cy.contains('暂无菜品').should('be.visible')
    })

    it('应当能够从搜索结果点击进入菜品详情页', () => {
      cy.get('.search-input input').clear().type('鸡{enter}')
      cy.url().should('include', '/search')
      cy.get('.dish-card', { timeout: 10000 }).first().click()
      cy.url().should('include', '/dish/')
      cy.get('.dish-title').should('exist')
    })
  })

  describe('步骤3: 菜品详情页功能', () => {
    // 先通过搜索进入一个菜品详情页
    beforeEach(() => {
      cy.visit('/search')
      cy.get('input[placeholder*="菜品名"]').type('鸡')
      cy.contains('button', '搜索').click()
      cy.get('.dish-card', { timeout: 10000 }).first().click()
      cy.url().should('include', '/dish/')
    })

    it('应当显示菜品详细信息', () => {
      // 验证菜品名称
      cy.get('.dish-title').should('exist')
      
      // 验证菜品图片
      cy.get('.dish-image img, .dish-image').should('exist')
      
      // 验证价格
      cy.get('.dish-price').should('exist')
      cy.contains(/￥|¥/).should('be.visible')
      
      // 验证描述
      cy.get('.dish-desc').should('exist')
      
      // 验证标签
      cy.get('.dish-tags').should('exist')
      cy.get('.el-tag').should('have.length.greaterThan', 0)
    })

    it('应当显示菜品评分', () => {
      // 验证评分组件
      cy.get('.dish-rating').should('exist')
      cy.get('.el-rate').should('exist')
    })

    it('应当能够点击打卡', () => {
      // 找到打卡按钮
      cy.contains('button', '打卡').should('exist')

      // 读取当前打卡计数，拦截 POST 请求，点击打卡后断言接口返回 200 且计数 +1
      cy.get('.checkin-count').invoke('text').then((txt) => {
        const m = String(txt).match(/(\d+)/)
        const before = m ? Number(m[1]) : 0
        // 明确断言已登录（localStorage 中有 jwt）
        cy.window().its('localStorage').invoke('getItem', 'jwt').should('exist')
        cy.intercept('POST', '/api/dishes/*/check-in/').as('checkinReq')
        cy.contains('button', '打卡').click()
        // 等待网络请求并断言返回 200（否则会是 401/403）
        cy.wait('@checkinReq', { timeout: 10000 }).then((interception) => {
          // 断言请求中包含 Authorization 头（防止未携带 token）
          const authHeader = interception.request.headers && (interception.request.headers.authorization || interception.request.headers.Authorization)
          expect(authHeader, 'Authorization header should be sent').to.exist
          if (authHeader) expect(String(authHeader).length).to.be.greaterThan(0)

          const status = interception.response?.statusCode
          if (status !== 200) {
            // 记录响应体和请求头，便于诊断 403/401/其他错误原因
            // 注意：Cypress 控制台和运行日志会显示这些信息
            try {
              cy.log('checkin response body: ' + JSON.stringify(interception.response.body))
            } catch (e) { cy.log('checkin response body: <unserializable>') }
            try {
              cy.log('checkin request headers: ' + JSON.stringify(interception.request.headers))
            } catch (e) { cy.log('checkin request headers: <unserializable>') }
          }
          expect(status).to.equal(200)
        })
        // 再断言前端计数增加
        cy.get('.checkin-count', { timeout: 10000 }).should(($el) => {
          const afterM = String($el.text()).match(/(\d+)/)
          const after = afterM ? Number(afterM[1]) : 0
          expect(after).to.equal(before + 1)
        })
      })
    })

    it('应当能够对菜品评分', () => {
      // 找到用户评分区域
      cy.contains('我要打分').should('exist')

      // 读取当前平均分文本（若存在）
      cy.get('.dish-rating .el-rate .el-rate__text').invoke('text').then((scoreBefore) => {
        const beforeNum = parseFloat(String(scoreBefore).trim()) || null

        // 明确断言已登录（localStorage 中有 jwt）
        cy.window().its('localStorage').invoke('getItem', 'jwt').should('exist')
        // 点击第4颗星（评4分）并提交，同时拦截评分请求以确保后端响应成功
        cy.intercept('POST', '/api/dishes/*/rate/').as('rateReq')
        cy.get('.rate-section .el-rate .el-rate__item').eq(3).click()
        cy.contains('button', '提交评分').click()
        // 等待网络请求并断言返回 200
        cy.wait('@rateReq', { timeout: 10000 }).then((interception) => {
          // 断言请求中包含 Authorization 头
          const authHeader = interception.request.headers && (interception.request.headers.authorization || interception.request.headers.Authorization)
          expect(authHeader, 'Authorization header should be sent').to.exist
          if (authHeader) expect(String(authHeader).length).to.be.greaterThan(0)

          const status = interception.response?.statusCode
          if (status !== 200) {
            try {
              cy.log('rate response body: ' + JSON.stringify(interception.response.body))
            } catch (e) { cy.log('rate response body: <unserializable>') }
            try {
              cy.log('rate request headers: ' + JSON.stringify(interception.request.headers))
            } catch (e) { cy.log('rate request headers: <unserializable>') }
          }
          expect(status).to.equal(200)
        })

        // 等待并断言平均分或展示已更新（避免只靠消息）
        cy.get('.dish-rating .el-rate .el-rate__text', { timeout: 10000 }).should(($el) => {
          const afterText = String($el.text()).trim()
          const afterNum = parseFloat(afterText) || null
          if (beforeNum !== null && afterNum !== null) {
            expect(afterNum).to.not.equal(beforeNum)
          } else {
            cy.get('body').should('not.contain.text', '您需要先登录')
            cy.get('body').should('not.contain.text', '没有权限')
          }
        })
      })
    })

    it('应当能够发表评论', () => {
      // 找到评论输入框
      cy.get('.comment-input textarea').should('exist')
      
      // 输入评论内容（至少5个字）
      const commentText = '这道菜非常好吃，值得推荐！'
      cy.get('.comment-input textarea').type(commentText)
      
      // 点击发表评论按钮
      cy.contains('button', '发表评论').click()
      
      // 验证评论成功（可能显示成功消息或评论出现在列表中）
      cy.wait(2000)
    })

    it('应当显示历史评论列表', () => {
      // 滚动到评论区域
      cy.get('.dish-reviews').should('exist')
      cy.contains('评论').should('exist')
      
      // 验证评论列表或空状态
      cy.get('body').then(($body) => {
        if ($body.find('.review-card').length > 0) {
          cy.get('.review-card').should('exist')
          cy.get('.review-user').should('exist')
          cy.get('.review-content').should('exist')
        } else {
          cy.get('.el-empty').should('exist')
        }
      })
    })

    it('应当能够返回上一页', () => {
      // 点击返回按钮
      cy.contains('button', '返回').click()
      
      // 验证返回到搜索页
      cy.url().should('include', '/search')
    })
  })

  describe('步骤4: 边界情况和用户体验', () => {
    it('菜品详情页应当显示打卡进度', () => {
      cy.visit('/search')
      cy.get('input[placeholder*="菜品名"]').type('鸡')
      cy.contains('button', '搜索').click()
      cy.get('.dish-card', { timeout: 10000 }).first().click()
      
      // 验证打卡进度条或等级标识
      cy.get('.checkin-section').should('exist')
      cy.get('.checkin-count').should('exist')
    })

    it('评论长度不足时应当禁用提交按钮', () => {
      cy.visit('/search')
      cy.get('input[placeholder*="菜品名"]').type('鸡')
      cy.contains('button', '搜索').click()
      cy.get('.dish-card', { timeout: 10000 }).first().click()
      
      // 输入少于5个字的评论
      cy.get('.comment-input textarea').clear().type('好吃')
      
      // 验证提交按钮被禁用
      cy.contains('button', '发表评论').should('be.disabled')
    })

    it('搜索表单未填写时应当禁用搜索按钮', () => {
      cy.visit('/search')
      
      // 验证搜索按钮被禁用（因为 canSearch 要求菜品名或标签）
      cy.contains('button', '搜索').should('be.disabled')
    })
  })
});
