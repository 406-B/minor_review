/**
 * E2E测试：响应式设计
 * 测试不同设备尺寸下的显示效果
 */

describe('响应式设计测试', () => {
  const viewports = [
    { name: 'mobile', width: 375, height: 667 },
    { name: 'tablet', width: 768, height: 1024 },
    { name: 'desktop', width: 1280, height: 720 },
    { name: 'large-desktop', width: 1920, height: 1080 },
  ];

  viewports.forEach((viewport) => {
    describe(`在 ${viewport.name} (${viewport.width}x${viewport.height}) 设备下`, () => {
      beforeEach(() => {
        cy.viewport(viewport.width, viewport.height);
        cy.visit('/');
      });

      it('页面应该正常显示', () => {
        // 验证页面基本元素可见
        cy.get('header, .header, nav').should('be.visible');
        cy.get('main, .main-content').should('be.visible');
      });

      it('导航栏应该正常工作', () => {
        cy.get('nav, .navbar').should('exist');

        if (viewport.width < 768) {
          // 移动端可能有汉堡菜单
          cy.get('.menu-toggle, .hamburger').should('be.visible');
        }
      });

      it('菜品列表应该适配屏幕', () => {
        cy.get('[data-cy="dish-card"], .dish-card')
          .should('be.visible')
          .first()
          .should('have.css', 'width')
          .and('match', /\d+px/);
      });

      it('图片应该自适应', () => {
        cy.get('img')
          .first()
          .should(($img) => {
            const width = $img.width();
            expect(width).to.be.lessThan(viewport.width);
          });
      });

      it('表单元素应该可用', () => {
        cy.get('input[type="search"], input[type="text"]')
          .first()
          .should('be.visible')
          .should('not.have.css', 'overflow', 'hidden');
      });
    });
  });
});

describe('移动端特定功能', () => {
  beforeEach(() => {
    cy.viewport('iphone-x');
    cy.visit('/');
  });

  it('汉堡菜单应该可以打开和关闭', () => {
    // 查找汉堡菜单按钮
    cy.get('.menu-toggle, .hamburger, [aria-label="menu"]').click({ force: true });

    cy.wait(300);

    // 菜单应该打开
    cy.get('.mobile-menu, .drawer, nav').should('be.visible');

    // 关闭菜单
    cy.get('.menu-toggle, .close-menu').click({ force: true });

    cy.wait(300);
  });

  it('触摸滑动应该工作', () => {
    // 测试横向滑动（如果有轮播图或滑动菜单）
    cy.get('.swiper, .carousel, .slider')
      .first()
      .trigger('touchstart', { touches: [{ clientX: 200, clientY: 100 }] })
      .trigger('touchmove', { touches: [{ clientX: 50, clientY: 100 }] })
      .trigger('touchend');

    cy.wait(300);
  });
});

describe('平板设备特定功能', () => {
  beforeEach(() => {
    cy.viewport('ipad-2');
    cy.visit('/');
  });

  it('应该显示适合平板的布局', () => {
    // 验证多列布局
    cy.get('.dish-grid, .grid')
      .should('have.css', 'display', 'grid')
      .or('have.css', 'display', 'flex');
  });

  it('侧边栏应该正常显示', () => {
    cy.get('.sidebar, aside').should('be.visible');
  });
});

describe('桌面设备特定功能', () => {
  beforeEach(() => {
    cy.viewport(1920, 1080);
    cy.visit('/');
  });

  it('应该显示完整的导航菜单', () => {
    cy.get('nav a, .nav-link').should('have.length.greaterThan', 3);
  });

  it('鼠标悬停效果应该工作', () => {
    cy.get('[data-cy="dish-card"]').first().trigger('mouseover');

    cy.wait(200);

    // 验证悬停效果（比如阴影变化）
    cy.get('[data-cy="dish-card"]').first().should('have.css', 'box-shadow');
  });
});

describe('横竖屏切换', () => {
  it('横屏模式下应该正常显示', () => {
    cy.viewport(667, 375); // 横屏
    cy.visit('/');

    cy.get('header').should('be.visible');
    cy.get('main').should('be.visible');
  });

  it('竖屏模式下应该正常显示', () => {
    cy.viewport(375, 667); // 竖屏
    cy.visit('/');

    cy.get('header').should('be.visible');
    cy.get('main').should('be.visible');
  });
});
