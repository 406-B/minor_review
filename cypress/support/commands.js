// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************

/**
 * 登录命令 - 用于快速登录测试用户
 * @param {string} username - 用户名
 * @param {string} password - 密码
 */
Cypress.Commands.add('login', (username = 'testuser', password = 'password123') => {
  cy.visit('/login');
  cy.get('[data-cy=username-input]').type(username);
  cy.get('[data-cy=password-input]').type(password);
  cy.get('[data-cy=login-button]').click();
  
  // 等待登录成功 - 通常会跳转到首页或显示用户信息
  cy.url().should('not.include', '/login');
  cy.window().its('localStorage.token').should('exist');
});

/**
 * 使用 API 登录 - 更快的登录方式，直接设置 token
 * @param {string} username - 用户名
 * @param {string} password - 密码
 */
Cypress.Commands.add('loginViaAPI', (username = 'testuser', password = 'password123') => {
  cy.request({
    method: 'POST',
    url: '/api/v1/login/',
    body: {
      username,
      password
    }
  }).then((response) => {
    // 假设返回的 token 在 response.body.token 中
    const token = response.body.token || response.body.access_token;
    if (token) {
      window.localStorage.setItem('token', token);
    }
    // 保存用户信息
    if (response.body.user) {
      window.localStorage.setItem('user', JSON.stringify(response.body.user));
    }
  });
});

/**
 * 登出命令
 */
Cypress.Commands.add('logout', () => {
  cy.get('[data-cy=logout-button]').click();
  cy.url().should('include', '/login');
});

/**
 * 等待 API 请求完成
 * @param {string} alias - 请求的别名
 */
Cypress.Commands.add('waitForAPI', (alias) => {
  cy.wait(`@${alias}`).its('response.statusCode').should('be.oneOf', [200, 201, 204]);
});

/**
 * 填写表单字段
 * @param {Object} fields - 字段对象，key 为 data-cy 属性值，value 为要输入的值
 */
Cypress.Commands.add('fillForm', (fields) => {
  Object.keys(fields).forEach((key) => {
    cy.get(`[data-cy=${key}]`).clear().type(fields[key]);
  });
});

/**
 * 检查表单验证错误
 * @param {string} field - 字段的 data-cy 值
 * @param {string} message - 期望的错误消息
 */
Cypress.Commands.add('checkValidationError', (field, message) => {
  cy.get(`[data-cy=${field}-error]`).should('be.visible').and('contain', message);
});

/**
 * 上传文件
 * @param {string} selector - 文件输入的选择器
 * @param {string} fileName - fixtures 文件夹中的文件名
 * @param {string} mimeType - MIME 类型
 */
Cypress.Commands.add('uploadFile', (selector, fileName, mimeType = 'image/jpeg') => {
  cy.fixture(fileName, 'base64').then((fileContent) => {
    cy.get(selector).attachFile({
      fileContent,
      fileName,
      mimeType,
      encoding: 'base64'
    });
  });
});

/**
 * 检查 Toast 消息
 * @param {string} message - 期望的消息内容
 * @param {string} type - 消息类型 (success, error, warning, info)
 */
Cypress.Commands.add('checkToast', (message, type = 'success') => {
  cy.get(`[data-cy=toast-${type}], .toast-${type}, .notification-${type}`)
    .should('be.visible')
    .and('contain', message);
});

/**
 * 等待加载完成
 */
Cypress.Commands.add('waitForLoading', () => {
  cy.get('[data-cy=loading], .loading, .spinner').should('not.exist');
});

/**
 * 模拟移动设备视口
 * @param {string} device - 设备类型 (mobile, tablet)
 */
Cypress.Commands.add('setViewport', (device = 'mobile') => {
  const viewports = {
    mobile: [375, 667],
    tablet: [768, 1024],
    desktop: [1280, 720]
  };
  const [width, height] = viewports[device] || viewports.desktop;
  cy.viewport(width, height);
});

/**
 * 检查元素可访问性（基本检查）
 * @param {string} selector - 元素选择器
 */
Cypress.Commands.add('checkA11y', (selector) => {
  cy.get(selector).should('be.visible').and('not.be.disabled');
});

/**
 * 滚动到元素
 * @param {string} selector - 元素选择器
 */
Cypress.Commands.add('scrollToElement', (selector) => {
  cy.get(selector).scrollIntoView().should('be.visible');
});

/**
 * 拦截并模拟 API 响应
 * @param {string} method - HTTP 方法
 * @param {string} url - API URL 模式
 * @param {Object} fixture - fixture 文件名或响应数据
 * @param {string} alias - 请求别名
 */
Cypress.Commands.add('mockAPI', (method, url, fixture, alias) => {
  cy.intercept(method, url, { fixture }).as(alias);
});
