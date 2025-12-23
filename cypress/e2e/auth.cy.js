/**
 * E2E 认证流程测试
 * 测试流程：注册 -> 登录 -> 登出 -> 再次登录
 * 每个环节包含：空表单测试、不合法输入测试、正常流程测试
 */

describe('E2E 认证流程测试', () => {
  // 生成符合前后端校验的用户名：以字母开头且包含数字，长度 5-12
  const suffix = String(Date.now()).slice(-4) // 取时间戳后4位作为数字后缀
  const testUser = {
    username: `tester${suffix}`,
    password: '123456Aa-',
    nickname: `测试用户${suffix}`
  }

  // 在所有测试之前清理状态
  before(() => {
    cy.clearLocalStorage()
  })

  // 辅助：处理可能的 onboarding 重定向（/profile -> /onboarding/tags）
  function handlePossibleOnboarding() {
    return cy.location('pathname', { timeout: 20000 }).then((p) => {
      if (p.includes('/tags')) {
        // 确保 actions 区域和跳过按钮已渲染
        cy.get('.actions', { timeout: 10000 }).should('exist')
        cy.contains('button', '跳过', { timeout: 10000 }).should('be.visible')
        // 定义递归尝试函数：最多尝试 3 次点击跳过
        const trySkipAttempt = (attempt = 1) => {
          return cy.contains('button', '跳过', { timeout: 10000 }).then(($btn) => {
            cy.wrap($btn).click({ force: attempt > 1 })
            // 点击后短等待让路由和异步处理有机会完成，然后检查当前路径
            return cy.wait(500).then(() => {
              return cy.location('pathname', { timeout: 5000 }).then((uAfter) => {
                if (uAfter.includes('/profile')) return cy.wrap(null)
                if (attempt < 3) {
                  cy.log(`Skip attempt ${attempt} failed, retrying...`)
                  return trySkipAttempt(attempt + 1)
                }
                // 三次尝试后仍未跳转，断言失败
                throw new Error('点击跳过后未能跳转到 /profile')
              })
            })
          })
        }
        return trySkipAttempt(1)
      }
      if (p.includes('/profile')) {
        // profile 页面短暂触发跳转到 onboarding 的情况，等待并再次检查
        return cy.wait(500).then(() => {
          return cy.location('pathname', { timeout: 5000 }).then((p2) => {
            if (p2.includes('/onboarding/tags')) {
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
        })
      }
      // 既不是 profile 也不是 onboarding，短等待后重试
      return cy.wait(500).then(() => handlePossibleOnboarding())
    })
  }

  // 每个测试后清理状态
  afterEach(() => {
    cy.clearLocalStorage()
  })

  describe('步骤1: 用户注册', () => {
    beforeEach(() => {
      cy.visit('/register')
    })

    it('应当能够成功注册新用户', () => {
      // 填写表单
      cy.get('input[autocomplete="username"]').type(testUser.username)
      cy.get('input[autocomplete="new-password"]').type(testUser.password)
      cy.get('input').eq(2).type(testUser.nickname) // 昵称字段
      
      // 提交注册（在 .el-form 内查找注册按钮）
      cy.get('.el-form').find('button.register-btn').click()
      
      // 等待 JWT 写入 localStorage，然后断言跳转
      cy.window().its('localStorage').invoke('getItem', 'jwt').should('exist')
      // 处理可能的 onboarding 跳转（包括 profile -> onboarding 的短暂跳转）
      handlePossibleOnboarding()
      
      // 验证用户信息已保存
      cy.window().then((win) => {
        const userInfo = JSON.parse(win.localStorage.getItem('userInfo'))
        expect(userInfo).to.exist
        expect(userInfo.username).to.equal(testUser.username)
      })
    })

    it('应当拒绝空表单提交', () => {
      // 直接点击注册按钮（不填写任何信息）——在 .el-form 内查找
      cy.get('.el-form').find('button.register-btn').first().click()
      
      // 应当留在注册页面
      cy.url().should('include', '/register')
      
      // 应当不存在 JWT token
      cy.window().then((win) => {
        expect(win.localStorage.getItem('jwt')).to.not.exist
      })
    })

    it('应当拒绝不合法的用户名（不符合格式要求）', () => {
      // 测试纯数字用户名
      cy.get('input[autocomplete="username"]').type('123456')
      cy.get('input[autocomplete="new-password"]').type(testUser.password)
      cy.get('input').eq(2).type(testUser.nickname)
      cy.get('.el-form').find('button.register-btn').first().click()
      
      // 应当留在注册页面（前端校验拦截）
      cy.url().should('include', '/register')
    })

    it('应当拒绝不合法的密码（不符合强度要求）', () => {
      // 测试弱密码
      cy.get('input[autocomplete="username"]').type(testUser.username)
      cy.get('input[autocomplete="new-password"]').type('12345678') // 缺少大小写字母和符号
      cy.get('input').eq(2).type(testUser.nickname)
      cy.get('.el-form').find('button.register-btn').first().click()
      
      // 应当留在注册页面（前端校验拦截）
      cy.url().should('include', '/register')
    })

    it('应当拒绝空昵称', () => {
      cy.get('input[autocomplete="username"]').type(testUser.username)
      cy.get('input[autocomplete="new-password"]').type(testUser.password)
      // 昵称留空
      cy.get('.el-form').find('button.register-btn').first().click()
      
      // 应当留在注册页面
      cy.url().should('include', '/register')
    })
  })

  describe('步骤2: 用户登录', () => {
    // 确保测试用户已注册（从步骤1获得）
    before(() => {
      // 如果步骤1已创建用户，这里直接测试登录
      cy.clearLocalStorage()
    })

    beforeEach(() => {
      cy.visit('/login')
    })

    it('应当能够使用已注册账号成功登录', () => {
      // 使用已注册的测试账号登录
      cy.get('input[autocomplete="username"]').type(testUser.username)
      cy.get('input[autocomplete="current-password"]').type(testUser.password)
      
      // 点击登录按钮（在 .el-form 内查找）
        cy.get('.el-form').find('button.login-btn').first().click()
      
      // 验证跳转并处理 onboarding 流程
      cy.url().should('not.include', '/login')
      handlePossibleOnboarding()
      
      // 验证 JWT token 存在
        cy.window().its('localStorage').invoke('getItem', 'jwt').should('exist')
      
      // 验证用户信息存在
      cy.window().then((win) => {
        const userInfo = JSON.parse(win.localStorage.getItem('userInfo'))
        expect(userInfo).to.exist
        expect(userInfo.username).to.equal(testUser.username)
      })
      // 合并登出流程：登录后直接尝试登出
      cy.visit('/profile')
      cy.contains('button', '登出账号', { timeout: 10000 }).first().click()
      cy.url().should('include', '/login')
      cy.window().then((win) => {
        expect(win.localStorage.getItem('jwt')).to.be.null
        expect(win.localStorage.getItem('userInfo')).to.be.null
      })
      // 再次登录验证（合并）：使用相同账号再次登录并验证
      cy.visit('/login')
      cy.get('input[autocomplete="username"]').type(testUser.username)
      cy.get('input[autocomplete="current-password"]').type(testUser.password)
      cy.get('.el-form').find('button.login-btn').first().click()
      cy.url().should('not.include', '/login')
      handlePossibleOnboarding()
      cy.window().its('localStorage').invoke('getItem', 'jwt').should('exist')
      cy.window().then((win) => {
        const userInfo = JSON.parse(win.localStorage.getItem('userInfo'))
        expect(userInfo).to.exist
        expect(userInfo.username).to.equal(testUser.username)
      })
    })

    it('应当拒绝空表单提交', () => {
      // 不填写任何信息直接点击登录（在 .el-form 内查找）
      cy.get('.el-form').find('button.login-btn').first().click()
      
      // 应当留在登录页面
      cy.url().should('include', '/login')
    })

    it('应当拒绝错误的用户名', () => {
      cy.get('input[autocomplete="username"]').type('wronguser999')
      cy.get('input[autocomplete="current-password"]').type(testUser.password)
      cy.get('.el-form').find('button.login-btn').first().click()
      
      // 应当留在登录页面
      cy.url().should('include', '/login')
      
      // 不应存在 token
      cy.window().then((win) => {
        expect(win.localStorage.getItem('jwt')).to.not.exist
      })
    })

    it('应当拒绝错误的密码', () => {
      cy.get('input[autocomplete="username"]').type(testUser.username)
      cy.get('input[autocomplete="current-password"]').type('WrongPass123-')
      cy.get('.el-form').find('button.login-btn').first().click()
      
      // 应当留在登录页面
      cy.url().should('include', '/login')
      
      // 不应存在 token
      cy.window().then((win) => {
        expect(win.localStorage.getItem('jwt')).to.not.exist
      })
    })
  })

  
})
