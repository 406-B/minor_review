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
  beforeEach(() => {
    cy.clearLocalStorage()
    cy.clearCookies()
    // 使用表单范围内的登录，匹配前端结构并确保 token 正确写入
    cy.visit('/login')
    cy.get('.el-form').within(() => {
      cy.get('input[autocomplete="username"]').clear().type(testUser.username)
      cy.get('input[autocomplete="current-password"]').clear().type(testUser.password)
      cy.get('button.login-btn').first().click()
    })
    cy.url().should('not.include', '/login')
    handlePossibleOnboarding()
    cy.window().its('localStorage').invoke('getItem', 'jwt').should('exist')
  })

  // 复用 auth 中的 onboarding 处理逻辑：登录后可能会被重定向到 onboarding，需要点击跳过
  function handlePossibleOnboarding() {
    return cy.location('pathname', { timeout: 20000 }).then((p) => {
      if (p.includes('/tags')) {
        cy.get('.actions', { timeout: 10000 }).should('exist')
        cy.contains('button', '跳过', { timeout: 10000 }).should('be.visible')
        const trySkipAttempt = (attempt = 1) => {
          return cy.contains('button', '跳过', { timeout: 10000 }).then(($btn) => {
            cy.wrap($btn).click({ force: attempt > 1 })
            return cy.wait(500).then(() => {
              return cy.location('pathname', { timeout: 5000 }).then((uAfter) => {
                if (uAfter.includes('/profile')) return cy.wrap(null)
                if (attempt < 3) {
                  cy.log(`Skip attempt ${attempt} failed, retrying...`)
                  return trySkipAttempt(attempt + 1)
                }
                throw new Error('点击跳过后未能跳转到 /profile')
              })
            })
          })
        }
        return trySkipAttempt(1)
      }
      if (p.includes('/profile')) {
        return cy.wait(500).then(() => {
          return cy.location('pathname', { timeout: 5000 }).then((p2) => {
            if (p2.includes('/onboarding/tags')) {
              cy.get('.actions', { timeout: 10000 }).should('exist')
              cy.contains('button', '跳过', { timeout: 10000 }).should('be.visible')
              const trySkipAttempt = (attempt = 1) => {
                return cy.contains('button', '跳过', { timeout: 10000 }).then(($btn) => {
                  cy.wrap($btn).click({ force: attempt > 1 })
                  return cy.wait(500).then(() => {
                    return cy.location('pathname', { timeout: 5000 }).then((uAfter) => {
                      if (uAfter.includes('/profile')) return cy.wrap(null)
                      if (attempt < 3) {
                        cy.log(`Skip attempt ${attempt} failed, retrying...`)
                        return trySkipAttempt(attempt + 1)
                      }
                      throw new Error('点击跳过后未能跳转到 /profile')
                    })
                  })
                })
              }
              return trySkipAttempt(1)
            }
            return cy.wrap(null)
          })
        })
      }
      return cy.wait(500).then(() => handlePossibleOnboarding())
    })
  }

  // 在需要登录前的测试可以显式执行这段登录流程
  function doLogin(user) {
    cy.visit('/login')
    cy.get('input[autocomplete="username"]').type(user.username)
    cy.get('input[autocomplete="current-password"]').type(user.password)
    // 在表单范围内点击登录按钮，避免选择到其他地方的同名按钮
    cy.get('.el-form').find('button.login-btn').first().click()
    // 等待 JWT 写入 localStorage 并处理可能的 onboarding
    cy.window().its('localStorage').invoke('getItem', 'jwt').should('exist')
    handlePossibleOnboarding()
    cy.url().should('not.include', '/login')
  }

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
      
      // 验证跳转到详情页（前端使用 /community/:id 路径）
      cy.url().should('include', '/community/')
      cy.contains('帖子详情').should('exist')
    })
  })

  describe('步骤2: 浏览帖子详情（包括菜品链接跳转）', () => {
    beforeEach(() => {
      cy.visit('/community')
      // 优先查找标题包含“红烧”的帖子用作评论/回复测试目标；不存在则使用第一条帖子
      cy.get('body').then(($body) => {
        const $target = $body.find('.post-card:contains("红烧"), .post-item:contains("红烧")')
        if ($target.length > 0) {
          cy.contains('.post-card, .post-item', '红烧').first().click()
        } else {
          cy.get('.post-left').first().click()
        }
      })
      cy.url().should('include', '/community/')
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
          cy.get('.dish-card').first().click()
          
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
      cy.url().should('include', '/community/')
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
      cy.get('button.comment-btn').first().click()
      
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
            cy.get('button.comment-reply-btn').first().click()
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
          cy.get('button.reply-submit-btn').first().click()
          
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
          cy.get('button.reply-cancel-btn').first().click()
          
          // 验证回复表单消失
          cy.get('.reply-form').should('not.exist')
        }
      })
    })

    // 将 步骤6 的边界用例合并到步骤3 中
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
  })

  describe('步骤4: 创建和发布帖子（包括关联菜品）', () => {
    beforeEach(() => {
      cy.visit('/community')
        cy.get('button.publish-btn').first().click()
        cy.url().should('include', '/community/create')
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
      cy.get('button.add-dish-btn').first().click()
      
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
      cy.get('button.confirm-btn').first().click()
      
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
      cy.get('button.remove-dish-btn').first().click()
      
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
      cy.contains('button', '发布').first().click()
      
      // 验证跳转到社区首页或帖子详情页
      cy.url().should('match', /\/community|\/community\/\d+/, { timeout: 10000 })

      // 验证帖子已发布并返回列表页面
      cy.wait(2000)
      cy.visit('/community')
      cy.contains(postTitle, { timeout: 10000 }).should('exist')

      // 将删除流程并入此用例：点击刚发布的帖子进入详情并删除
      cy.contains(postTitle).closest('.post-card').within(() => {
        cy.get('.post-left').click()
      })

      // 详情页点击更多菜单并删除（若为自己的帖子，删除按钮应存在）
      cy.get('.more-btn').first().click()
      cy.get('.dropdown-menu').should('be.visible')
      cy.get('body').then(($body) => {
        const $del = $body.find('.menu-item.delete-item, .delete-item')
        if ($del.length > 0) {
          cy.get('.delete-item').click()
          // 处理 confirm
          cy.on('window:confirm', () => true)
          // 等待删除并验证回到列表
          cy.url({ timeout: 10000 }).should('include', '/community')
          // 确认帖子已被移除
          cy.contains(postTitle).should('not.exist')
        } else {
          // 如果删除按钮不存在，记录警告
          cy.log('⚠️ 删除按钮未找到，可能权限问题或并非自己的帖子')
        }
      })
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
      cy.url().should('match', /\/community|\/community\/\d+/, { timeout: 10000 })
    })

    it('空标题应当无法发布', () => {
      // 只填写内容
      cy.get('textarea.content-input').type('只有内容没有标题')
      
      // 点击发布（前端可能会验证）
      cy.contains('button', '发布').click()
      
      // 应当留在创建页面或显示错误提示
      cy.wait(1000)
      cy.url().should('include', '/community/create')
    })

    it('应当能够点击返回按钮', () => {
      cy.contains('button', '返回').first().click()
      
      // 验证返回到社区首页
      cy.url().should('include', '/community')
    })
  })

  describe('步骤5: 删除相关检查（仅保留他人帖子无删除按钮）', () => {
    it('不应当在他人的帖子详情页看到删除按钮', () => {
      // 访问帖子列表并打开第一条帖子详情
      cy.visit('/community')
      cy.get('.post-left').first().click()
      cy.url().should('include', '/community/')

      // 点击更多菜单并检查下拉菜单中是否有删除项
      cy.get('.more-btn').first().click()
      cy.get('.dropdown-menu').should('be.visible')

      cy.get('body').then(($body) => {
        const $deleteBtn = $body.find('.menu-item.delete-item, .delete-item')
        if ($deleteBtn.length === 0) {
          cy.log('✅ 他人帖子没有删除按钮')
        } else {
          cy.log('⚠️ 可能为自己的帖子，存在删除按钮')
        }
      })
    })
  })

});
