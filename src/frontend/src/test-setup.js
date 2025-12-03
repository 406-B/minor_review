/**
 * 测试环境设置
 * 在所有测试运行前执行
 */

import { vi } from 'vitest';
import { config } from '@vue/test-utils';

// 设置全局 mocks
global.console = {
  ...console,
  error: vi.fn(),
  warn: vi.fn(),
};

// 配置 Vue Test Utils
config.global.mocks = {
  $t: (key) => key, // 模拟国际化
  $router: {
    push: vi.fn(),
    replace: vi.fn(),
  },
  $route: {
    params: {},
    query: {},
  },
};

// 模拟 window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation((query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

// 模拟 IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  takeRecords() {
    return [];
  }
  unobserve() {}
};
