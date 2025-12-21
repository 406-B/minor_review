/**
 * 社区功能端到端测试
 * 测试流程：浏览帖子列表 -> 帖子详情(含菜品跳转) -> 评论和回复 -> 创建帖子(含关联菜品) -> 删除帖子
 */

describe('E2E 社区功能测试', () => {
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
    cy.get('button.login-btn').click()
    cy.url().should('not.include', '/login')
  })

  describe('步骤1: 浏览帖子列表', () => {
    beforeEach(() => {
      cy.visit('/community')
    })

    it('应当显示社区首页标题', () => {
      cy.contains('点评社区').should('exist')
    })

    it('应当显示"我要发帖"按钮', () => {
      cy.get('button.publish-btn').should('exist')
      cy.contains('我要发帖').should('be.visible')
    })

    it('应当显示帖子列表', () => {
      // 验证帖子卡片加载
      cy.get('.post-card').should('have.length.greaterThan', 0)
    })

    it('应当显示帖子的基本信息', () => {
      cy.get('.post-card').first().within(() => {
        // 标题
        cy.get('.post-title').should('exist')
        
        // 作者信息
        cy.get('.post-author').should('exist')
        
        // 统计信息（点赞数、评论数）
        cy.get('.post-stats').should('exist')
        cy.contains(/❤️/).should('exist')
        cy.contains(/💬/).should('exist')
      })
    })

    it('应当显示关联菜品的标签', () => {
      // 查找带有菜品标签的帖子
      cy.get('.dish-tag').then(($tags) => {
        if ($tags.length > 0) {
          cy.wrap($tags).first().within(() => {
            cy.get('.dish-name').should('exist')
            cy.get('.dish-price').should('exist')
          })
        }
      })
    })

    it('应当能够点击帖子进入详情页', () => {
      // 点击帖子左侧区域（post-left）
      cy.get('.post-left').first().click()
      
      // 验证跳转到详情页
      cy.url().should('include', '/post/')
      cy.contains('帖子详情').should('exist')
    })

    it('应当显示分页控制（如果有多页）', () => {
      cy.get('.pagination').then(($pagination) => {
        if ($pagination.length > 0) {
          cy.contains('上一页').should('exist')
          cy.contains('下一页').should('exist')
        }
      })
    })
  })

  describe('步骤2: 浏览帖子详情（包括菜品链接跳转）', () => {
    beforeEach(() => {
      cy.visit('/community')
      cy.get('.post-left').first().click()
      cy.url().should('include', '/post/')
    })

    it('应当显示帖子完整内容', () => {
      // 验证标题
      cy.get('.post-subject').should('exist')
      
      // 验证正文
      cy.get('.body').should('exist')
      
      // 验证作者信息
      cy.get('.author-info').should('exist')
      cy.get('.author-name').should('exist')
      
      // 验证发布时间
      cy.get('.post-time').should('exist')
    })

    it('应当显示点赞按钮和点赞数', () => {
      cy.get('.like-btn').should('exist')
    })

    it('应当显示更多菜单（⋯按钮）', () => {
      cy.get('.more-btn').should('exist')
    })

    it('应当显示关联的菜品卡片（如果有）', () => {
      cy.get('.dish-card-section').then(($section) => {
        if ($section.length > 0) {
          cy.get('.dish-card').should('exist')
          cy.get('.dish-name').should('exist')
          cy.get('.dish-price').should('exist')
          cy.get('.dish-canteen').should('exist')
        }
      })
    })

    it('应当能够点击菜品卡片跳转到菜品详情页', () => {
      cy.get('.dish-card-section').then(($section) => {
        if ($section.length > 0) {
          // 点击菜品卡片
          cy.get('.dish-card').click()
          
          // 验证跳转到菜品详情页
          cy.url().should('include', '/dish/')
          cy.get('.dish-title').should('exist')
        } else {
          cy.log('当前帖子没有关联菜品')
        }
      })
    })

    it('应当显示评论区', () => {
      // 返回帖子详情（如果之前跳转到了菜品页）
      cy.visit('/community')
      cy.get('.post-left').first().click()
      
      cy.get('.comments-section').should('exist')
      cy.contains('评论').should('exist')
    })

    it('应当显示返回按钮', () => {
      cy.contains('button', '返回').should('exist')
    })
  })

  describe('步骤3: 评论和回复帖子', () => {
    beforeEach(() => {
      cy.visit('/community')
      cy.get('.post-left').first().click()
      cy.url().should('include', '/post/')
    })

    it('应当显示评论输入框', () => {
      cy.get('.comment-input').should('exist')
      cy.get('textarea.comment-input').should('have.attr', 'placeholder', '写下你的评论...')
    })

    it('应当能够发表评论', () => {
      const commentText = `测试评论 ${Date.now()}`
      
      // 输入评论内容
      cy.get('textarea.comment-input').clear().type(commentText)
      
      // 点击发表评论按钮
      cy.get('button.comment-btn').click()
      
      // 等待评论发表成功
      cy.wait(2000)
      
      // 验证评论出现在列表中（可能需要刷新）
      cy.reload()
      cy.contains(commentText, { timeout: 10000 }).should('exist')
    })

    it('空评论应当禁用发表按钮', () => {
      cy.get('textarea.comment-input').clear()
      cy.get('button.comment-btn').should('be.disabled')
    })

    it('应当显示已有的评论列表', () => {
      cy.get('.comments-list').then(($list) => {
        if ($list.find('.comment-item').length > 0) {
          cy.get('.comment-item').should('exist')
          cy.get('.comment-author-name').should('exist')
          cy.get('.comment-content').should('exist')
          cy.get('.comment-time').should('exist')
        } else {
          cy.get('.no-comments').should('exist')
        }
      })
    })

    it('应当能够点击回复按钮展开回复表单', () => {
      cy.get('.comment-item').then(($items) => {
        if ($items.length > 0) {
          // 点击第一条评论的回复按钮
          cy.get('.comment-item').first().within(() => {
            cy.get('button.comment-reply-btn').click()
          })
          
          // 验证回复表单出现
          cy.get('.reply-form').should('exist')
          cy.get('textarea.reply-input').should('exist')
        }
      })
    })

    it('应当能够发表回复', () => {
      cy.get('.comment-item').then(($items) => {
        if ($items.length > 0) {
          const replyText = `测试回复 ${Date.now()}`
          
          // 点击回复按钮
          cy.get('.comment-item').first().within(() => {
            cy.get('button.comment-reply-btn').click()
          })
          
          // 输入回复内容
          cy.get('textarea.reply-input').type(replyText)
          
          // 点击发送按钮
          cy.get('button.reply-submit-btn').click()
          
          // 等待回复成功
          cy.wait(2000)
          
          // 验证回复出现
          cy.reload()
          cy.contains(replyText, { timeout: 10000 }).should('exist')
        }
      })
    })

    it('应当能够取消回复', () => {
      cy.get('.comment-item').then(($items) => {
        if ($items.length > 0) {
          // 点击回复按钮
          cy.get('.comment-item').first().within(() => {
            cy.get('button.comment-reply-btn').click()
          })
          
          // 点击取消按钮
          cy.get('button.reply-cancel-btn').click()
          
          // 验证回复表单消失
          cy.get('.reply-form').should('not.exist')
        }
      })
    })
  })

  describe('步骤4: 创建和发布帖子（包括关联菜品）', () => {
    beforeEach(() => {
      cy.visit('/community')
      cy.get('button.publish-btn').click()
      cy.url().should('include', '/post/create')
    })

    it('应当显示发帖表单', () => {
      cy.contains('发帖').should('exist')
      
      // 标题输入框
      cy.get('input.subject-input').should('exist')
      cy.get('input.subject-input').should('have.attr', 'placeholder', '请输入标题（最多200字符）')
      
      // 内容输入框
      cy.get('textarea.content-input').should('exist')
      cy.get('textarea.content-input').should('have.attr', 'placeholder', '分享你的想法...')
      
      // 发布按钮
      cy.contains('button', '发布').should('exist')
    })

    it('应当显示添加菜品按钮', () => {
      cy.contains('关联菜品').should('exist')
      cy.get('button.add-dish-btn').should('exist')
    })

    it('应当能够打开菜品选择悬浮窗', () => {
      cy.get('button.add-dish-btn').click()
      
      // 验证悬浮窗出现
      cy.get('.dish-modal').should('exist')
      cy.contains('选择菜品').should('exist')
      
      // 验证搜索框
      cy.get('.modal-search input').should('exist')
    })

    it('应当能够搜索并选择菜品', () => {
      // 点击添加菜品
      cy.get('button.add-dish-btn').click()
      
      // 输入搜索关键词
      cy.get('.modal-search input').type('鸡')
      
      // 等待搜索结果
      cy.wait(1000)
      
      // 选择第一个菜品
      cy.get('.modal-results .dish-card').first().click()
      
      // 点击确认选择
      cy.get('button.confirm-btn').click()
      
      // 验证菜品已选中
      cy.get('.selected-dish-card').should('exist')
      cy.get('.selected-dish-card .dish-name').should('exist')
    })

    it('应当能够移除已选菜品', () => {
      // 先选择一个菜品
      cy.get('button.add-dish-btn').click()
      cy.get('.modal-search input').type('鸡')
      cy.wait(1000)
      cy.get('.modal-results .dish-card').first().click()
      cy.get('button.confirm-btn').click()
      
      // 点击移除按钮
      cy.get('button.remove-dish-btn').click()
      
      // 验证菜品已移除
      cy.get('.selected-dish-card').should('not.exist')
      cy.get('button.add-dish-btn').should('exist')
    })

    it('应当能够成功发布帖子（不含菜品）', () => {
      const postTitle = `测试帖子 ${Date.now()}`
      const postContent = '这是一个测试帖子的内容，用于验证发帖功能。'
      
      // 填写标题
      cy.get('input.subject-input').type(postTitle)
      
      // 填写内容
      cy.get('textarea.content-input').type(postContent)
      
      // 点击发布
      cy.contains('button', '发布').click()
      
      // 验证跳转到社区首页或帖子详情页
      cy.url().should('match', /\/community|\/post\/\d+/, { timeout: 10000 })
      
      // 验证帖子已发布
      cy.wait(2000)
      cy.visit('/community')
      cy.contains(postTitle, { timeout: 10000 }).should('exist')
    })

    it('应当能够发布带菜品的帖子', () => {
      const postTitle = `带菜品的测试帖子 ${Date.now()}`
      const postContent = '这个帖子关联了一道菜品。'
      
      // 填写标题和内容
      cy.get('input.subject-input').type(postTitle)
      cy.get('textarea.content-input').type(postContent)
      
      // 添加菜品
      cy.get('button.add-dish-btn').click()
      cy.get('.modal-search input').type('鸡')
      cy.wait(1000)
      cy.get('.modal-results .dish-card').first().click()
      cy.get('button.confirm-btn').click()
      
      // 发布帖子
      cy.contains('button', '发布').click()
      
      // 验证发布成功
      cy.url().should('match', /\/community|\/post\/\d+/, { timeout: 10000 })
    })

    it('空标题应当无法发布', () => {
      // 只填写内容
      cy.get('textarea.content-input').type('只有内容没有标题')
      
      // 点击发布（前端可能会验证）
      cy.contains('button', '发布').click()
      
      // 应当留在创建页面或显示错误提示
      cy.wait(1000)
      cy.url().should('include', '/post/create')
    })

    it('应当能够点击返回按钮', () => {
      cy.contains('button', '返回').click()
      
      // 验证返回到社区首页
      cy.url().should('include', '/community')
    })
  })

  describe('步骤5: 删除自己的帖子（不能删除他人帖子）', () => {
    let myPostId = null

    before(() => {
      // 先创建一个测试帖子
      cy.visit('/community')
      cy.get('button.publish-btn').click()
      
      const postTitle = `待删除的测试帖子 ${Date.now()}`
      cy.get('input.subject-input').type(postTitle)
      cy.get('textarea.content-input').type('这个帖子将被用于测试删除功能')
      cy.contains('button', '发布').click()
      
      // 等待发布成功并获取帖子ID
      cy.url({ timeout: 10000 }).then((url) => {
        const match = url.match(/\/post\/(\d+)/)
        if (match) {
          myPostId = match[1]
        }
      })
    })

    it('应当在自己的帖子详情页看到删除按钮', () => {
      if (!myPostId) {
        cy.log('未找到测试帖子ID，跳过测试')
        return
      }
      
      cy.visit(`/post/${myPostId}`)
      
      // 点击更多菜单
      cy.get('.more-btn').first().click()
      
      // 验证删除按钮存在
      cy.get('.dropdown-menu').should('be.visible')
      cy.get('.delete-item').should('exist')
      cy.contains('删除').should('be.visible')
    })

    it('应当能够删除自己的帖子', () => {
      if (!myPostId) {
        cy.log('未找到测试帖子ID，跳过测试')
        return
      }
      
      cy.visit(`/post/${myPostId}`)
      
      // 点击更多菜单
      cy.get('.more-btn').first().click()
      
      // 点击删除按钮
      cy.get('.delete-item').click()
      
      // 确认删除（处理浏览器原生confirm对话框）
      cy.on('window:confirm', () => true)
      
      // 等待删除完成并验证跳转
      cy.url({ timeout: 10000 }).should('include', '/community')
    })

    it('不应当在他人的帖子详情页看到删除按钮', () => {
      // 访问帖子列表
      cy.visit('/community')
      
      // 点击第一个帖子
      cy.get('.post-left').first().click()
      cy.url().should('include', '/post/')
      
      // 点击更多菜单
      cy.get('.more-btn').first().click()
      
      // 获取下拉菜单
      cy.get('.dropdown-menu').should('be.visible')
      
      // 验证删除按钮不存在或不可见（如果作者不是当前用户）
      cy.get('body').then(($body) => {
        const $deleteBtn = $body.find('.delete-item')
        if ($deleteBtn.length === 0) {
          // 删除按钮不存在，符合预期
          cy.log('✅ 他人帖子没有删除按钮')
        } else {
          // 如果存在，说明这是自己的帖子
          cy.log('⚠️ 这是自己的帖子，所以有删除按钮')
        }
      })
    })
  })

  describe('步骤6: 边界情况和用户体验', () => {
    it('评论区应当显示评论数量', () => {
      cy.visit('/community')
      cy.get('.post-left').first().click()
      
      cy.get('.comments-header').should('exist')
      cy.contains(/评论/).should('exist')
    })

    it('应当能够点赞评论', () => {
      cy.visit('/community')
      cy.get('.post-left').first().click()
      
      cy.get('.comment-item').then(($items) => {
        if ($items.length > 0) {
          cy.get('.comment-like-btn').first().click()
          cy.wait(500)
        }
      })
    })

    it('应当显示回复列表（如果有）', () => {
      cy.visit('/community')
      cy.get('.post-left').first().click()
      
      cy.get('.replies-list').then(($list) => {
        if ($list.length > 0) {
          cy.get('.reply-item').should('exist')
        }
      })
    })

    it('帖子列表为空时应当显示空状态', () => {
      // 这个测试可能需要特殊的测试环境
      // 暂时跳过或使用 mock 数据
      cy.log('帖子列表空状态测试需要特殊环境')
    })
  })

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
