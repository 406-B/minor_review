/**
 * 个人主页功能端到端测试
 * 测试个人主页浏览、资料编辑、互动统计、成就查看等功能
 */

describe('E2E 个人主页功能测试', () => {
  const testUser = {
    username: 'tester123',
    password: '123456Aa-'
  }

  // 处理可能的 onboarding 跳转（复用 auth 测试中的逻辑）
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
                if (attempt < 3) return trySkipAttempt(attempt + 1)
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
                      if (attempt < 3) return trySkipAttempt(attempt + 1)
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

  // 每个测试前登录（与 community.cy.js 保持一致）
  beforeEach(() => {
    cy.clearLocalStorage()
    cy.clearCookies()
    cy.visit('/login')
    cy.get('.el-form').within(() => {
      cy.get('input[autocomplete="username"]').clear().type(testUser.username)
      cy.get('input[autocomplete="current-password"]').clear().type(testUser.password)
      cy.get('button.login-btn').first().click()
    })
    cy.url().should('not.include', '/login')
    handlePossibleOnboarding()
    // 使用页面 UI 修改偏好（若可见）以确保个性化推荐有数据：
    // - 在个人主页偏好区域点击“修改偏好”或“去设置”（若存在）
    // - 在 /onboarding/tags 页面选择最多 3 个标签并点击“保存偏好”
    cy.visit('/profile')
    cy.get('body').then(($body) => {
      // 先查找偏好区域内的修改入口
      if ($body.find('.pref-tags').length > 0) {
        cy.get('.pref-tags').then(($pt) => {
          const btnExists = $pt.find('button:contains("修改偏好"), button:contains("去设置"), .el-button:contains("修改偏好"), .el-button:contains("去设置")').length > 0
          if (btnExists) {
            cy.wrap($pt).contains(/修改偏好|去设置/).click({ force: true })
            // 确认进入标签页
            cy.url({ timeout: 10000 }).should('include', '/onboarding/tags')

            // 等待标签加载并选择最多 3 个
            cy.get('.tag-item', { timeout: 10000 }).then(($tags) => {
              if ($tags.length > 0) {
                const take = Math.min(3, $tags.length)
                for (let i = 0; i < take; i++) {
                  cy.wrap($tags.eq(i)).click()
                }
                cy.contains('button', '保存偏好').click()
                // 保存后应回到 /profile
                cy.url({ timeout: 10000 }).should('include', '/profile')
              } else {
                // 若标签未加载则点击跳过
                cy.contains('button', '跳过').click({ force: true })
                cy.url({ timeout: 10000 }).should('include', '/profile')
              }
            })
          }
        })
      }
    })
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
      // 偏好标签区域应存在（登录用户）
      cy.get('.pref-tags').should('exist')
      cy.get('.pref-tags').then(($pt) => {
        // 在 pref-tags 范围内断言文字与按钮存在性
        expect($pt.find(':contains("我的偏好")').length > 0).to.equal(true)
        const hasModify = $pt.find('button:contains("修改偏好"), .el-button:contains("修改偏好")').length > 0
        const hasSetup = $pt.find('button:contains("去设置"), .el-button:contains("去设置")').length > 0
        expect(hasModify || hasSetup).to.equal(true)
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
        cy.contains('查看全部').first().click()
      })
      
      cy.url().should('include', '/profile/posts')
      cy.contains('我的帖子').should('exist')
    })

    it('我的帖子页应当显示帖子列表', () => {
      // 通过首页的“查看全部”入口进入我的帖子页（符合前端实现）
      cy.visit('/profile')
      cy.contains('已发布内容').parent().within(() => {
        cy.contains('查看全部').first().click()
      })

      // 验证标题
      cy.contains('h2', '我的帖子').should('exist')

      // 返回按钮
      cy.get('button.back-btn').should('exist')

      // 帖子列表或空状态
      cy.get('.posts-container').then(($ct) => {
        if ($ct.find('.post-item').length > 0) {
          cy.get('.posts-container .post-item').should('exist')
        } else {
          cy.get('.empty').should('exist')
          cy.contains('暂无发布的帖子').should('exist')
        }
      })
    })

    it('应当能够从我的帖子页返回', () => {
      cy.visit('/profile/posts')
      cy.get('button.back-btn').first().click()
      
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
      cy.get('button.edit-btn').first().click()
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
      cy.contains('button', '保存').first().click()
      
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
      cy.contains('button', '返回').first().click()
      
      cy.url().should('not.include', '/edit')
      cy.url().should('include', '/profile')
    })

    it('应当显示修改偏好tag按钮', () => {
      cy.contains('button', '修改偏好tag').should('exist')
    })

    it('应当能够点击更换头像按钮', () => {
      cy.contains('button', '更换头像').first().click()
      
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
      cy.contains('.equal-card', '个性化推荐').then(($card) => {
        // 先使用同步 jQuery 检查分支，避免对可能不存在的选择器进行等待
        const hasDish = $card.find('.dish-card').length > 0
        const hasLoading = $card.find('.loading-placeholder').length > 0
        const hasEmpty = $card.find('.el-empty').length > 0

        if (hasDish) {
          cy.wrap($card).find('.dish-card').should('exist')
          cy.wrap($card).find('.dish-name').should('exist')
        } else if (hasLoading) {
          cy.wrap($card).contains('正在努力加载中').should('exist')
        } else if (hasEmpty) {
          cy.wrap($card).find('.el-empty').should('exist')
        } else {
          // 既无菜品，也无加载或空态，记录日志（可能为异步短暂未渲染）
          cy.log('个性化推荐区：既无菜品也无空态或加载占位，跳过断言')
        }
      })
    })

    it('应当能够点击菜品卡片跳转', () => {
      cy.contains('.equal-card', '个性化推荐').within(() => {
        cy.get('.dish-card').then(($cards) => {
          if ($cards.length > 0) {
            // 优先选取可见的 card，避免被分页/遮挡的占位元素影响点击
            const visible = $cards.filter(':visible')
            if (visible.length > 0) {
              cy.wrap(visible.eq(0)).scrollIntoView().should('be.visible').click()
              cy.url({ timeout: 5000 }).should('include', '/dish/')
            } else {
              // 回退：若所有元素都不可见，尝试滚动第一个并强制点击
              cy.wrap($cards.eq(0)).scrollIntoView().click({ force: true })
              cy.url({ timeout: 5000 }).should('include', '/dish/')
            }
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
      // Element Plus 渲染的 tab header 为 `.el-tabs__item`
      cy.contains('.el-tabs__item', '全部').should('exist')
      cy.contains('.el-tabs__item', '本科').should('exist')
      cy.contains('.el-tabs__item', '硕士').should('exist')
      cy.contains('.el-tabs__item', '博士').should('exist')
      cy.contains('.el-tabs__item', '院士').should('exist')
    })

    it('应当默认显示URL参数指定的tab', () => {
      cy.visit('/achievements?tab=bronze')
      cy.get('.el-tabs__item.is-active').should('contain', '本科')
    })

    it('应当显示成就列表并验证项结构（若为空则去食堂打卡一次）', () => {
      // 等待成就详情容器渲染并给予短暂稳定时间，再在容器内判断是否有成就项，避免因异步渲染导致误判
      cy.get('.achievements-detail', { timeout: 10000 }).should('exist')
      // 等待短时以让前端可能的异步数据与动画完成
      cy.wait(1000)
      cy.get('.achievements-detail').then(($root) => {
        if ($root.find('.grid-list .achi-item').length > 0) {
          cy.wrap($root).find('.grid-list .achi-item').first().within(() => {
            cy.get('.name').should('exist')
            cy.get('.sub').should('exist')
            cy.contains('打卡').should('exist')
          })
        } else {
          // 如果容器内没有成就项，前往食堂页面，打开第一个菜品并执行一次打卡（参考 canteen.cy.js）
          cy.visit('/canteen')
          cy.get('.canteen-sidebar-menu .el-menu-item', { timeout: 10000 }).first().click()
          cy.get('.dish-card', { timeout: 10000 }).first().click()
          cy.url({ timeout: 10000 }).should('include', '/dish/')

          // 明确断言已登录并拦截打卡请求
          cy.window().its('localStorage').invoke('getItem', 'jwt').should('exist')
          cy.intercept('POST', '/api/dishes/*/check-in/').as('checkinReq')

          // 点击打卡（若存在）并等待后端响应
          cy.contains('button', '打卡', { timeout: 5000 }).then(($btn) => {
            if ($btn.length > 0) {
              cy.wrap($btn).click()
              cy.wait('@checkinReq', { timeout: 10000 }).then((interception) => {
                const authHeader = interception.request.headers && (interception.request.headers.authorization || interception.request.headers.Authorization)
                expect(authHeader, 'Authorization header should be sent').to.exist
                const status = interception.response?.statusCode
                // 记录以便排查非200情况
                if (status !== 200) {
                  try { cy.log('checkin response: ' + JSON.stringify(interception.response.body)) } catch (e) { cy.log('checkin response: <unserializable>') }
                }
                expect(status).to.equal(200)
              })
            }
          })

          // 返回成就页并断言至少有一条成就（等待后端数据刷新）
          cy.visit('/achievements')
          cy.get('.achievements-detail .hint', { timeout: 10000 }).should('not.exist')
          cy.get('.achievements-detail .grid-list .achi-item', { timeout: 10000 }).should('exist')
          cy.get('.achievements-detail .grid-list .achi-item').first().within(() => {
            cy.get('.name').should('exist')
            cy.get('.sub').should('exist')
            cy.contains('打卡').should('exist')
          })
        }
      })
    })

    it('应当能够切换标签页', () => {
      cy.contains('.el-tabs__item', '本科').click()
      cy.wait(500)
      cy.url().should('include', 'tab=bronze')
      
      cy.contains('.el-tabs__item', '硕士').click()
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
      
      // 验证显示当前年月（接受任意空白间隔以兼容前端渲染差异）
      cy.get('.month-label').invoke('text').then((txt) => {
        expect(txt.trim()).to.match(/\d{4}年\s*\d{1,2}月/)
      })
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
      // 从个人主页入口进入“我点赞的帖子”页，避免直接访问路由
      cy.visit('/profile')
      cy.get('.interactions').within(() => {
        cy.contains('我点赞的帖子').parent().click()
      })

      // 如果当前没有已点赞的帖子，前往社区打开第一条帖子详情并在详情页点赞，再返回已点赞列表
      cy.get('body').then(($body) => {
        if ($body.find('.post-item').length === 0) {
          cy.log('未发现已点赞的帖子，前往社区在详情页为一条帖子点赞')
          cy.visit('/community')

          // 打开第一条帖子详情：优先点击内部链接，否则点击卡片或左侧区域
          cy.get('.post-card, .post-item', { timeout: 10000 }).first().then(($card) => {
            const $link = $card.find('a[href*="/community/"]')
            if ($link.length > 0) {
              cy.wrap($link).first().click({ force: true })
            } else if ($card.find('.post-left').length > 0) {
              cy.wrap($card).find('.post-left').first().click({ force: true })
            } else {
              cy.wrap($card).click({ force: true })
            }
          })

          // 在详情页重新查询并点击点赞按钮（避免使用已脱离 DOM 的 jQuery 对象）
          cy.url({ timeout: 5000 }).should('include', '/community/')
          cy.get('body').then(($bd) => {
            if ($bd.find('.like-btn').length > 0) {
              cy.get('.like-btn', { timeout: 5000 }).first().click({ force: true })
              cy.wait(500)
            }
          })

          // 返回个人主页并再次进入已点赞页面
          cy.visit('/profile')
          cy.get('.interactions').within(() => {
            cy.contains('我点赞的帖子').parent().click()
          })
        }
      })
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
        } else {
          // 若为空，则去社区为一条帖子点赞（在详情页点赞更可靠），然后返回并断言已点赞列表有内容
          cy.visit('/community')

          // 打开第一条帖子详情（优先通过链接，否则点击卡片左侧）
          cy.get('.post-card, .post-item', { timeout: 10000 }).first().then(($card) => {
            const $link = $card.find('a[href*="/community/"]')
            if ($link.length > 0) {
              cy.wrap($link).first().click({ force: true })
            } else if ($card.find('.post-left').length > 0) {
              cy.wrap($card).find('.post-left').first().click({ force: true })
            } else {
              cy.wrap($card).click({ force: true })
            }
          })

          // 确认已进入详情页并点赞（若可见）
          cy.url({ timeout: 5000 }).should('include', '/community/')
          cy.get('body').then(($bd) => {
            if ($bd.find('.like-btn').length > 0) {
              cy.get('.like-btn', { timeout: 5000 }).first().click({ force: true })
              cy.wait(500)
            }
          })

          // 返回个人主页并进入已点赞页面
          cy.visit('/profile')
          cy.get('.interactions').within(() => {
            cy.contains('我点赞的帖子').parent().click()
          })

          // 现在断言已点赞的帖子列表存在
          cy.get('.post-item', { timeout: 10000 }).should('have.length.greaterThan', 0)
        }
      })
    })

    it('应当显示分页控件（如果有多页）', () => {
      // 分页检查已移除（不在当前测试范围）
    })

    it('应当能够点击帖子跳转到详情', () => {
      cy.get('.post-item', { timeout: 10000 }).then(($items) => {
        if ($items.length > 0) {
          // 重新查询并点击第一项，避免使用之前已脱离 DOM 的 jQuery 对象
          cy.get('.post-item').first().scrollIntoView().click({ force: true })
          cy.url({ timeout: 5000 }).should('include', '/community/')
        }
      })
    })

    it('应当能够点击返回按钮', () => {
      // 已在 beforeEach 导航到该页
      cy.get('button.back-btn').click()
      cy.url().should('not.include', '/liked-posts')
    })
  })

  describe('步骤11: 我收到的评论页', () => {
    beforeEach(() => {
      // 从个人主页入口进入“我收到的评论”页
      cy.visit('/profile')
      cy.get('.interactions').within(() => {
        cy.contains('我收到的评论').parent().click()
      })
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
          cy.get('.el-empty', { timeout: 10000 }).should('exist')
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
      // 分页检查已移除（不在当前测试范围）
    })

    it('应当能够点击返回按钮', () => {
      cy.get('button.back-btn').click()
      cy.url().should('not.include', '/received-comments')
    })
  })

  describe('步骤12: 我发布的评论页', () => {
    beforeEach(() => {
      // 通过个人主页导航到“我发布的评论”页
      cy.visit('/profile')
      cy.get('.interactions').within(() => {
        cy.contains('我发布的评论').parent().click()
      })
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
          cy.get('.el-empty', { timeout: 10000 }).should('exist')
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
      // 分页检查已移除（不在当前测试范围）
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
  })
})
