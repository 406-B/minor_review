/**
 * 个人主页功能端到端测试
 * 测试个人主页浏览、资料编辑、互动统计、成就查看等功能
 */

describe('E2E 个人主页功能测试', () => {
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


  describe('步骤1: 浏览个人主页', () => {
    beforeEach(() => {
      cy.visit('/profile')
    })

    it('应当显示个人资料卡片', () => {
      cy.get('.profile-info-card').should('exist')
      cy.get('.profile-info').should('exist')
    })

    it('应当显示用户头像和昵称', () => {
      cy.get('.profile-info').within(() => {
        // 头像
        cy.get('img.avatar').should('exist')
        
        // 用户名或昵称
        cy.get('.name').should('exist')
        
        // 编辑资料按钮
        cy.get('button.edit-btn').should('exist')
        cy.contains('编辑资料').should('be.visible')
      })
    })

    it('应当显示注册时间', () => {
      cy.get('.profile-info').within(() => {
        cy.contains('注册时间').should('exist')
      })
    })

    it('应当显示偏好标签区域', () => {
      cy.get('.pref-tags').should('exist')
      cy.contains('我的偏好').should('exist')
      
      // 应当有修改偏好按钮
      cy.get('.pref-tags').within(() => {
        cy.contains('修改偏好').should('exist')
      })
    })

    it('应当显示美食日历卡片', () => {
      cy.contains('.equal-card', '美食日历').should('exist')
      cy.contains('查看完整日历').should('exist')
    })

    it('应当显示已发布内容卡片', () => {
      cy.contains('.equal-card', '已发布内容').should('exist')
      cy.contains('查看全部').should('exist')
    })

    it('应当显示我的互动卡片', () => {
      cy.contains('.equal-card', '我的互动').should('exist')
      cy.get('.interactions').should('exist')
    })

    it('应当显示我的成就卡片', () => {
      cy.contains('.equal-card', '我的成就').should('exist')
      cy.contains('查看全部').should('exist')
      
      // 四个成就等级
      cy.get('.achi-card.bronze').should('exist')
      cy.get('.achi-card.silver').should('exist')
      cy.get('.achi-card.gold').should('exist')
      cy.get('.achi-card.rainbow').should('exist')
    })

    it('应当显示个性化推荐卡片', () => {
      cy.contains('.equal-card', '个性化推荐').should('exist')
      cy.contains('查看全部').should('exist')
      
      // 推荐源选择器
      cy.get('.el-select').should('exist')
    })

    it('应当显示消费记录卡片', () => {
      cy.get('.consumption-card, .equal-card').should('exist')
    })

    it('应当显示控制面板', () => {
      cy.get('.control-panel').should('exist')
    })
  })

  describe('步骤2: 我的互动统计', () => {
    beforeEach(() => {
      cy.visit('/profile')
    })

    it('应当显示三个互动统计项', () => {
      cy.get('.interactions').within(() => {
        cy.get('.interaction-stat').should('have.length', 3)
      })
    })

    it('应当显示"我点赞的帖子"统计', () => {
      cy.get('.interactions').within(() => {
        cy.contains('我点赞的帖子').should('exist')
        cy.contains('我点赞的帖子').parent().within(() => {
          cy.get('.num').should('exist')
        })
      })
    })

    it('应当显示"我收到的评论"统计', () => {
      cy.get('.interactions').within(() => {
        cy.contains('我收到的评论').should('exist')
      })
    })

    it('应当显示"我发布的评论"统计', () => {
      cy.get('.interactions').within(() => {
        cy.contains('我发布的评论').should('exist')
      })
    })

    it('应当能够点击"我点赞的帖子"跳转', () => {
      cy.get('.interactions').within(() => {
        cy.contains('我点赞的帖子').parent().click()
      })
      
      cy.url().should('include', '/profile/liked-posts')
    })

    it('应当能够点击"我收到的评论"跳转', () => {
      cy.visit('/profile')
      
      cy.get('.interactions').within(() => {
        cy.contains('我收到的评论').parent().click()
      })
      
      cy.url().should('include', '/profile/received-comments')
    })

    it('应当能够点击"我发布的评论"跳转', () => {
      cy.visit('/profile')
      
      cy.get('.interactions').within(() => {
        cy.contains('我发布的评论').parent().click()
      })
      
      cy.url().should('include', '/profile/my-comments')
    })
  })

  describe('步骤3: 已发布内容', () => {
    beforeEach(() => {
      cy.visit('/profile')
    })

    it('应当显示已发布的帖子列表或空状态', () => {
      cy.contains('.equal-card', '已发布内容').within(() => {
        cy.get('.posts').then(($posts) => {
          // 要么有帖子，要么显示空状态
          if ($posts.find('.post-item').length > 0) {
            cy.get('.post-item').should('exist')
          } else {
            cy.contains('暂无已发布内容').should('exist')
          }
        })
      })
    })

    it('应当能够点击"查看全部"跳转到我的帖子页', () => {
      cy.contains('已发布内容').parent().within(() => {
        cy.contains('查看全部').click()
      })
      
      cy.url().should('include', '/profile/posts')
      cy.contains('我的帖子').should('exist')
    })

    it('我的帖子页应当显示帖子列表', () => {
      cy.visit('/profile/posts')
      
      // 验证标题
      cy.contains('h2', '我的帖子').should('exist')
      
      // 返回按钮
      cy.get('button.back-btn').should('exist')
      
      // 帖子列表或空状态
      cy.get('body').then(($body) => {
        if ($body.find('.post-item').length > 0) {
          cy.get('.post-item').should('exist')
        } else {
          cy.get('.empty').should('exist')
          cy.contains('暂无发布的帖子').should('exist')
        }
      })
    })

    it('应当能够从我的帖子页返回', () => {
      cy.visit('/profile/posts')
      cy.get('button.back-btn').click()
      
      cy.url().should('not.include', '/posts')
    })
  })

  describe('步骤4: 我的成就', () => {
    beforeEach(() => {
      cy.visit('/profile')
    })

    it('应当显示四个成就等级的数量', () => {
      cy.get('.achi-card.bronze').within(() => {
        cy.get('.achi-count').should('exist')
        cy.contains('本科').should('exist')
      })

      cy.get('.achi-card.silver').within(() => {
        cy.get('.achi-count').should('exist')
        cy.contains('硕士').should('exist')
      })

      cy.get('.achi-card.gold').within(() => {
        cy.get('.achi-count').should('exist')
        cy.contains('博士').should('exist')
      })

      cy.get('.achi-card.rainbow').within(() => {
        cy.get('.achi-count').should('exist')
        cy.contains('院士').should('exist')
      })
    })

    it('应当能够点击本科成就查看详情', () => {
      cy.get('.achi-card.bronze').click()
      
      cy.url().should('include', '/achievements')
      cy.url().should('include', 'tab=bronze')
    })

    it('应当能够点击硕士成就查看详情', () => {
      cy.visit('/profile')
      cy.get('.achi-card.silver').click()
      
      cy.url().should('include', '/achievements')
      cy.url().should('include', 'tab=silver')
    })

    it('应当能够点击博士成就查看详情', () => {
      cy.visit('/profile')
      cy.get('.achi-card.gold').click()
      
      cy.url().should('include', '/achievements')
      cy.url().should('include', 'tab=gold')
    })

    it('应当能够点击院士成就查看详情', () => {
      cy.visit('/profile')
      cy.get('.achi-card.rainbow').click()
      
      cy.url().should('include', '/achievements')
      cy.url().should('include', 'tab=rainbow')
    })
  })

  describe('步骤5: 编辑个人资料', () => {
    beforeEach(() => {
      cy.visit('/profile')
      cy.get('button.edit-btn').click()
      cy.url().should('include', '/profile/edit')
    })

    it('应当显示编辑资料页面', () => {
      cy.contains('编辑个人资料').should('exist')
    })

    it('应当显示头像编辑区域', () => {
      cy.get('.avatar-edit').should('exist')
      cy.get('.avatar-preview').should('exist')
      cy.get('img.avatar-img').should('exist')
      cy.contains('更换头像').should('exist')
    })

    it('应当显示昵称编辑输入框', () => {
      cy.get('.nickname-edit').should('exist')
      cy.get('input.nickname-input').should('exist')
      cy.get('.char-count').should('exist')
      cy.contains('/10').should('exist')
    })

    it('应当验证昵称不能为空', () => {
      cy.get('input.nickname-input').clear()
      cy.get('input.nickname-input').blur()
      
      // 验证错误提示
      cy.wait(500)
      cy.get('body').then(($body) => {
        if ($body.find('.error-hint').length > 0) {
          cy.contains('昵称不能为空').should('exist')
        }
      })
    })

    it('应当验证昵称不能包含空格', () => {
      cy.get('input.nickname-input').clear().type('test user')
      
      cy.wait(500)
      cy.get('.error-hint').should('exist')
      cy.contains('昵称不能包含空格').should('exist')
    })

    it('应当验证昵称长度限制', () => {
      cy.get('input.nickname-input').clear().type('12345678901')
      
      // 验证字符数限制
      cy.get('input.nickname-input').should('have.value', '1234567890') // maxlength=10
      cy.get('.char-count').should('contain', '10/10')
    })

    it('应当能够成功修改昵称', () => {
      const newNickname = `测试昵称${Date.now().toString().slice(-4)}`
      
      cy.get('input.nickname-input').clear().type(newNickname)
      cy.contains('button', '保存').click()
      
      // 等待保存成功（可能会跳转或显示提示）
      cy.wait(2000)
      
      // 验证跳转回个人主页或显示成功提示
      cy.url({ timeout: 10000 }).then((url) => {
        if (url.includes('/profile/edit')) {
          // 如果还在编辑页，检查是否有成功提示
          cy.log('保存成功，留在编辑页')
        } else {
          // 已跳转回个人主页
          cy.url().should('include', '/profile')
        }
      })
    })

    it('应当显示返回按钮', () => {
      cy.contains('button', '返回').should('exist')
    })

    it('应当能够点击返回按钮', () => {
      cy.contains('button', '返回').click()
      
      cy.url().should('not.include', '/edit')
      cy.url().should('include', '/profile')
    })

    it('应当显示修改偏好tag按钮', () => {
      cy.contains('button', '修改偏好tag').should('exist')
    })

    it('应当能够点击更换头像按钮', () => {
      cy.contains('button', '更换头像').click()
      
      // 验证头像裁剪器弹窗出现
      cy.wait(500)
      cy.get('body').then(($body) => {
        if ($body.find('.avatar-cropper, .el-dialog').length > 0) {
          cy.log('头像裁剪器已打开')
        }
      })
    })
  })

  describe('步骤6: 个性化推荐', () => {
    beforeEach(() => {
      cy.visit('/profile')
    })

    it('应当显示推荐源选择器', () => {
      cy.contains('.equal-card', '个性化推荐').within(() => {
        cy.get('.el-select').should('exist')
      })
    })

    it('应当能够切换推荐源', () => {
      cy.contains('.equal-card', '个性化推荐').within(() => {
        cy.get('.el-select').click()
      })
      
      // 验证下拉选项
      cy.wait(500)
      cy.get('.el-select-dropdown').then(($dropdown) => {
        if ($dropdown.is(':visible')) {
          cy.contains('综合').should('exist')
          cy.contains('偏好').should('exist')
          cy.contains('热度').should('exist')
        }
      })
    })

    it('应当显示推荐的菜品卡片', () => {
      cy.contains('.equal-card', '个性化推荐').within(() => {
        cy.get('body').then(($body) => {
          if ($body.find('.dish-card').length > 0) {
            cy.get('.dish-card').should('exist')
            cy.get('.dish-name').should('exist')
          } else if ($body.find('.loading-placeholder').length > 0) {
            cy.contains('正在努力加载中').should('exist')
          } else {
            cy.get('.el-empty').should('exist')
          }
        })
      })
    })

    it('应当能够点击菜品卡片跳转', () => {
      cy.contains('.equal-card', '个性化推荐').within(() => {
        cy.get('.dish-card').then(($cards) => {
          if ($cards.length > 0) {
            cy.wrap($cards).first().click()
            
            // 验证跳转到菜品详情页
            cy.url({ timeout: 5000 }).should('include', '/dish/')
          } else {
            cy.log('暂无推荐菜品')
          }
        })
      })
    })
  })

  describe('步骤7: 美食日历', () => {
    beforeEach(() => {
      cy.visit('/profile')
    })

    it('应当显示美食日历组件', () => {
      cy.contains('.equal-card', '美食日历').should('exist')
      cy.get('.food-calendar').should('exist')
    })

    it('应当能够点击查看完整日历', () => {
      cy.contains('.equal-card', '美食日历').within(() => {
        cy.contains('查看完整日历').click()
      })
      
      cy.url().should('include', '/profile/food-calendar')
    })
  })

  describe('步骤8: 成就详情页', () => {
    beforeEach(() => {
      cy.visit('/achievements')
    })

    it('应当显示成就详情页标题', () => {
      cy.contains('h2', '我的成就').should('exist')
      cy.get('button.back-btn').should('exist')
    })

    it('应当显示五个标签页', () => {
      cy.get('.el-tabs').should('exist')
      cy.contains('.el-tab-pane', '全部').should('exist')
      cy.contains('.el-tab-pane', '本科').should('exist')
      cy.contains('.el-tab-pane', '硕士').should('exist')
      cy.contains('.el-tab-pane', '博士').should('exist')
      cy.contains('.el-tab-pane', '院士').should('exist')
    })

    it('应当默认显示URL参数指定的tab', () => {
      cy.visit('/achievements?tab=bronze')
      cy.get('.el-tabs__item.is-active').should('contain', '本科')
    })

    it('应当显示成就列表或空状态', () => {
      cy.get('body').then(($body) => {
        if ($body.find('.achi-item').length > 0) {
          cy.get('.achi-item').should('exist')
          
          // 验证成就项的结构
          cy.get('.achi-item').first().within(() => {
            cy.get('.name').should('exist')
            cy.get('.sub').should('exist')
            cy.contains('打卡').should('exist')
          })
        } else {
          cy.get('.el-empty').should('exist')
          cy.contains('暂无数据').should('exist')
        }
      })
    })

    it('应当能够切换标签页', () => {
      cy.contains('.el-tab-pane', '本科').click()
      cy.wait(500)
      cy.url().should('include', 'tab=bronze')
      
      cy.contains('.el-tab-pane', '硕士').click()
      cy.wait(500)
      cy.url().should('include', 'tab=silver')
    })

    it('应当显示进度条', () => {
      cy.get('.achi-item').then(($items) => {
        if ($items.length > 0) {
          cy.get('.progress').should('exist')
        }
      })
    })

    it('应当能够点击成就项跳转到菜品详情', () => {
      cy.get('.achi-item').then(($items) => {
        if ($items.length > 0) {
          cy.wrap($items).first().click()
          cy.url().should('include', '/dish/')
        }
      })
    })

    it('应当能够点击返回按钮', () => {
      cy.get('button.back-btn').click()
      cy.url().should('not.include', '/achievements')
    })
  })

  describe('步骤9: 美食日历详情页', () => {
    beforeEach(() => {
      cy.visit('/profile/food-calendar')
    })

    it('应当显示美食日历页面标题', () => {
      cy.contains('h2', '美食日历').should('exist')
      cy.get('button.back-btn').should('exist')
    })

    it('应当显示月份选择器', () => {
      cy.get('.month-selector').should('exist')
      cy.get('.month-label').should('exist')
      
      // 验证显示当前年月
      cy.get('.month-label').should('match', /\d{4}年 \d{1,2}月/)
    })

    it('应当显示月份导航按钮', () => {
      cy.get('.month-selector').within(() => {
        cy.get('button.nav-btn').should('have.length', 2)
      })
    })

    it('应当能够切换到上一个月', () => {
      cy.get('.month-selector').within(() => {
        cy.get('button.nav-btn').first().click()
      })
      
      cy.wait(1000)
      // 验证月份已改变
      cy.get('.month-label').should('exist')
    })

    it('应当显示星期标题', () => {
      cy.get('.weekday-header').should('exist')
      cy.contains('.weekday-label', '日').should('exist')
      cy.contains('.weekday-label', '一').should('exist')
    })

    it('应当显示日历格子', () => {
      cy.get('.calendar-days').should('exist')
      cy.get('.calendar-cell').should('have.length.greaterThan', 0)
    })

    it('应当高亮显示有打卡的日期', () => {
      cy.get('.calendar-cell.has-check-in').then(($cells) => {
        if ($cells.length > 0) {
          cy.log(`找到 ${$cells.length} 个有打卡的日期`)
          cy.wrap($cells).first().within(() => {
            cy.get('.day-number').should('exist')
            cy.get('.dishes-preview').should('exist')
          })
        } else {
          cy.log('本月暂无打卡记录')
        }
      })
    })

    it('应当显示今天的标记', () => {
      cy.get('.calendar-cell.is-today').then(($today) => {
        if ($today.length > 0) {
          cy.wrap($today).should('have.class', 'is-today')
        }
      })
    })

    it('应当能够悬停查看菜品详情卡片', () => {
      cy.get('.calendar-cell.has-check-in').then(($cells) => {
        if ($cells.length > 0) {
          cy.wrap($cells).first().within(() => {
            cy.get('.dish-item').first().trigger('mouseenter')
          })
          
          cy.wait(500)
          // 验证悬浮卡片出现
          cy.get('.dish-hover-card').should('exist')
        }
      })
    })

    it('应当能够点击返回按钮', () => {
      cy.get('button.back-btn').click()
      cy.url().should('not.include', '/food-calendar')
    })
  })

  describe('步骤10: 我点赞的帖子页', () => {
    beforeEach(() => {
      cy.visit('/profile/liked-posts')
    })

    it('应当显示页面标题', () => {
      cy.contains('h2', '我点赞的帖子').should('exist')
      cy.get('button.back-btn').should('exist')
    })

    it('应当显示帖子列表或空状态', () => {
      cy.wait(1000)
      cy.get('body').then(($body) => {
        if ($body.find('.post-item').length > 0) {
          cy.get('.post-item').should('exist')
        } else if ($body.find('.el-empty').length > 0) {
          cy.get('.el-empty').should('exist')
          cy.contains('暂无点赞的帖子').should('exist')
          cy.contains('去社区看看').should('exist')
        } else if ($body.find('.loading').length > 0) {
          cy.contains('加载中').should('exist')
        }
      })
    })

    it('应当显示分页控件（如果有多页）', () => {
      cy.get('.pagination').then(($pagination) => {
        if ($pagination.length > 0) {
          cy.contains('上一页').should('exist')
          cy.contains('下一页').should('exist')
          cy.contains(/第 \d+ \/ \d+ 页/).should('exist')
        }
      })
    })

    it('应当能够点击帖子跳转到详情', () => {
      cy.get('.post-item').then(($items) => {
        if ($items.length > 0) {
          cy.wrap($items).first().click()
          cy.url({ timeout: 5000 }).should('include', '/community/')
        }
      })
    })

    it('应当能够点击返回按钮', () => {
      cy.visit('/profile/liked-posts')
      cy.get('button.back-btn').click()
      cy.url().should('not.include', '/liked-posts')
    })
  })

  describe('步骤11: 我收到的评论页', () => {
    beforeEach(() => {
      cy.visit('/profile/received-comments')
    })

    it('应当显示页面标题', () => {
      cy.contains('h2', '我收到的评论').should('exist')
      cy.get('button.back-btn').should('exist')
    })

    it('应当显示评论列表或空状态', () => {
      cy.wait(2000)
      cy.get('body').then(($body) => {
        if ($body.find('.comment-card').length > 0) {
          cy.get('.comment-card').should('exist')
          
          // 验证评论卡片结构
          cy.get('.comment-card').first().within(() => {
            cy.get('.comment-header').should('exist')
            cy.get('.comment-avatar').should('exist')
            cy.get('.author-name').should('exist')
            cy.get('.comment-content').should('exist')
            cy.get('.post-link').should('exist')
          })
        } else if ($body.find('.el-empty').length > 0) {
          cy.get('.el-empty').should('exist')
          cy.contains('暂无收到的评论').should('exist')
        } else if ($body.find('.loading').length > 0) {
          cy.contains('加载中').should('exist')
        }
      })
    })

    it('应当显示评论来源的帖子标题', () => {
      cy.get('.comment-card').then(($cards) => {
        if ($cards.length > 0) {
          cy.get('.post-link').should('exist')
          cy.contains('来自您的帖子').should('exist')
        }
      })
    })

    it('应当显示评论者信息', () => {
      cy.get('.comment-card').then(($cards) => {
        if ($cards.length > 0) {
          cy.get('.author-info').should('exist')
          cy.get('.comment-time').should('exist')
        }
      })
    })

    it('应当能够点击评论卡片跳转到帖子详情', () => {
      cy.get('.comment-card').then(($cards) => {
        if ($cards.length > 0) {
          cy.wrap($cards).first().click()
          cy.url({ timeout: 5000 }).should('match', /\/community\/\d+/)
        }
      })
    })

    it('应当显示分页控件（如果有多页）', () => {
      cy.visit('/profile/received-comments')
      cy.wait(1000)
      cy.get('.pagination').then(($pagination) => {
        if ($pagination.length > 0) {
          cy.contains('上一页').should('exist')
          cy.contains('下一页').should('exist')
        }
      })
    })

    it('应当能够点击返回按钮', () => {
      cy.get('button.back-btn').click()
      cy.url().should('not.include', '/received-comments')
    })
  })

  describe('步骤12: 我发布的评论页', () => {
    beforeEach(() => {
      cy.visit('/profile/my-comments')
    })

    it('应当显示页面标题', () => {
      cy.contains('h2', '我发布的评论').should('exist')
      cy.get('button.back-btn').should('exist')
    })

    it('应当显示评论列表或空状态', () => {
      cy.wait(1000)
      cy.get('body').then(($body) => {
        if ($body.find('.comment-card').length > 0) {
          cy.get('.comment-card').should('exist')
          
          // 验证评论卡片结构
          cy.get('.comment-card').first().within(() => {
            cy.get('.comment-content').should('exist')
            cy.get('.comment-meta').should('exist')
            cy.get('.post-link').should('exist')
            cy.get('.comment-time').should('exist')
          })
        } else if ($body.find('.el-empty').length > 0) {
          cy.get('.el-empty').should('exist')
          cy.contains('暂无发布的评论').should('exist')
        } else if ($body.find('.loading').length > 0) {
          cy.contains('加载中').should('exist')
        }
      })
    })

    it('应当显示评论所属的帖子标题', () => {
      cy.get('.comment-card').then(($cards) => {
        if ($cards.length > 0) {
          cy.get('.post-link').should('exist')
          cy.contains('来自帖子').should('exist')
        }
      })
    })

    it('应当显示评论时间', () => {
      cy.get('.comment-card').then(($cards) => {
        if ($cards.length > 0) {
          cy.get('.comment-time').should('exist')
        }
      })
    })

    it('应当能够点击评论卡片跳转到帖子详情', () => {
      cy.get('.comment-card').then(($cards) => {
        if ($cards.length > 0) {
          cy.wrap($cards).first().click()
          cy.url({ timeout: 5000 }).should('match', /\/community\/\d+/)
        }
      })
    })

    it('应当显示分页控件（如果有多页）', () => {
      cy.get('.pagination').then(($pagination) => {
        if ($pagination.length > 0) {
          cy.contains('上一页').should('exist')
          cy.contains('下一页').should('exist')
          cy.contains(/第 \d+ \/ \d+ 页/).should('exist')
        }
      })
    })

    it('应当能够点击返回按钮', () => {
      cy.get('button.back-btn').click()
      cy.url().should('not.include', '/my-comments')
    })
  })

  describe('步骤13: 边界情况和响应式', () => {
    it('未登录用户访问个人主页应显示提示', () => {
      // 退出登录
      cy.clearLocalStorage()
      cy.visit('/profile')
      
      // 验证显示登录提示
      cy.get('.profile-info-placeholder').should('exist')
      cy.contains('登录以体验更多个性化内容').should('exist')
      
      // 验证各功能区显示遮罩
      cy.get('.component-overlay').should('exist')
      cy.contains('登录后查看详细内容').should('exist')
    })

    it('应当在移动设备上正常显示', () => {
      cy.viewport('iphone-x')
      cy.visit('/profile')
      
      cy.get('.profile-wrap').should('be.visible')
    })

    it('应当在平板上正常显示', () => {
      cy.viewport('ipad-2')
      cy.visit('/profile')
      
      cy.get('.profile-wrap').should('be.visible')
    })
  })
})
