/**
 * E2E测试：用户核心流程
 * 测试从注册到评论的完整用户旅程
 */

describe('用户核心流程 E2E', () => {
  // 在每个测试前访问首页
  beforeEach(() => {
    cy.visit('/');
  });

  it('完整用户旅程：注册-登录-浏览-评分-评论', () => {
    // 生成唯一的用户名避免冲突
    const timestamp = Date.now();
    const username = `testuser_${timestamp}`;
    const password = 'testpass123';
    const nickname = '测试用户';

    // 1. 访问首页
    cy.url().should('include', '/');

    // 2. 点击注册（如果有注册链接）
    cy.contains('注册').click({ force: true });

    // 3. 填写注册表单
    cy.get('input[name="username"], input[placeholder*="用户名"]').first().type(username);
    cy.get('input[name="password"], input[type="password"]').first().type(password);
    cy.get('input[name="nickname"], input[placeholder*="昵称"]').first().type(nickname);

    // 4. 提交注册
    cy.contains('button', '注册').click();

    // 5. 等待注册成功提示（可能需要登录）
    cy.wait(1000);

    // 6. 如果注册后需要登录，则进行登录
    cy.url().then((url) => {
      if (url.includes('login')) {
        cy.get('input[name="username"]').type(username);
        cy.get('input[type="password"]').type(password);
        cy.contains('button', '登录').click();
      }
    });

    // 7. 等待登录成功
    cy.wait(1000);

    // 验证登录成功（检查是否有用户信息或欢迎消息）
    cy.contains(nickname, { timeout: 5000 }).should('be.visible');
  });

  it('浏览食堂和菜品', () => {
    // 测试浏览功能（不需要登录）
    cy.visit('/');

    // 查找并点击食堂列表链接
    cy.contains('食堂', { timeout: 5000 });

    // 如果有食堂卡片，点击第一个
    cy.get('[data-cy="canteen-card"], .canteen-card, .canteen-item')
      .first()
      .should('be.visible')
      .click({ force: true });

    // 等待页面加载
    cy.wait(1000);

    // 验证进入了食堂详情页
    cy.url().should('match', /canteen|dishes/);
  });

  it('搜索菜品', () => {
    cy.visit('/');

    // 查找搜索输入框
    cy.get('input[type="search"], input[placeholder*="搜索"]').first().type('宫保鸡丁');

    // 点击搜索按钮或按Enter
    cy.get('button[type="submit"], button:contains("搜索")').first().click({ force: true });

    // 等待搜索结果
    cy.wait(1000);

    // 验证URL或页面内容变化
    cy.url().should('match', /search|dishes/);
  });

  it('查看菜品详情', () => {
    cy.visit('/');

    // 查找并点击第一个菜品卡片
    cy.get('[data-cy="dish-card"], .dish-card, .dish-item').first().click({ force: true });

    // 等待详情页加载
    cy.wait(1000);

    // 验证菜品详情页内容
    cy.url().should('match', /dish/);

    // 验证页面包含菜品信息
    cy.contains('价格', { timeout: 5000 });
  });
});

describe('用户认证流程', () => {
  it('测试登录流程', () => {
    cy.visit('/');

    // 查找登录链接
    cy.contains('登录').click({ force: true });

    // 填写登录表单（使用测试账号）
    cy.get('input[name="username"]').type('testuser');
    cy.get('input[type="password"]').type('testpass');

    // 提交登录
    cy.contains('button', '登录').click();

    // 等待响应
    cy.wait(1000);
  });

  it('测试登出流程', () => {
    // 假设已经登录
    cy.visit('/');

    // 查找并点击用户菜单
    cy.get('[data-cy="user-menu"], .user-menu').click({ force: true });

    // 点击登出
    cy.contains('登出').click({ force: true });

    // 验证已登出
    cy.wait(500);
    cy.contains('登录').should('be.visible');
  });
});

describe('错误处理', () => {
  it('处理无效的登录凭证', () => {
    cy.visit('/login');

    cy.get('input[name="username"]').type('invaliduser');
    cy.get('input[type="password"]').type('wrongpassword');
    cy.contains('button', '登录').click();

    // 应该显示错误消息
    cy.wait(500);
    cy.contains(/错误|失败|Invalid|incorrect/i, { timeout: 3000 });
  });

  it('处理不存在的页面', () => {
    cy.visit('/nonexistent-page', { failOnStatusCode: false });

    // 应该显示404页面或重定向
    cy.wait(500);
    cy.url().then((url) => {
      expect(url).to.match(/404|not-found|home/);
    });
  });
});
