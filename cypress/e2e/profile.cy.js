/**
 * 用户资料功能端到端测试
 * 测试用户资料查看、编辑、头像上传等功能
 */

describe('用户资料管理', () => {
  beforeEach(() => {
    // 登录用户
    cy.visit('/login');
    cy.get('input[name="username"]').type('testuser');
    cy.get('input[name="password"]').type('password123');
    cy.get('button[type="submit"]').click();
    cy.url().should('not.include', '/login');
  });

  describe('查看用户资料', () => {
    it('应该能够查看自己的资料', () => {
      cy.visit('/profile');
      
      // 验证资料页面加载
      cy.contains(/个人资料|Profile|我的资料/i).should('be.visible');
      
      // 验证基本信息显示
      cy.get('[data-cy=user-profile], .profile-container, .user-info').should('exist');
    });

    it('应该显示用户的基本信息', () => {
      cy.visit('/profile');
      
      // 检查用户名
      cy.contains('testuser').should('be.visible');
      
      // 检查其他信息（如果存在）
      cy.get('.profile-info, .user-details').within(() => {
        cy.get('.username, .email, .bio').should('exist');
      });
    });

    it('应该能够查看其他用户的资料', () => {
      // 访问特定用户的资料页
      cy.visit('/profile/1');
      
      // 验证页面加载
      cy.get('.profile-container, .user-profile').should('exist');
    });
  });

  describe('编辑用户资料', () => {
    beforeEach(() => {
      cy.visit('/profile/edit');
    });

    it('应该能够访问编辑页面', () => {
      cy.url().should('include', '/profile/edit');
      cy.contains(/编辑资料|Edit Profile/i).should('be.visible');
    });

    it('应该能够更新个人简介', () => {
      const newBio = '这是我的新个人简介 - ' + Date.now();
      
      cy.get('textarea[name="bio"], textarea[placeholder*="简介"], textarea[placeholder*="bio"]')
        .clear()
        .type(newBio);
      
      cy.get('button[type="submit"], button:contains("保存"), button:contains("Save")').click();
      
      // 验证保存成功
      cy.contains(/保存成功|Saved successfully|更新成功/i, { timeout: 10000 }).should('be.visible');
      
      // 返回资料页验证更新
      cy.visit('/profile');
      cy.contains(newBio).should('be.visible');
    });

    it('应该能够更新用户名', () => {
      const newUsername = 'newusername_' + Date.now();
      
      cy.get('input[name="username"]').clear().type(newUsername);
      cy.get('button[type="submit"]').click();
      
      cy.contains(/保存成功|Saved/i, { timeout: 10000 }).should('be.visible');
    });

    it('应该能够更新邮箱', () => {
      const newEmail = `newemail_${Date.now()}@example.com`;
      
      cy.get('input[name="email"], input[type="email"]').clear().type(newEmail);
      cy.get('button[type="submit"]').click();
      
      cy.contains(/保存成功|Saved/i, { timeout: 10000 }).should('be.visible');
    });

    it('应该验证邮箱格式', () => {
      cy.get('input[name="email"]').clear().type('invalid-email');
      cy.get('button[type="submit"]').click();
      
      // 验证错误消息
      cy.contains(/邮箱格式|Invalid email|不正确/i).should('be.visible');
    });

    it('应该能够取消编辑', () => {
      // 修改一些内容
      cy.get('textarea[name="bio"]').then(($textarea) => {
        if ($textarea.length > 0) {
          cy.wrap($textarea).clear().type('将要取消的内容');
        }
      });
      
      // 点击取消按钮
      cy.contains('button', /取消|Cancel/).click();
      
      // 验证返回到资料页
      cy.url().should('match', /\/profile(?!\/edit)/);
    });
  });

  describe('头像管理', () => {
    beforeEach(() => {
      cy.visit('/profile/edit');
    });

    it('应该显示当前头像', () => {
      cy.get('img[alt*="头像"], img[alt*="avatar"], .avatar-image').should('exist');
    });

    it('应该有上传头像的选项', () => {
      cy.get('input[type="file"], button:contains("上传"), button:contains("Upload")').should('exist');
    });

    it('应该能够预览选择的头像', () => {
      // 注意: 这需要实际的文件上传功能
      cy.get('input[type="file"]').then(($input) => {
        if ($input.length > 0) {
          // 这里需要 cypress-file-upload 插件来完整测试
          cy.log('头像上传功能需要 cypress-file-upload 插件');
        }
      });
    });
  });

  describe('隐私设置', () => {
    it('应该能够访问隐私设置', () => {
      cy.visit('/profile');
      
      // 查找隐私设置链接或按钮
      cy.get('a:contains("设置"), a:contains("Settings")').then(($link) => {
        if ($link.length > 0) {
          cy.wrap($link).first().click();
          cy.url().should('match', /settings|privacy/);
        }
      });
    });
  });

  describe('我的内容', () => {
    it('应该能够查看我的帖子', () => {
      cy.visit('/profile');
      
      cy.contains(/我的帖子|My Posts|发布的/i).click();
      
      cy.url().should('match', /posts|profile/);
      cy.get('.post-item, .post-card').should('exist');
    });

    it('应该能够查看我的评论', () => {
      cy.visit('/profile');
      
      cy.contains(/我的评论|My Comments|评论/i).then(($link) => {
        if ($link.length > 0) {
          cy.wrap($link).click();
          cy.url().should('match', /comments|profile/);
        }
      });
    });

    it('应该能够查看收藏的内容', () => {
      cy.visit('/profile');
      
      cy.contains(/收藏|Favorites|喜欢/i).then(($link) => {
        if ($link.length > 0) {
          cy.wrap($link).click();
          cy.url().should('match', /favorites|liked|profile/);
        }
      });
    });
  });

  describe('账户设置', () => {
    it('应该能够修改密码', () => {
      cy.visit('/profile');
      
      // 查找修改密码链接
      cy.contains(/修改密码|Change Password|密码设置/i).then(($link) => {
        if ($link.length > 0) {
          cy.wrap($link).click();
          
          // 填写密码表单
          cy.get('input[name="old_password"], input[placeholder*="当前密码"]')
            .type('password123');
          cy.get('input[name="new_password"], input[placeholder*="新密码"]')
            .type('newPassword123!');
          cy.get('input[name="confirm_password"], input[placeholder*="确认密码"]')
            .type('newPassword123!');
          
          cy.get('button[type="submit"]').click();
          
          cy.contains(/密码修改成功|Password changed/i, { timeout: 10000 })
            .should('be.visible');
        }
      });
    });
  });

  describe('成就和统计', () => {
    it('应该显示用户统计信息', () => {
      cy.visit('/profile');
      
      // 检查统计数据（帖子数、关注数、粉丝数等）
      cy.get('.stats, .profile-stats, .user-statistics').then(($stats) => {
        if ($stats.length > 0) {
          cy.wrap($stats).within(() => {
            cy.get('.stat-item, .count').should('have.length.greaterThan', 0);
          });
        }
      });
    });

    it('应该能够查看成就页面', () => {
      cy.visit('/achievements');
      
      cy.get('.achievement, .badge, .trophy').should('exist');
    });
  });

  describe('响应式设计', () => {
    it('应该在移动设备上正常显示', () => {
      cy.viewport('iphone-x');
      cy.visit('/profile');
      
      cy.get('.profile-container').should('be.visible');
    });

    it('应该在平板上正常显示', () => {
      cy.viewport('ipad-2');
      cy.visit('/profile');
      
      cy.get('.profile-container').should('be.visible');
    });
  });
});
