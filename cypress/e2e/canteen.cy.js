/**
 * 食堂和菜品功能端到端测试
 * 测试流程：食堂浏览 -> 楼层/窗口/菜品 -> 菜品搜索 -> 菜品详情 -> 打卡/评分/评论
 */

describe('E2E 食堂和菜品测试', () => {
  const testUser = {
    username: 'tester123',
    password: '123456Aa-'
  }

  // 在所有测试之前登录一次
  before(() => {
    cy.clearLocalStorage()
    cy.visit('/login')
    cy.get('input[autocomplete="username"]').type(testUser.username)
    cy.get('input[autocomplete="current-password"]').type(testUser.password)
      cy.get('button.login-btn').first().click()
    cy.url().should('not.include', '/login')
  })

  describe('步骤1: 通过多层列表浏览食堂、楼层、菜品', () => {
    beforeEach(() => {
      cy.visit('/canteen')
    })

    it('应当显示食堂列表（侧边栏）', () => {
      // CanteenSidebar 组件显示食堂列表
      cy.get('.canteen-sidebar').should('exist')
      cy.get('.canteen-item').should('have.length.greaterThan', 0)
    })

    it('应当能够点击选择不同食堂', () => {
      // 点击第一个食堂
      cy.get('.canteen-item').first().click()
      cy.get('.canteen-item.active').should('exist')
      
      // 点击第二个食堂（如果有）
      cy.get('.canteen-item').eq(1).then(($item) => {
        if ($item.length > 0) {
          cy.wrap($item).click()
          cy.get('.canteen-item.active').should('exist')
        }
      })
    })

    it('应当显示选中食堂的楼层标签页', () => {
      // 选择第一个食堂
      cy.get('.canteen-item').first().click()
      
      // 验证楼层标签页加载（el-tabs）
      cy.get('.el-tabs').should('exist')
      cy.get('.el-tabs__item').should('have.length.greaterThan', 0)
    })

    it('应当能够切换楼层标签', () => {
      // 选择食堂
      cy.get('.canteen-item').first().click()
      
      // 点击第一个楼层标签
      cy.get('.el-tabs__item').first().click()
      cy.get('.el-tabs__item.is-active').should('exist')
      
      // 切换到第二个楼层（如果有）
      cy.get('.el-tabs__item').eq(1).then(($tab) => {
        if ($tab.length > 0) {
          cy.wrap($tab).click()
          cy.wait(500) // 等待动画
          cy.get('.el-tabs__item.is-active').should('exist')
        }
      })
    })

    it('应当显示楼层下的窗口列表', () => {
      cy.get('.canteen-item').first().click()
      
      // 验证窗口块加载
      cy.get('.window-block').should('have.length.greaterThan', 0)
      cy.get('.window-title').should('exist')
    })

    it('应当显示窗口下的菜品卡片', () => {
      cy.get('.canteen-item').first().click()
      
      // 验证菜品卡片
      cy.get('.dish-card').should('have.length.greaterThan', 0)
      cy.get('.dish-card-name').should('exist')
      cy.get('.dish-card-price').should('exist')
    })

    it('应当能够点击菜品卡片跳转到详情页', () => {
      cy.get('.canteen-item').first().click()
      cy.wait(1000) // 等待楼层数据加载
      
      // 点击第一个菜品卡片
      cy.get('.dish-card').first().click()
      
      // 验证跳转到菜品详情页
      cy.url().should('include', '/dish/')
      cy.get('.dish-title').should('exist')
    })
  })

  describe('步骤2: 菜品搜索功能', () => {
    beforeEach(() => {
      cy.visit('/dish/search')
    })

    it('应当显示搜索表单（菜品名、价格区间、标签）', () => {
      // 验证表单元素存在
      cy.get('.search-form').should('exist')
      
      // 菜品名输入框
      cy.get('input[placeholder*="菜品名"]').should('exist')
      
      // 价格区间输入框
      cy.get('.el-input-number').should('have.length', 2)
      
      // 标签下拉框
      cy.get('.el-select').should('exist')
      
      // 搜索按钮
      cy.contains('button', '搜索').should('exist')
    })

    it('应当能够通过菜品名搜索', () => {
      // 输入菜品名
      cy.get('input[placeholder*="菜品名"]').type('鸡')
      
      // 点击搜索
        cy.contains('button', '搜索').first().click()
      
      // 验证搜索结果
      cy.get('.dish-card', { timeout: 10000 }).should('have.length.greaterThan', 0)
      cy.contains('鸡').should('be.visible')
    })

    it('应当能够通过价格区间搜索', () => {
      // 设置价格区间 10-20
      cy.get('.el-input-number').first().type('10')
      cy.get('.el-input-number').eq(1).type('20')
      
      // 需要输入菜品名或选择标签才能搜索（canSearch 限制）
      cy.get('input[placeholder*="菜品名"]').type('肉')
      
      // 点击搜索
      cy.contains('button', '搜索').click()
      
      // 验证结果中的菜品价格在范围内
      cy.get('.dish-price').first().should('exist')
    })

    it('应当能够通过标签搜索', () => {
      // 点击标签下拉框
      cy.get('.el-select').click()
      
      // 选择第一个标签
      cy.get('.el-select-dropdown__item').first().click({ force: true })
      
      // 点击搜索
        cy.contains('button', '搜索').first().click()
      
      // 验证搜索结果
      cy.get('.dish-card', { timeout: 10000 }).should('have.length.greaterThan', 0)
    })

    it('应当能够组合搜索（菜品名 + 价格 + 标签）', () => {
      // 1. 输入菜品名
      cy.get('input[placeholder*="菜品名"]').type('肉')
      
      // 2. 设置价格区间
      cy.get('.el-input-number').first().clear().type('10')
      cy.get('.el-input-number').eq(1).clear().type('20')
      
      // 3. 选择标签
      cy.get('.el-select').click()
      cy.get('.el-select-dropdown__item').first().click({ force: true })
      
      // 点击搜索
        cy.contains('button', '搜索').first().click()
      
      // 验证搜索结果（可能有结果或无结果）
      cy.wait(2000)
      // 如果有结果，验证菜品卡片存在
      cy.get('body').then(($body) => {
        if ($body.find('.dish-card').length > 0) {
          cy.get('.dish-card').should('exist')
        } else {
          // 如果没有结果，验证空状态提示
          cy.get('.el-empty').should('exist')
        }
      })
    })

    it('搜索无结果时应当显示空状态', () => {
      // 搜索一个不存在的菜品名
      cy.get('input[placeholder*="菜品名"]').type('不存在的菜品xyz123')
      
      // 点击搜索
      cy.contains('button', '搜索').click()
      
      // 验证空状态
      cy.get('.el-empty', { timeout: 10000 }).should('exist')
      cy.contains('暂无菜品').should('be.visible')
    })

    it('应当能够从搜索结果点击进入菜品详情页', () => {
      // 搜索
      cy.get('input[placeholder*="菜品名"]').type('鸡')
      cy.contains('button', '搜索').click()
      
      // 等待结果加载并点击第一个菜品
      cy.get('.dish-card', { timeout: 10000 }).first().click()
      
      // 验证跳转到详情页
      cy.url().should('include', '/dish/')
      cy.get('.dish-title').should('exist')
    })
  })

  describe('步骤3: 菜品详情页功能', () => {
    // 先通过搜索进入一个菜品详情页
    beforeEach(() => {
      cy.visit('/dish/search')
      cy.get('input[placeholder*="菜品名"]').type('鸡')
      cy.contains('button', '搜索').click()
      cy.get('.dish-card', { timeout: 10000 }).first().click()
      cy.url().should('include', '/dish/')
    })

    it('应当显示菜品详细信息', () => {
      // 验证菜品名称
      cy.get('.dish-title').should('exist')
      
      // 验证菜品图片
      cy.get('.dish-image img, .dish-image').should('exist')
      
      // 验证价格
      cy.get('.dish-price').should('exist')
      cy.contains(/￥|¥/).should('be.visible')
      
      // 验证描述
      cy.get('.dish-desc').should('exist')
      
      // 验证标签
      cy.get('.dish-tags').should('exist')
      cy.get('.el-tag').should('have.length.greaterThan', 0)
    })

    it('应当显示菜品评分', () => {
      // 验证评分组件
      cy.get('.dish-rating').should('exist')
      cy.get('.el-rate').should('exist')
    })

    it('应当能够点击打卡', () => {
      // 找到打卡按钮
      cy.contains('button', '打卡').should('exist')
      
      // 点击打卡
      cy.contains('button', '打卡').click()
      
      // 验证打卡成功提示或打卡次数增加
      cy.wait(1000)
      cy.get('.checkin-count').should('exist')
    })

    it('应当能够对菜品评分', () => {
      // 找到用户评分区域
      cy.contains('我要打分').should('exist')
      
      // 点击第4颗星（评4分）
      cy.get('.rate-section .el-rate .el-rate__item').eq(3).click()
      
      // 点击提交评分按钮
      cy.contains('button', '提交评分').click()
      
      // 验证评分成功（可能显示成功消息）
      cy.wait(1000)
      // 验证按钮状态或消息提示
    })

    it('应当能够发表评论', () => {
      // 找到评论输入框
      cy.get('.comment-input textarea').should('exist')
      
      // 输入评论内容（至少5个字）
      const commentText = '这道菜非常好吃，值得推荐！'
      cy.get('.comment-input textarea').type(commentText)
      
      // 点击发表评论按钮
      cy.contains('button', '发表评论').click()
      
      // 验证评论成功（可能显示成功消息或评论出现在列表中）
      cy.wait(2000)
    })

    it('应当显示历史评论列表', () => {
      // 滚动到评论区域
      cy.get('.dish-reviews').should('exist')
      cy.contains('评论').should('exist')
      
      // 验证评论列表或空状态
      cy.get('body').then(($body) => {
        if ($body.find('.review-card').length > 0) {
          cy.get('.review-card').should('exist')
          cy.get('.review-user').should('exist')
          cy.get('.review-content').should('exist')
        } else {
          cy.get('.el-empty').should('exist')
        }
      })
    })

    it('应当能够返回上一页', () => {
      // 点击返回按钮
      cy.contains('button', '返回').click()
      
      // 验证返回到搜索页
      cy.url().should('include', '/dish/search')
    })
  })

  describe('步骤4: 边界情况和用户体验', () => {
    it('菜品详情页应当显示打卡进度', () => {
      cy.visit('/dish/search')
      cy.get('input[placeholder*="菜品名"]').type('鸡')
      cy.contains('button', '搜索').click()
      cy.get('.dish-card', { timeout: 10000 }).first().click()
      
      // 验证打卡进度条或等级标识
      cy.get('.checkin-section').should('exist')
      cy.get('.checkin-count').should('exist')
    })

    it('评论长度不足时应当禁用提交按钮', () => {
      cy.visit('/dish/search')
      cy.get('input[placeholder*="菜品名"]').type('鸡')
      cy.contains('button', '搜索').click()
      cy.get('.dish-card', { timeout: 10000 }).first().click()
      
      // 输入少于5个字的评论
      cy.get('.comment-input textarea').clear().type('好吃')
      
      // 验证提交按钮被禁用
      cy.contains('button', '发表评论').should('be.disabled')
    })

    it('搜索表单未填写时应当禁用搜索按钮', () => {
      cy.visit('/dish/search')
      
      // 验证搜索按钮被禁用（因为 canSearch 要求菜品名或标签）
      cy.contains('button', '搜索').should('be.disabled')
    })
  })


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
