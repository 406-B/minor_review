// ***********************************************************
// This file is processed and loaded automatically before your test files.
//
// You can change the location of this file or turn off automatically serving
// support files with the 'supportFile' configuration option.
//
// You can read more here:
// https://on.cypress.io/configuration
// ***********************************************************

// Import commands.js using ES2015 syntax:
import './commands';

// Alternatively you can use CommonJS syntax:
// require('./commands')

// 全局配置
Cypress.on('uncaught:exception', (err, runnable) => {
  // 返回 false 以防止 Cypress 将未捕获的异常视为失败
  // 在开发中可能会有一些非关键的错误
  return false;
});

// 在每个测试之前清除本地存储和 cookies
beforeEach(() => {
  cy.clearLocalStorage();
  cy.clearCookies();
});
