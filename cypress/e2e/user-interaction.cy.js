/**
 * E2E测试：用户交互完整流程
 * 测试用户注册、登录、浏览、评分、评论、发帖等完整交互
 */

describe('用户完整交互流程 E2E', () => {
  const timestamp = Date.now();
  const username = `testuser_${timestamp}`;
  const password = 'testpass123';
  const nickname = '测试用户';

  beforeEach(() => {
    cy.visit('/');
    cy.wait(500);
  });

  it('新用户注册流程', () => {
    // 点击注册链接
    cy.contains('注册', { timeout: 5000 }).click({ force: true });

    // 等待注册页面加载
    cy.wait(1000);

    // 填写注册表单
    cy.get('input[name="username"], input[placeholder*="用户名"]')
      .first()
      .should('be.visible')
      .clear()
      .type(username);

    cy.get('input[name="password"], input[type="password"]')
      .first()
      .should('be.visible')
      .clear()
      .type(password);

    cy.get('input[name="nickname"], input[placeholder*="昵称"]')
      .first()
      .should('be.visible')
      .clear()
      .type(nickname);

    // 提交注册
    cy.contains('button', '注册').click({ force: true });

    // 等待响应
    cy.wait(2000);

    // 验证注册成功（可能自动登录或跳转到登录页）
    cy.url().then((url) => {
      if (url.includes('login')) {
        // 如果跳转到登录页，需要手动登录
        cy.get('input[name="username"]').clear().type(username);
        cy.get('input[type="password"]').clear().type(password);
        cy.contains('button', '登录').click();
        cy.wait(1000);
      }
    });

    // 验证登录成功
    cy.contains(nickname, { timeout: 5000 }).should('be.visible');
  });

  it('用户登录流程', () => {
    // 假设用户已注册，现在测试登录
    cy.contains('登录').click({ force: true });

    cy.get('input[name="username"]').clear().type(username);
    cy.get('input[type="password"]').clear().type(password);
    cy.contains('button', '登录').click();

    cy.wait(1000);

    // 验证登录成功
    cy.contains(nickname, { timeout: 5000 }).should('be.visible');
  });

  it('浏览和筛选菜品', () => {
    // 搜索菜品
    cy.get('input[type="search"], input[placeholder*="搜索"]').first().clear().type('宫保鸡丁');

    cy.get('input[type="search"], input[placeholder*="搜索"]').first().type('{enter}');

    cy.wait(1000);

    // 点击第一个菜品查看详情
    cy.get('[data-cy="dish-card"], .dish-card, .dish-item').first().click({ force: true });

    cy.wait(1000);

    // 验证详情页
    cy.url().should('match', /dish/);
    cy.contains('价格', { timeout: 5000 });
  });

  it('评分菜品', () => {
    // 访问菜品详情页
    cy.get('[data-cy="dish-card"], .dish-card, .dish-item').first().click({ force: true });

    cy.wait(1000);

    // 查找评分控件（假设是星级评分）
    cy.get('[data-cy="rating-stars"], .rating-stars, .stars')
      .first()
      .within(() => {
        // 点击4星
        cy.get('[data-rating="4"], .star:nth-child(4)').click({ force: true });
      });

    // 提交评分
    cy.contains('button', /评分|提交/).click({ force: true });

    cy.wait(1000);

    // 验证评分成功提示
    cy.contains(/评分成功|谢谢|已评分/i, { timeout: 3000 });
  });

  it('发表评论', () => {
    // 访问菜品详情页
    cy.get('[data-cy="dish-card"], .dish-card, .dish-item').first().click({ force: true });

    cy.wait(1000);

    // 查找评论输入框
    cy.get('[data-cy="comment-input"], textarea[name="comment"], .comment-input')
      .first()
      .clear()
      .type('这道菜真的很好吃！强烈推荐！');

    // 提交评论
    cy.contains('button', /发表评论|提交/).click({ force: true });

    cy.wait(1000);

    // 验证评论出现
    cy.contains('这道菜真的很好吃！强烈推荐！', { timeout: 3000 });
  });

  it('发帖分享美食', () => {
    // 点击发帖按钮
    cy.contains('发帖', { timeout: 5000 }).click({ force: true });

    cy.wait(1000);

    // 填写帖子内容
    cy.get('input[name="title"], input[placeholder*="标题"]')
      .first()
      .clear()
      .type('分享我的美食体验');

    cy.get('textarea[name="content"], .post-content')
      .first()
      .clear()
      .type(
        '今天在校园食堂吃到了超级好吃的宫保鸡丁！\\n\\n配料新鲜，味道正宗，厨师手艺一流！\\n\\n大家快去试试吧！'
      );

    // 上传图片（如果有的话）
    // cy.get('input[type="file"]').selectFile('cypress/fixtures/test-image.jpg', { force: true });

    // 提交帖子
    cy.contains('button', /发表|发布/).click({ force: true });

    cy.wait(2000);

    // 验证帖子发布成功
    cy.contains('分享我的美食体验', { timeout: 5000 });
  });

  it('浏览社区帖子', () => {
    // 访问社区页面
    cy.contains('社区', { timeout: 5000 }).click({ force: true });

    cy.wait(1000);

    // 验证帖子列表
    cy.get('[data-cy="post-item"], .post-item, .post-card').should('have.length.greaterThan', 0);

    // 点击查看帖子详情
    cy.get('[data-cy="post-item"], .post-item, .post-card').first().click({ force: true });

    cy.wait(1000);

    // 验证帖子详情页
    cy.url().should('match', /post|detail/);
  });

  it('对帖子点赞和评论', () => {
    // 访问帖子详情
    cy.get('[data-cy="post-item"], .post-item, .post-card').first().click({ force: true });

    cy.wait(1000);

    // 点击点赞
    cy.get('[data-cy="like-btn"], .like-btn, .btn-like').first().click({ force: true });

    cy.wait(500);

    // 验证点赞成功
    cy.get('[data-cy="like-btn"], .like-btn, .btn-like').first().should('have.class', 'liked');

    // 添加评论
    cy.get('[data-cy="comment-input"], .comment-input')
      .first()
      .clear()
      .type('很棒的分享！谢谢推荐！');

    cy.contains('button', /评论|回复/).click({ force: true });

    cy.wait(1000);

    // 验证评论出现
    cy.contains('很棒的分享！谢谢推荐！', { timeout: 3000 });
  });

  it('查看个人资料', () => {
    // 点击个人资料
    cy.contains('个人主页').click({ force: true });

    cy.wait(1000);

    // 验证个人资料页
    cy.url().should('match', /profile/);

    // 检查是否显示用户信息
    cy.contains(nickname, { timeout: 5000 });
  });

  it('编辑个人资料', () => {
    // 访问个人资料页
    cy.contains('个人主页').click({ force: true });

    cy.wait(1000);

    // 点击编辑按钮
    cy.contains('编辑资料', { timeout: 5000 }).click({ force: true });

    // 修改签名
    cy.get('textarea[name="bio"], input[name="signature"]')
      .first()
      .clear()
      .type('热爱美食，喜欢分享校园生活的点点滴滴！');

    // 保存修改
    cy.contains('button', /保存|提交/).click({ force: true });

    cy.wait(1000);

    // 验证修改成功
    cy.contains('热爱美食，喜欢分享校园生活的点点滴滴！', { timeout: 3000 });
  });

  it('用户登出', () => {
    // 点击用户菜单
    cy.get('[data-cy="user-menu"], .user-menu').first().click({ force: true });

    // 点击登出
    cy.contains('登出').click({ force: true });

    cy.wait(1000);

    // 验证已登出
    cy.contains('登录').should('be.visible');
    cy.contains(nickname).should('not.exist');
  });
});

describe('错误处理和边界情况', () => {
  beforeEach(() => {
    cy.visit('/');
    cy.wait(500);
  });

  it('处理无效登录凭证', () => {
    cy.contains('登录').click({ force: true });

    cy.get('input[name="username"]').clear().type('invaliduser');
    cy.get('input[type="password"]').clear().type('wrongpassword');

    cy.contains('button', '登录').click();

    cy.wait(1000);

    // 应该显示错误消息
    cy.contains(/错误|失败|Invalid|incorrect|用户名或密码错误/i, { timeout: 3000 });
  });

  it('处理重复评分', () => {
    // 登录并访问菜品详情
    cy.contains('登录').click();
    cy.get('input[name="username"]').clear().type('testuser');
    cy.get('input[type="password"]').clear().type('testpass');
    cy.contains('button', '登录').click();

    cy.wait(1000);

    // 访问菜品详情
    cy.get('[data-cy="dish-card"]').first().click();

    cy.wait(1000);

    // 尝试重复评分
    cy.get('.rating-stars .star').first().click();
    cy.contains('button', '评分').click();

    cy.wait(500);

    // 再次尝试评分
    cy.get('.rating-stars .star').eq(4).click();
    cy.contains('button', '评分').click();

    cy.wait(500);

    // 应该提示已评分或更新成功
    cy.contains(/已更新|评分成功|您已经/i, { timeout: 3000 });
  });

  it('处理空评论提交', () => {
    // 登录并访问菜品详情
    cy.contains('登录').click();
    cy.get('input[name="username"]').clear().type('testuser');
    cy.get('input[type="password"]').clear().type('testpass');
    cy.contains('button', '登录').click();

    cy.wait(1000);

    cy.get('[data-cy="dish-card"]').first().click();

    cy.wait(1000);

    // 尝试提交空评论
    cy.contains('button', /发表评论|提交/).click({ force: true });

    cy.wait(500);

    // 应该显示错误提示
    cy.contains(/不能为空|请输入|必填/i, { timeout: 3000 });
  });

  it('处理网络错误', () => {
    // 模拟网络断开
    cy.intercept('GET', '**/api/**', { forceNetworkError: true });

    cy.get('input[type="search"]').first().type('test{enter}');

    cy.wait(1000);

    // 应该显示网络错误提示
    cy.contains(/网络错误|连接失败|请检查网络/i, { timeout: 3000 });
  });
});

describe('响应式设计测试', () => {
  beforeEach(() => {
    cy.visit('/');
    cy.wait(500);
  });

  it('在移动设备上正常显示', () => {
    // 设置为手机视图
    cy.viewport('iphone-x');

    // 验证页面适配移动端
    cy.get('.top-bar').should('be.visible');
    cy.get('.nav-options').should('have.css', 'flex-direction', 'column');

    // 检查菜单是否可点击
    cy.contains('食堂浏览').should('be.visible').click({ force: true });
  });

  it('在平板设备上正常显示', () => {
    // 设置为平板视图
    cy.viewport('ipad-2');

    cy.get('.top-bar').should('be.visible');
    cy.get('.nav-options').should('be.visible');

    // 验证布局合理
    cy.get('.app-title').should('be.visible');
  });
});
