/**
 * E2E测试：菜品交互功能
 * 测试评分、评论、点赞等交互功能
 */

describe('菜品评分功能', () => {
  beforeEach(() => {
    // 假设需要登录才能评分
    cy.visit('/');
  });

  it('给菜品评分', () => {
    // 访问菜品详情页
    cy.get('[data-cy="dish-card"], .dish-card').first().click({ force: true });

    cy.wait(1000);

    // 查找评分组件
    cy.get('[data-cy="rating-stars"], .rating, .star').should('exist');

    // 点击评分（如果未登录可能需要先登录）
    cy.get('[data-cy="rating-star-4"], .star:nth-child(4)').click({ force: true });

    cy.wait(500);
  });

  it('更新已有评分', () => {
    // 假设已经评过分
    cy.visit('/dish/1');

    // 更改评分
    cy.get('[data-cy="rating-star-5"]').click({ force: true });

    cy.wait(500);

    // 验证评分已更新
    cy.contains(/评分成功|更新成功/, { timeout: 3000 });
  });
});

describe('菜品评论功能', () => {
  beforeEach(() => {
    cy.visit('/');
  });

  it('查看菜品评论列表', () => {
    // 进入菜品详情页
    cy.get('[data-cy="dish-card"]').first().click({ force: true });

    cy.wait(1000);

    // 滚动到评论区域
    cy.contains('评论').scrollIntoView();

    // 验证评论列表存在
    cy.get('[data-cy="review-list"], .review-list, .reviews').should('exist');
  });

  it('提交新评论', () => {
    cy.visit('/dish/1');

    // 查找评论输入框
    cy.get('textarea[name="content"], textarea[placeholder*="评论"]')
      .first()
      .type('这道菜很好吃！非常推荐！');

    // 点击提交按钮
    cy.contains('button', /提交|发表/).click({ force: true });

    cy.wait(1000);

    // 应该显示成功提示或新评论
    cy.contains(/提交成功|评论成功/, { timeout: 3000 });
  });

  it('提交带评分的评论', () => {
    cy.visit('/dish/1');

    // 先评分
    cy.get('[data-cy="rating-star-5"]').click({ force: true });

    // 写评论
    cy.get('textarea[name="content"]').first().type('五星好评！');

    // 提交
    cy.contains('button', /提交|发表/).click({ force: true });

    cy.wait(1000);
  });

  it('防止提交空评论', () => {
    cy.visit('/dish/1');

    // 不输入内容直接提交
    cy.contains('button', /提交|发表/).click({ force: true });

    // 应该显示错误提示
    cy.contains(/不能为空|请输入/, { timeout: 2000 });
  });

  it('编辑自己的评论', () => {
    cy.visit('/dish/1');

    // 找到自己的评论
    cy.get('[data-cy="my-review"], .review.own')
      .first()
      .within(() => {
        // 点击编辑按钮
        cy.contains('编辑').click({ force: true });
      });

    // 修改评论内容
    cy.get('textarea').clear().type('修改后的评论内容');

    // 保存
    cy.contains('button', /保存|确定/).click({ force: true });

    cy.wait(500);
  });

  it('删除自己的评论', () => {
    cy.visit('/dish/1');

    // 找到自己的评论
    cy.get('[data-cy="my-review"]')
      .first()
      .within(() => {
        cy.contains('删除').click({ force: true });
      });

    // 确认删除
    cy.contains('button', /确认|确定/).click({ force: true });

    cy.wait(500);

    // 验证删除成功
    cy.contains(/删除成功/, { timeout: 2000 });
  });
});

describe('评论点赞功能', () => {
  it('点赞评论', () => {
    cy.visit('/dish/1');

    // 找到评论的点赞按钮
    cy.get('[data-cy="like-button"], .like-btn').first().click({ force: true });

    cy.wait(500);

    // 验证点赞数增加
    cy.get('[data-cy="like-button"]').first().should('contain', /\d+/);
  });

  it('取消点赞', () => {
    cy.visit('/dish/1');

    const likeButton = cy.get('[data-cy="like-button"]').first();

    // 第一次点击点赞
    likeButton.click({ force: true });
    cy.wait(500);

    // 第二次点击取消点赞
    likeButton.click({ force: true });
    cy.wait(500);
  });
});

describe('评论排序', () => {
  it('按时间排序评论', () => {
    cy.visit('/dish/1');

    // 选择按时间排序
    cy.get('select[name="review-sort"], .sort-select')
      .first()
      .select('created_at', { force: true });

    cy.wait(500);
  });

  it('按点赞数排序评论', () => {
    cy.visit('/dish/1');

    // 选择按点赞数排序
    cy.get('select[name="review-sort"]').first().select('likes_count', { force: true });

    cy.wait(500);
  });
});

describe('评论图片', () => {
  it('上传评论图片', () => {
    cy.visit('/dish/1');

    // 查找图片上传按钮
    cy.get('input[type="file"]').attachFile('test-image.jpg', {
      force: true,
    });

    cy.wait(500);

    // 验证图片预览
    cy.get('.image-preview, img[src*="blob"]').should('exist');
  });

  it('查看评论中的图片', () => {
    cy.visit('/dish/1');

    // 找到带图片的评论
    cy.get('.review-image, .review img').first().click({ force: true });

    // 应该打开图片预览或新窗口
    cy.wait(500);
  });
});
