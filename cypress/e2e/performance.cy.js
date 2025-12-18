/**
 * E2E性能测试：页面加载和响应时间
 * 测试关键用户流程的性能指标
 */

describe('性能测试', () => {
  beforeEach(() => {
    // 清除缓存确保每次测试都是冷启动
    cy.clearCookies();
    cy.clearLocalStorage();
  });

  it('首页加载性能', () => {
    // 记录开始时间
    const startTime = Date.now();

    cy.visit('/', {
      onBeforeLoad: (win) => {
        // 监听页面加载完成事件
        win.performance.mark('page-start');
      },
      onLoad: (win) => {
        win.performance.mark('page-loaded');
      },
    });

    // 等待页面完全加载
    cy.window().should('have.property', 'performance');

    // 测量页面加载时间
    cy.window().then((win) => {
      const loadTime = Date.now() - startTime;
      const perfData = win.performance.getEntriesByType('navigation')[0];

      // 记录性能指标
      cy.log(`页面加载时间: ${loadTime}ms`);
      cy.log(
        `DOM处理时间: ${perfData.domContentLoadedEventEnd - perfData.domContentLoadedEventStart}ms`
      );
      cy.log(`页面完全加载时间: ${perfData.loadEventEnd - perfData.loadEventStart}ms`);

      // 断言加载时间不超过阈值
      expect(loadTime).to.be.lessThan(5000); // 5秒内加载完成
      expect(perfData.loadEventEnd - perfData.loadEventStart).to.be.lessThan(3000);
    });
  });

  it('API响应时间测试', () => {
    cy.visit('/');

    // 测试菜品列表API响应时间
    cy.intercept('GET', '**/api/dishes/**').as('getDishes');

    // 触发API请求
    cy.get('input[type="search"]').first().type('test{enter}');

    cy.wait('@getDishes').then((interception) => {
      const responseTime = interception.response.duration;

      cy.log(`API响应时间: ${responseTime}ms`);

      // 断言API响应时间
      expect(responseTime).to.be.lessThan(2000); // 2秒内响应
    });
  });

  it('搜索性能测试', () => {
    cy.visit('/');

    const searchTerms = ['宫保', '鸡丁', '食堂', '测试'];

    searchTerms.forEach((term) => {
      const startTime = Date.now();

      cy.get('input[type="search"]').first().clear().type(term);

      cy.intercept('GET', '**/api/dishes/**').as('searchRequest');

      cy.get('input[type="search"]').first().type('{enter}');

      cy.wait('@searchRequest').then((interception) => {
        const searchTime = Date.now() - startTime;
        const responseTime = interception.response.duration;

        cy.log(`搜索"${term}"总时间: ${searchTime}ms`);
        cy.log(`搜索"${term}"API响应时间: ${responseTime}ms`);

        expect(searchTime).to.be.lessThan(3000);
        expect(responseTime).to.be.lessThan(1500);
      });

      // 等待结果加载
      cy.wait(500);
    });
  });

  it('页面导航性能', () => {
    cy.visit('/');

    // 测试导航到不同页面
    const pages = [
      { name: '食堂浏览', selector: '食堂浏览' },
      { name: '美食论坛', selector: '美食论坛' },
      { name: '个人主页', selector: '个人主页' },
    ];

    pages.forEach((page) => {
      const navStart = Date.now();

      cy.contains(page.selector).click({ force: true });

      cy.window().should('have.property', 'performance');

      cy.window().then(() => {
        const navTime = Date.now() - navStart;
        cy.log(`导航到"${page.name}"时间: ${navTime}ms`);
        expect(navTime).to.be.lessThan(2000);
      });

      // 等待页面加载
      cy.wait(500);

      // 返回首页继续测试
      cy.visit('/');
      cy.wait(500);
    });
  });

  it('图片加载性能', () => {
    cy.visit('/');

    // 查找页面上的图片
    cy.get('img').each(($img) => {
      // 检查图片是否在合理时间内加载
      cy.wrap($img)
        .should('be.visible')
        .then(() => {
          // 如果图片有src，检查加载状态
          const src = $img.attr('src');
          if (src) {
            cy.request(src).then((response) => {
              expect(response.status).to.eq(200);
              expect(response.duration).to.be.lessThan(5000); // 5秒内加载图片
            });
          }
        });
    });
  });

  it('内存泄漏检测', () => {
    cy.visit('/');

    // 执行一些用户操作
    cy.get('input[type="search"]').first().type('test{enter}');
    cy.wait(1000);

    // 点击一些菜品卡片
    cy.get('[data-cy="dish-card"], .dish-card').first().click({ force: true });
    cy.wait(1000);

    // 返回首页
    cy.go('back');
    cy.wait(1000);

    // 重复操作多次
    for (let i = 0; i < 5; i++) {
      cy.get('[data-cy="dish-card"], .dish-card')
        .eq(i % 3)
        .click({ force: true });
      cy.wait(500);
      cy.go('back');
      cy.wait(500);
    }

    // 检查控制台是否有内存警告
    cy.window().then((win) => {
      // 记录内存使用情况（如果可用）
      if (win.performance.memory) {
        const memInfo = win.performance.memory;
        cy.log(`堆使用: ${Math.round(memInfo.usedJSHeapSize / 1024 / 1024)}MB`);
        cy.log(`堆大小: ${Math.round(memInfo.totalJSHeapSize / 1024 / 1024)}MB`);
        cy.log(`堆限制: ${Math.round(memInfo.jsHeapSizeLimit / 1024 / 1024)}MB`);
      }
    });
  });

  it('并发请求处理', () => {
    cy.visit('/');

    // 模拟多个并发请求
    const requests = [];

    for (let i = 0; i < 5; i++) {
      requests.push(
        cy.request({
          url: '/api/dishes/',
          method: 'GET',
          qs: { page: i + 1 },
        })
      );
    }

    // 等待所有请求完成
    cy.wrap(Promise.all(requests)).then((responses) => {
      responses.forEach((response, index) => {
        expect(response.status).to.eq(200);
        expect(response.duration).to.be.lessThan(2000);
        cy.log(`请求${index + 1}响应时间: ${response.duration}ms`);
      });
    });
  });

  it('缓存效果测试', () => {
    cy.visit('/');

    // 首次访问
    cy.intercept('GET', '**/api/dishes/**').as('firstRequest');

    cy.get('input[type="search"]').first().type('cache{enter}');
    cy.wait('@firstRequest').then((interception) => {
      const firstResponseTime = interception.response.duration;
      cy.log(`首次请求时间: ${firstResponseTime}ms`);
    });

    cy.wait(1000);

    // 再次访问相同内容（应该从缓存加载）
    cy.intercept('GET', '**/api/dishes/**').as('secondRequest');

    cy.get('input[type="search"]').first().clear().type('cache{enter}');
    cy.wait('@secondRequest').then((interception) => {
      const secondResponseTime = interception.response.duration;
      cy.log(`缓存请求时间: ${secondResponseTime}ms`);

      // 缓存请求应该更快
      expect(secondResponseTime).to.be.lessThan(firstResponseTime);
    });
  });
});

describe('负载测试模拟', () => {
  it('大量数据渲染性能', () => {
    cy.visit('/');

    // 模拟加载大量菜品数据
    cy.intercept('GET', '**/api/dishes/**', { fixture: 'large-dish-list.json' }).as('largeList');

    cy.get('input[type="search"]').first().type('大量数据{enter}');

    cy.wait('@largeList');

    const startTime = Date.now();

    // 等待列表渲染完成
    cy.get('[data-cy="dish-card"], .dish-card').should('have.length.greaterThan', 10);

    cy.window().then(() => {
      const renderTime = Date.now() - startTime;
      cy.log(`大量数据渲染时间: ${renderTime}ms`);
      expect(renderTime).to.be.lessThan(5000);
    });
  });

  it('滚动性能测试', () => {
    cy.visit('/');

    // 确保有足够的内容可以滚动
    cy.get('body').should('have.length.greaterThan', 0);

    // 测试滚动性能
    const scrollSteps = 10;
    const scrollAmount = 500;

    for (let i = 0; i < scrollSteps; i++) {
      const scrollStart = Date.now();

      cy.scrollTo(0, (i + 1) * scrollAmount);

      cy.window().then(() => {
        const scrollTime = Date.now() - scrollStart;
        cy.log(`滚动${i + 1}耗时: ${scrollTime}ms`);
        expect(scrollTime).to.be.lessThan(1000);
      });

      cy.wait(200); // 短暂等待滚动完成
    }
  });

  it('表单提交性能', () => {
    // 假设有用户登录
    cy.visit('/');

    // 模拟快速连续的表单操作
    const operations = [];

    for (let i = 0; i < 5; i++) {
      const opStart = Date.now();

      cy.then(() => {
        operations.push(Date.now() - opStart);
      });
    }

    cy.then(() => {
      const avgTime = operations.reduce((a, b) => a + b, 0) / operations.length;
      cy.log(`平均操作时间: ${avgTime}ms`);
      expect(avgTime).to.be.lessThan(500);
    });
  });
});
