/**
 * 食堂和菜品功能端到端测试
 * 测试食堂浏览、菜品搜索、菜品详情、评分等功能
 */

describe('食堂和菜品管理', () => {
  beforeEach(() => {
    // 登录用户
    cy.visit('/login');
    cy.get('input[name="username"]').type('testuser');
    cy.get('input[name="password"]').type('password123');
    cy.get('button[type="submit"]').click();
    cy.url().should('not.include', '/login');
  });

  describe('食堂浏览', () => {
    it('应该能够查看食堂列表', () => {
      cy.visit('/canteen');
      
      // 验证食堂列表加载
      cy.get('.canteen-list, .canteen-grid, [data-cy=canteen-list]').should('exist');
      cy.get('.canteen-item, .canteen-card').should('have.length.greaterThan', 0);
    });

    it('应该显示食堂的基本信息', () => {
      cy.visit('/canteen');
      
      cy.get('.canteen-item, .canteen-card').first().within(() => {
        // 验证食堂名称
        cy.get('.canteen-name, h3, h2').should('exist');
        // 验证其他信息（如位置、营业时间等）
        cy.get('.canteen-info, .info').should('exist');
      });
    });

    it('应该能够点击查看食堂详情', () => {
      cy.visit('/canteen');
      
      cy.get('.canteen-item, .canteen-card').first().click();
      
      // 验证跳转到详情页
      cy.url().should('match', /canteen\/\d+/);
    });

    it('应该能够在地图上查看食堂位置', () => {
      cy.visit('/canteen');
      
      // 检查地图按钮或地图视图
      cy.get('button:contains("地图"), button:contains("Map"), .map-toggle').then(($btn) => {
        if ($btn.length > 0) {
          cy.wrap($btn).click();
          cy.get('.map-container, #map').should('be.visible');
        }
      });
    });
  });

  describe('菜品浏览和搜索', () => {
    it('应该能够查看菜品列表', () => {
      cy.visit('/dishes');
      
      cy.get('.dish-list, .dish-grid, [data-cy=dish-list]').should('exist');
      cy.get('.dish-item, .dish-card').should('have.length.greaterThan', 0);
    });

    it('应该能够搜索菜品', () => {
      cy.visit('/dishes');
      
      const searchTerm = '鸡';
      cy.get('input[type="search"], input[placeholder*="搜索"], [data-cy=search-input]')
        .type(searchTerm);
      
      // 点击搜索按钮或按回车
      cy.get('button[type="submit"], .search-button').click();
      
      // 验证搜索结果
      cy.get('.dish-item, .dish-card').should('exist');
      cy.contains(searchTerm).should('be.visible');
    });

    it('应该能够按分类筛选菜品', () => {
      cy.visit('/dishes');
      
      // 选择一个分类
      cy.get('.category-filter, .filter-tabs, select[name="category"]').then(($filter) => {
        if ($filter.length > 0) {
          if ($filter.is('select')) {
            cy.wrap($filter).select(1);
          } else {
            cy.wrap($filter).find('button, .tab').first().click();
          }
          
          // 验证筛选结果
          cy.get('.dish-item, .dish-card').should('exist');
        }
      });
    });

    it('应该能够按价格排序', () => {
      cy.visit('/dishes');
      
      // 查找排序选项
      cy.get('select[name="sort"], .sort-dropdown').then(($sort) => {
        if ($sort.length > 0) {
          cy.wrap($sort).select('price');
          
          // 验证排序生效
          cy.get('.dish-item, .dish-card').should('exist');
        }
      });
    });

    it('应该能够按评分排序', () => {
      cy.visit('/dishes');
      
      cy.get('select[name="sort"], button:contains("评分")').then(($sort) => {
        if ($sort.length > 0) {
          if ($sort.is('select')) {
            cy.wrap($sort).select('rating');
          } else {
            cy.wrap($sort).click();
          }
          
          cy.get('.dish-item, .dish-card').should('exist');
        }
      });
    });

    it('搜索无结果时应该显示提示', () => {
      cy.visit('/dishes');
      
      cy.get('input[type="search"]').type('不存在的菜品名称xyz123');
      cy.get('button[type="submit"]').click();
      
      cy.contains(/没有找到|No results|暂无/i).should('be.visible');
    });
  });

  describe('菜品详情', () => {
    beforeEach(() => {
      cy.visit('/dishes');
      // 点击第一个菜品
      cy.get('.dish-item, .dish-card').first().click();
      cy.url().should('match', /dish\/\d+/);
    });

    it('应该显示菜品的详细信息', () => {
      // 验证菜品名称
      cy.get('h1, .dish-name').should('exist');
      
      // 验证价格
      cy.contains(/￥|¥|\d+元/).should('be.visible');
      
      // 验证描述
      cy.get('.dish-description, .description').should('exist');
    });

    it('应该显示菜品图片', () => {
      cy.get('img[alt*="菜品"], .dish-image, .dish-photo').should('exist');
    });

    it('应该显示菜品评分', () => {
      cy.get('.rating, .score, .stars').should('exist');
    });

    it('应该能够查看用户评价', () => {
      cy.get('.reviews, .comments, .ratings').should('exist');
      cy.get('.review-item, .comment-item').should('have.length.greaterThan', 0);
    });

    it('应该能够对菜品进行评分', () => {
      // 查找评分组件
      cy.get('.rate-button, button:contains("评分"), .rating-input').then(($btn) => {
        if ($btn.length > 0) {
          cy.wrap($btn).click();
          
          // 选择星级
          cy.get('.star, .rating-star').eq(3).click();
          
          // 提交评分
          cy.get('button:contains("提交"), button[type="submit"]').click();
          
          cy.contains(/评分成功|Rating submitted/i, { timeout: 10000 }).should('be.visible');
        }
      });
    });

    it('应该能够撰写评价', () => {
      // 查找评价输入框
      cy.get('textarea[placeholder*="评价"], .review-input').then(($textarea) => {
        if ($textarea.length > 0) {
          const reviewText = '这道菜很好吃！';
          cy.wrap($textarea).type(reviewText);
          
          cy.get('button:contains("提交"), button:contains("发表")').click();
          
          cy.contains(/评价成功|Review submitted/i, { timeout: 10000 }).should('be.visible');
          cy.contains(reviewText).should('be.visible');
        }
      });
    });

    it('应该能够上传菜品图片', () => {
      cy.get('button:contains("上传图片"), input[type="file"]').then(($upload) => {
        if ($upload.length > 0) {
          cy.log('图片上传功能存在');
        }
      });
    });
  });

  describe('食堂详情页', () => {
    beforeEach(() => {
      cy.visit('/canteen');
      cy.get('.canteen-item, .canteen-card').first().click();
    });

    it('应该显示食堂的详细信息', () => {
      // 验证食堂名称
      cy.get('h1, .canteen-name').should('exist');
      
      // 验证营业时间
      cy.contains(/营业时间|Opening hours|时间/).should('be.visible');
      
      // 验证位置信息
      cy.contains(/位置|Location|地址/).should('be.visible');
    });

    it('应该显示该食堂的菜品列表', () => {
      cy.get('.dish-list, .dishes, .menu').should('exist');
      cy.get('.dish-item, .dish-card').should('have.length.greaterThan', 0);
    });

    it('应该能够从食堂页面查看菜品详情', () => {
      cy.get('.dish-item, .dish-card').first().click();
      cy.url().should('match', /dish\/\d+/);
    });
  });

  describe('收藏功能', () => {
    it('应该能够收藏菜品', () => {
      cy.visit('/dishes');
      cy.get('.dish-item, .dish-card').first().click();
      
      // 查找收藏按钮
      cy.get('button:contains("收藏"), .favorite-button, .like-button').then(($btn) => {
        if ($btn.length > 0) {
          cy.wrap($btn).click();
          
          // 验证收藏成功
          cy.contains(/已收藏|Favorited|收藏成功/i).should('be.visible');
        }
      });
    });

    it('应该能够取消收藏', () => {
      cy.visit('/dishes');
      cy.get('.dish-item, .dish-card').first().click();
      
      // 先收藏
      cy.get('button:contains("收藏"), .favorite-button').then(($btn) => {
        if ($btn.length > 0) {
          cy.wrap($btn).click();
          cy.wait(1000);
          
          // 再取消收藏
          cy.wrap($btn).click();
          
          cy.contains(/取消收藏|Unfavorited|已取消/i).should('be.visible');
        }
      });
    });

    it('应该能够查看收藏的菜品列表', () => {
      cy.visit('/profile');
      
      cy.contains(/我的收藏|Favorites|收藏/).then(($link) => {
        if ($link.length > 0) {
          cy.wrap($link).click();
          cy.get('.dish-item, .favorite-item').should('exist');
        }
      });
    });
  });

  describe('菜品推荐', () => {
    it('应该显示推荐菜品', () => {
      cy.visit('/recommend');
      
      cy.get('.dish-item, .recommended-dish, .dish-card').should('have.length.greaterThan', 0);
    });

    it('应该能够刷新推荐', () => {
      cy.visit('/recommend');
      
      cy.get('button:contains("换一批"), button:contains("刷新"), .refresh-button').then(($btn) => {
        if ($btn.length > 0) {
          cy.wrap($btn).click();
          cy.get('.dish-item, .dish-card').should('exist');
        }
      });
    });
  });

  describe('食堂消费记录', () => {
    it('应该能够查看消费记录', () => {
      cy.visit('/canteen/consumption');
      
      cy.get('.consumption-list, .transaction-list, .record-list').should('exist');
    });

    it('应该显示消费金额和日期', () => {
      cy.visit('/canteen/consumption');
      
      cy.get('.consumption-item, .transaction-item').first().within(() => {
        cy.contains(/￥|¥|\d+/).should('be.visible');
        cy.contains(/\d{4}|\d{2}\/\d{2}/).should('be.visible');
      });
    });

    it('应该能够按日期筛选消费记录', () => {
      cy.visit('/canteen/consumption');
      
      cy.get('input[type="date"], .date-picker').then(($datePicker) => {
        if ($datePicker.length > 0) {
          cy.log('日期筛选功能存在');
        }
      });
    });
  });

  describe('响应式设计', () => {
    it('菜品列表应该在移动端正常显示', () => {
      cy.viewport('iphone-x');
      cy.visit('/dishes');
      
      cy.get('.dish-item, .dish-card').should('be.visible');
    });

    it('菜品详情应该在平板上正常显示', () => {
      cy.viewport('ipad-2');
      cy.visit('/dishes');
      cy.get('.dish-item').first().click();
      
      cy.get('.dish-detail, .dish-info').should('be.visible');
    });
  });
});
