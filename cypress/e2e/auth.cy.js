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
      
      // 提交注册
      cy.get('button.register-btn').first().click()
      
      // 等待 JWT 写入 localStorage，然后断言跳转
      cy.window().its('localStorage').invoke('getItem', 'jwt').should('exist')
      cy.url({ timeout: 20000 }).should('match', /\/(profile|onboarding\/tags)/)
      
      // 验证用户信息已保存
      cy.window().then((win) => {
        const userInfo = JSON.parse(win.localStorage.getItem('userInfo'))
        expect(userInfo).to.exist
        expect(userInfo.username).to.equal(testUser.username)
      })
    })

    it('应当拒绝空表单提交', () => {
      // 直接点击注册按钮（不填写任何信息）
      cy.get('button.register-btn').first().click()
      
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
      cy.get('button.register-btn').first().click()
      
      // 应当留在注册页面（前端校验拦截）
      cy.url().should('include', '/register')
    })

    it('应当拒绝不合法的密码（不符合强度要求）', () => {
      // 测试弱密码
      cy.get('input[autocomplete="username"]').type(testUser.username)
      cy.get('input[autocomplete="new-password"]').type('12345678') // 缺少大小写字母和符号
      cy.get('input').eq(2).type(testUser.nickname)
      cy.get('button.register-btn').first().click()
      
      // 应当留在注册页面（前端校验拦截）
      cy.url().should('include', '/register')
    })

    it('应当拒绝空昵称', () => {
      cy.get('input[autocomplete="username"]').type(testUser.username)
      cy.get('input[autocomplete="new-password"]').type(testUser.password)
      // 昵称留空
      cy.get('button.register-btn').first().click()
      
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
      
      // 点击登录按钮
        cy.get('button.login-btn').first().click()
      
      // 验证跳转到个人主页或标签设置页
      cy.url().should('not.include', '/login')
      cy.url().should('match', /\/(profile|onboarding\/tags)/)
      
      // 验证 JWT token 存在
        cy.window().its('localStorage').invoke('getItem', 'jwt').should('exist')
      
      // 验证用户信息存在
      cy.window().then((win) => {
        const userInfo = JSON.parse(win.localStorage.getItem('userInfo'))
        expect(userInfo).to.exist
        expect(userInfo.username).to.equal(testUser.username)
      })
    })

    it('应当拒绝空表单提交', () => {
      // 不填写任何信息直接点击登录
      cy.get('button.login-btn').first().click()
      
      // 应当留在登录页面
      cy.url().should('include', '/login')
    })

    it('应当拒绝错误的用户名', () => {
      cy.get('input[autocomplete="username"]').type('wronguser999')
      cy.get('input[autocomplete="current-password"]').type(testUser.password)
      cy.get('button.login-btn').first().click()
      
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
      cy.get('button.login-btn').first().click()
      
      // 应当留在登录页面
      cy.url().should('include', '/login')
      
      // 不应存在 token
      cy.window().then((win) => {
        expect(win.localStorage.getItem('jwt')).to.not.exist
      })
    })
  })

  describe('步骤3: 用户登出', () => {
    beforeEach(() => {
      // 先登录
      cy.visit('/login')
      cy.get('input[autocomplete="username"]').type(testUser.username)
      cy.get('input[autocomplete="current-password"]').type(testUser.password)
      cy.get('button.login-btn').first().click()
      
      // 等待跳转完成
      cy.url().should('not.include', '/login')
      cy.url().should('match', /\/(profile|onboarding\/tags)/)
    })

    it('应当能够成功登出', () => {
      // 访问个人主页（确保能看到登出按钮）
      cy.visit('/profile')
      
      // 点击登出按钮（ControlPanel 组件中的登出按钮）
      cy.contains('button', '登出账号').first().click()
      
      // 验证跳转到登录页
      cy.url().should('include', '/login')
      
      // 验证 JWT token 已清除
      cy.window().then((win) => {
        expect(win.localStorage.getItem('jwt')).to.be.null
      })
      
      // 验证用户信息已清除
      cy.window().then((win) => {
        expect(win.localStorage.getItem('userInfo')).to.be.null
      })
    })
  })

  describe('步骤4: 再次登录验证', () => {
    before(() => {
      // 确保已登出
      cy.clearLocalStorage()
    })

    beforeEach(() => {
      cy.visit('/login')
    })

    it('应当能够在登出后再次登录', () => {
      // 使用相同账号再次登录
      cy.get('input[autocomplete="username"]').type(testUser.username)
      cy.get('input[autocomplete="current-password"]').type(testUser.password)
      cy.get('button.login-btn').first().click()
      
      // 验证登录成功
      cy.url().should('not.include', '/login')
      cy.url().should('match', /\/(profile|onboarding\/tags)/)
      
      // 验证 token 和用户信息重新创建
      cy.window().its('localStorage').invoke('getItem', 'jwt').should('exist')
      cy.window().then((win) => {
        const userInfo = JSON.parse(win.localStorage.getItem('userInfo'))
        expect(userInfo).to.exist
        expect(userInfo.username).to.equal(testUser.username)
      })
    })
  })
})
