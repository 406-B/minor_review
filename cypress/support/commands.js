/**
 * Cypress 自定义命令
 * 用于简化测试代码
 */

// 登录命令
Cypress.Commands.add('login', (username, password) => {
  cy.session([username, password], () => {
    cy.visit('/login');
    cy.get('input[name="username"]').type(username);
    cy.get('input[type="password"]').type(password);
    cy.contains('button', '登录').click();
    cy.wait(1000);
    // 验证登录成功
    cy.url().should('not.include', '/login');
  });
});

// 登出命令
Cypress.Commands.add('logout', () => {
  cy.get('[data-cy="user-menu"]').click();
  cy.contains('登出').click();
  cy.wait(500);
});

// 访问菜品详情
Cypress.Commands.add('visitDish', (dishId) => {
  cy.visit(`/dish/${dishId}`);
  cy.wait(500);
});

// 搜索菜品
Cypress.Commands.add('searchDish', (keyword) => {
  cy.get('input[type="search"]').first().clear().type(keyword);
  cy.get('input[type="search"]').first().type('{enter}');
  cy.wait(1000);
});

// 给菜品评分
Cypress.Commands.add('rateDish', (rating) => {
  cy.get(`[data-cy="rating-star-${rating}"]`).click({ force: true });
  cy.wait(500);
});

// 提交评论
Cypress.Commands.add('submitReview', (content, options = {}) => {
  cy.get('textarea[name="content"]').first().clear().type(content);

  if (options.rating) {
    cy.rateDish(options.rating);
  }

  if (options.images) {
    options.images.forEach((image) => {
      cy.get('input[type="file"]').attachFile(image);
    });
  }

  cy.contains('button', /提交|发表/).click({ force: true });
  cy.wait(1000);
});

// 检查元素是否在视口中
Cypress.Commands.add('isInViewport', { prevSubject: true }, (subject) => {
  const rect = subject[0].getBoundingClientRect();

  expect(rect.top).to.be.at.least(0);
  expect(rect.left).to.be.at.least(0);
  expect(rect.bottom).to.be.at.most(Cypress.config('viewportHeight'));
  expect(rect.right).to.be.at.most(Cypress.config('viewportWidth'));

  return subject;
});

// 等待 API 请求完成
Cypress.Commands.add('waitForApi', (alias, timeout = 5000) => {
  cy.wait(alias, { timeout });
});

// 模拟 API 响应
Cypress.Commands.add('mockApi', (method, url, response, statusCode = 200) => {
  cy.intercept(method, url, {
    statusCode,
    body: response,
  }).as('mockRequest');
});

// 检查 toast 消息
Cypress.Commands.add('checkToast', (message) => {
  cy.contains('.toast, .message, .notification', message, { timeout: 3000 }).should('be.visible');
});

// 清除 localStorage
Cypress.Commands.add('clearStorage', () => {
  cy.clearLocalStorage();
  cy.clearCookies();
});

// 设置视口并访问页面
Cypress.Commands.add('visitWithViewport', (url, width, height) => {
  cy.viewport(width, height);
  cy.visit(url);
});
