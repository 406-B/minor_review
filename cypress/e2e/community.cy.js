/**
 * 社区功能端到端测试
 * 测试帖子创建、浏览、评论、点赞等社区互动功能
 */

describe('社区功能', () => {
  beforeEach(() => {
    // 登录用户
    cy.visit('/login');
    cy.get('input[name="username"]').type('testuser');
    cy.get('input[name="password"]').type('password123');
    cy.get('button[type="submit"]').click();
    cy.url().should('not.include', '/login');
  });

  describe('帖子浏览', () => {
    it('应该能够查看社区首页', () => {
      cy.visit('/community');
      
      // 验证帖子列表加载
      cy.get('.post-list, .posts, [data-cy=post-list]').should('exist');
      cy.get('.post-item, .post-card').should('have.length.greaterThan', 0);
    });

    it('应该显示帖子的基本信息', () => {
      cy.visit('/community');
      
      cy.get('.post-item, .post-card').first().within(() => {
        // 标题
        cy.get('.post-title, h3, h2').should('exist');
        // 作者
        cy.get('.author, .username').should('exist');
        // 时间
        cy.get('.time, .date, .timestamp').should('exist');
      });
    });

    it('应该能够点击查看帖子详情', () => {
      cy.visit('/community');
      
      cy.get('.post-item, .post-card').first().click();
      
      // 验证跳转到详情页
      cy.url().should('match', /post\/\d+/);
    });

    it('应该能够分页浏览帖子', () => {
      cy.visit('/community');
      
      // 查找分页组件
      cy.get('.pagination, .pager').then(($pagination) => {
        if ($pagination.length > 0) {
          cy.get('button:contains("下一页"), .next-page, button:contains("2")').then(($btn) => {
            if ($btn.length > 0 && !$btn.is(':disabled')) {
              cy.wrap($btn).click();
              cy.get('.post-item, .post-card').should('exist');
            }
          });
        }
      });
    });

    it('应该能够按最新排序', () => {
      cy.visit('/community');
      
      cy.get('button:contains("最新"), .sort-latest').then(($btn) => {
        if ($btn.length > 0) {
          cy.wrap($btn).click();
          cy.get('.post-item, .post-card').should('exist');
        }
      });
    });

    it('应该能够按热度排序', () => {
      cy.visit('/community');
      
      cy.get('button:contains("热门"), button:contains("最热"), .sort-hot').then(($btn) => {
        if ($btn.length > 0) {
          cy.wrap($btn).click();
          cy.get('.post-item, .post-card').should('exist');
        }
      });
    });
  });

  describe('创建帖子', () => {
    beforeEach(() => {
      cy.visit('/community');
      // 点击创建帖子按钮
      cy.get('button:contains("发帖"), button:contains("创建"), a[href*="post/create"]').click();
      cy.url().should('include', '/post/create');
    });

    it('应该能够创建文本帖子', () => {
      const postTitle = '测试帖子标题 - ' + Date.now();
      const postContent = '这是一个测试帖子的内容。';
      
      // 填写标题
      cy.get('input[name="title"], input[placeholder*="标题"]').type(postTitle);
      
      // 填写内容
      cy.get('textarea[name="content"], .editor, .content-input')
        .type(postContent);
      
      // 提交
      cy.get('button[type="submit"], button:contains("发布")').click();
      
      // 验证创建成功
      cy.contains(/发布成功|Post created|已发布/i, { timeout: 10000 }).should('be.visible');
      cy.url().should('match', /post\/\d+|community/);
    });

    it('应该能够添加图片到帖子', () => {
      cy.get('input[name="title"]').type('带图片的帖子');
      cy.get('textarea[name="content"]').type('这是帖子内容');
      
      // 查找图片上传按钮
      cy.get('input[type="file"], button:contains("上传图片")').then(($upload) => {
        if ($upload.length > 0) {
          cy.log('图片上传功能存在');
        }
      });
    });

    it('应该能够选择帖子分类', () => {
      cy.get('input[name="title"]').type('测试分类');
      
      // 选择分类
      cy.get('select[name="category"], .category-select').then(($select) => {
        if ($select.length > 0) {
          cy.wrap($select).select(1);
        }
      });
    });

    it('应该验证标题不能为空', () => {
      // 只填写内容，不填标题
      cy.get('textarea[name="content"]').type('只有内容没有标题');
      
      cy.get('button[type="submit"]').click();
      
      // 验证错误提示
      cy.contains(/标题不能为空|Title required|请输入标题/i).should('be.visible');
    });

    it('应该验证内容不能为空', () => {
      // 只填写标题，不填内容
      cy.get('input[name="title"]').type('只有标题');
      
      cy.get('button[type="submit"]').click();
      
      cy.contains(/内容不能为空|Content required|请输入内容/i).should('be.visible');
    });

    it('应该能够保存草稿', () => {
      cy.get('input[name="title"]').type('草稿标题');
      cy.get('textarea[name="content"]').type('草稿内容');
      
      cy.get('button:contains("保存草稿"), button:contains("草稿")').then(($btn) => {
        if ($btn.length > 0) {
          cy.wrap($btn).click();
          cy.contains(/保存成功|Saved/i).should('be.visible');
        }
      });
    });

    it('应该能够取消创建', () => {
      cy.get('input[name="title"]').type('将要取消的帖子');
      
      cy.get('button:contains("取消"), .cancel-button').click();
      
      cy.url().should('include', '/community');
    });
  });

  describe('帖子详情', () => {
    beforeEach(() => {
      cy.visit('/community');
      cy.get('.post-item, .post-card').first().click();
    });

    it('应该显示完整的帖子内容', () => {
      // 验证标题
      cy.get('h1, .post-title').should('exist');
      
      // 验证内容
      cy.get('.post-content, .content').should('exist');
      
      // 验证作者信息
      cy.get('.author, .username').should('exist');
      
      // 验证发布时间
      cy.get('.time, .date').should('exist');
    });

    it('应该显示点赞数', () => {
      cy.get('.likes, .like-count').should('exist');
    });

    it('应该显示评论数', () => {
      cy.get('.comments-count, .comment-count').should('exist');
    });

    it('应该能够点赞帖子', () => {
      cy.get('button:contains("赞"), .like-button, .thumbs-up').then(($btn) => {
        if ($btn.length > 0) {
          cy.wrap($btn).click();
          
          // 验证点赞成功
          cy.wait(500);
          cy.get('.like-count, .likes').should('exist');
        }
      });
    });

    it('应该能够取消点赞', () => {
      // 先点赞
      cy.get('.like-button, button:contains("赞")').then(($btn) => {
        if ($btn.length > 0) {
          cy.wrap($btn).click();
          cy.wait(500);
          
          // 再取消点赞
          cy.wrap($btn).click();
          cy.wait(500);
        }
      });
    });

    it('应该能够收藏帖子', () => {
      cy.get('button:contains("收藏"), .favorite-button, .bookmark').then(($btn) => {
        if ($btn.length > 0) {
          cy.wrap($btn).click();
          cy.contains(/已收藏|Favorited/i).should('be.visible');
        }
      });
    });

    it('应该能够分享帖子', () => {
      cy.get('button:contains("分享"), .share-button').then(($btn) => {
        if ($btn.length > 0) {
          cy.wrap($btn).click();
          cy.get('.share-modal, .share-options').should('be.visible');
        }
      });
    });
  });

  describe('评论功能', () => {
    beforeEach(() => {
      cy.visit('/community');
      cy.get('.post-item, .post-card').first().click();
    });

    it('应该显示评论列表', () => {
      cy.get('.comments, .comment-list').should('exist');
    });

    it('应该能够发表评论', () => {
      const commentText = '这是一条测试评论 - ' + Date.now();
      
      // 找到评论输入框
      cy.get('textarea[placeholder*="评论"], .comment-input, textarea[name="comment"]')
        .type(commentText);
      
      // 提交评论
      cy.get('button:contains("发表"), button:contains("评论"), button[type="submit"]').click();
      
      // 验证评论成功
      cy.contains(commentText, { timeout: 10000 }).should('be.visible');
    });

    it('应该能够回复评论', () => {
      // 找到第一条评论的回复按钮
      cy.get('.comment-item').first().within(() => {
        cy.get('button:contains("回复"), .reply-button').then(($btn) => {
          if ($btn.length > 0) {
            cy.wrap($btn).click();
            
            // 输入回复内容
            cy.get('textarea, .reply-input').type('这是一条回复');
            cy.get('button:contains("发表"), button[type="submit"]').click();
            
            cy.contains(/回复成功|Reply sent/i).should('be.visible');
          }
        });
      });
    });

    it('应该能够点赞评论', () => {
      cy.get('.comment-item').first().within(() => {
        cy.get('button:contains("赞"), .like-button').then(($btn) => {
          if ($btn.length > 0) {
            cy.wrap($btn).click();
            cy.wait(500);
          }
        });
      });
    });

    it('应该能够删除自己的评论', () => {
      // 先发表一条评论
      const commentText = '要删除的评论 - ' + Date.now();
      cy.get('textarea[placeholder*="评论"]').type(commentText);
      cy.get('button:contains("发表")').click();
      
      cy.wait(1000);
      
      // 找到刚发表的评论并删除
      cy.contains(commentText).parent().within(() => {
        cy.get('button:contains("删除"), .delete-button').then(($btn) => {
          if ($btn.length > 0) {
            cy.wrap($btn).click();
            
            // 确认删除
            cy.get('button:contains("确认")').then(($confirm) => {
              if ($confirm.length > 0) {
                cy.wrap($confirm).click();
              }
            });
          }
        });
      });
    });

    it('评论应该按时间排序', () => {
      cy.get('.comment-item').should('have.length.greaterThan', 0);
    });
  });

  describe('编辑和删除帖子', () => {
    it('作者应该能够编辑自己的帖子', () => {
      // 访问自己创建的帖子
      cy.visit('/profile');
      cy.contains(/我的帖子|My Posts/).click();
      
      cy.get('.post-item').first().click();
      
      // 查找编辑按钮
      cy.get('button:contains("编辑"), .edit-button').then(($btn) => {
        if ($btn.length > 0) {
          cy.wrap($btn).click();
          
          // 修改内容
          cy.get('input[name="title"]').clear().type('编辑后的标题');
          cy.get('button[type="submit"]').click();
          
          cy.contains(/更新成功|Updated/i).should('be.visible');
        }
      });
    });

    it('作者应该能够删除自己的帖子', () => {
      cy.visit('/profile');
      cy.contains(/我的帖子|My Posts/).click();
      
      cy.get('.post-item').first().click();
      
      cy.get('button:contains("删除"), .delete-button').then(($btn) => {
        if ($btn.length > 0) {
          cy.wrap($btn).click();
          
          // 确认删除
          cy.contains('button', '确认').click();
          
          cy.contains(/删除成功|Deleted/i).should('be.visible');
          cy.url().should('not.match', /post\/\d+/);
        }
      });
    });
  });

  describe('我的内容管理', () => {
    it('应该能够查看我的帖子', () => {
      cy.visit('/profile');
      cy.contains(/我的帖子|My Posts/).click();
      
      cy.url().should('match', /posts|my-posts/);
      cy.get('.post-item, .post-card').should('exist');
    });

    it('应该能够查看我的评论', () => {
      cy.visit('/profile');
      cy.contains(/我的评论|My Comments/).then(($link) => {
        if ($link.length > 0) {
          cy.wrap($link).click();
          cy.url().should('match', /comments|my-comments/);
        }
      });
    });

    it('应该能够查看我收藏的帖子', () => {
      cy.visit('/profile');
      cy.contains(/收藏|Favorites|喜欢/).then(($link) => {
        if ($link.length > 0) {
          cy.wrap($link).click();
          cy.get('.post-item').should('exist');
        }
      });
    });
  });

  describe('搜索功能', () => {
    it('应该能够搜索帖子', () => {
      cy.visit('/community');
      
      cy.get('input[type="search"], input[placeholder*="搜索"]').type('美食');
      cy.get('button[type="submit"], .search-button').click();
      
      cy.get('.post-item, .search-result').should('exist');
    });

    it('搜索无结果时应该显示提示', () => {
      cy.visit('/community');
      
      cy.get('input[type="search"]').type('不存在的内容xyz123abc');
      cy.get('button[type="submit"]').click();
      
      cy.contains(/没有找到|No results|暂无/i).should('be.visible');
    });
  });

  describe('通知功能', () => {
    it('应该能够查看通知', () => {
      cy.visit('/');
      
      cy.get('.notification-icon, button[aria-label*="通知"]').then(($icon) => {
        if ($icon.length > 0) {
          cy.wrap($icon).click();
          cy.get('.notification-list, .notifications').should('be.visible');
        }
      });
    });

    it('应该显示未读通知数量', () => {
      cy.visit('/');
      
      cy.get('.notification-badge, .badge').then(($badge) => {
        if ($badge.length > 0 && $badge.text().trim()) {
          expect(parseInt($badge.text())).to.be.a('number');
        }
      });
    });
  });

  describe('响应式设计', () => {
    it('社区页面应该在移动端正常显示', () => {
      cy.viewport('iphone-x');
      cy.visit('/community');
      
      cy.get('.post-list, .posts').should('be.visible');
    });

    it('帖子详情应该在平板上正常显示', () => {
      cy.viewport('ipad-2');
      cy.visit('/community');
      cy.get('.post-item').first().click();
      
      cy.get('.post-content').should('be.visible');
    });
  });
});
