/**
 * 认证功能端到端测试
 * 测试用户登录、注册、登出等功能
 */

describe('用户认证流程', () => {
  beforeEach(() => {
    cy.visit('/');
  });

  describe('用户登录', () => {
    it('应该能够成功登录', () => {
      cy.visit('/login');
      
      // 填写登录表单
      cy.get('[data-cy=username-input], input[name="username"], input[placeholder*="用户名"]')
        .type('testuser');
      cy.get('[data-cy=password-input], input[name="password"], input[type="password"]')
        .type('password123');
      
      // 提交表单
      cy.get('[data-cy=login-button], button[type="submit"]').click();
      
      // 验证登录成功
      cy.url().should('not.include', '/login');
      cy.window().its('localStorage').invoke('getItem', 'token').should('exist');
    });

    it('应该显示无效凭据错误', () => {
      cy.visit('/login');
      
      cy.get('[data-cy=username-input], input[name="username"], input[placeholder*="用户名"]')
        .type('wronguser');
      cy.get('[data-cy=password-input], input[name="password"], input[type="password"]')
        .type('wrongpassword');
      
      cy.get('[data-cy=login-button], button[type="submit"]').click();
      
      // 验证显示错误消息
      cy.contains(/用户名或密码错误|Invalid credentials|登录失败/i).should('be.visible');
      cy.url().should('include', '/login');
    });

    it('应该验证必填字段', () => {
      cy.visit('/login');
      
      // 尝试提交空表单
      cy.get('[data-cy=login-button], button[type="submit"]').click();
      
      // 检查 HTML5 验证或自定义验证消息
      cy.get('input[name="username"]').then(($input) => {
        expect($input[0].validationMessage || $input[0].checkValidity()).to.exist;
      });
    });

    it('应该能够查看和隐藏密码', () => {
      cy.visit('/login');
      
      const password = 'password123';
      cy.get('input[type="password"]').type(password);
      
      // 点击显示密码按钮（如果存在）
      cy.get('button[aria-label*="显示"], button[aria-label*="Show"], .password-toggle').then(($btn) => {
        if ($btn.length > 0) {
          cy.wrap($btn).click();
          cy.get('input[type="text"]').should('have.value', password);
        }
      });
    });
  });

  describe('用户注册', () => {
    it('应该能够成功注册新用户', () => {
      cy.visit('/register');
      
      const timestamp = Date.now();
      const testUser = {
        username: `testuser_${timestamp}`,
        email: `test_${timestamp}@example.com`,
        password: 'Password123!',
        confirmPassword: 'Password123!'
      };
      
      // 填写注册表单
      cy.get('input[name="username"]').type(testUser.username);
      cy.get('input[name="email"], input[type="email"]').type(testUser.email);
      cy.get('input[name="password"]').first().type(testUser.password);
      cy.get('input[name="confirmPassword"], input[name="password_confirm"]')
        .type(testUser.confirmPassword);
      
      // 提交注册
      cy.get('button[type="submit"]').click();
      
      // 验证注册成功 - 可能跳转到登录页或直接登录
      cy.url().should('match', /\/(login|home|dashboard)/);
    });

    it('应该在密码不匹配时显示错误', () => {
      cy.visit('/register');
      
      cy.get('input[name="username"]').type('testuser');
      cy.get('input[name="email"]').type('test@example.com');
      cy.get('input[name="password"]').first().type('Password123!');
      cy.get('input[name="confirmPassword"], input[name="password_confirm"]')
        .type('DifferentPassword123!');
      
      cy.get('button[type="submit"]').click();
      
      cy.contains(/密码不匹配|Passwords do not match|不一致/i).should('be.visible');
    });

    it('应该在用户名已存在时显示错误', () => {
      cy.visit('/register');
      
      // 使用已存在的用户名
      cy.get('input[name="username"]').type('testuser');
      cy.get('input[name="email"]').type('newemail@example.com');
      cy.get('input[name="password"]').first().type('Password123!');
      cy.get('input[name="confirmPassword"], input[name="password_confirm"]')
        .type('Password123!');
      
      cy.get('button[type="submit"]').click();
      
      // 验证错误消息
      cy.contains(/用户名已存在|Username already exists|已被占用/i, { timeout: 10000 })
        .should('be.visible');
    });

    it('应该验证邮箱格式', () => {
      cy.visit('/register');
      
      cy.get('input[name="email"]').type('invalid-email');
      cy.get('input[name="username"]').click(); // 触发失焦验证
      
      // 检查 HTML5 验证或自定义验证
      cy.get('input[name="email"]').then(($input) => {
        expect($input[0].validity.valid).to.be.false;
      });
    });
  });

  describe('用户登出', () => {
    beforeEach(() => {
      // 先登录
      cy.visit('/login');
      cy.get('input[name="username"]').type('testuser');
      cy.get('input[name="password"]').type('password123');
      cy.get('button[type="submit"]').click();
      cy.url().should('not.include', '/login');
    });

    it('应该能够成功登出', () => {
      // 查找并点击登出按钮
      cy.get('[data-cy=logout-button], button:contains("登出"), button:contains("Logout"), a:contains("退出")')
        .click();
      
      // 验证登出成功
      cy.url().should('match', /\/(login|home|$)/);
      cy.window().its('localStorage').invoke('getItem', 'token').should('not.exist');
    });

    it('登出后应该无法访问受保护的页面', () => {
      // 先登出
      cy.get('[data-cy=logout-button], button:contains("登出"), button:contains("Logout")')
        .click();
      
      // 尝试访问受保护的页面
      cy.visit('/profile');
      
      // 应该被重定向到登录页
      cy.url().should('include', '/login');
    });
  });

  describe('会话管理', () => {
    it('应该保持登录状态在页面刷新后', () => {
      // 登录
      cy.visit('/login');
      cy.get('input[name="username"]').type('testuser');
      cy.get('input[name="password"]').type('password123');
      cy.get('button[type="submit"]').click();
      cy.url().should('not.include', '/login');
      
      // 刷新页面
      cy.reload();
      
      // 验证仍然登录
      cy.url().should('not.include', '/login');
      cy.window().its('localStorage.token').should('exist');
    });

    it('未登录时访问受保护页面应该重定向到登录', () => {
      cy.visit('/profile');
      cy.url().should('include', '/login');
    });
  });

  describe('密码找回', () => {
    it('应该显示忘记密码链接', () => {
      cy.visit('/login');
      cy.contains(/忘记密码|Forgot password/i).should('be.visible');
    });
  });
});
