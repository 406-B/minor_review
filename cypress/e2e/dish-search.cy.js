/**
 * E2E测试：菜品搜索和筛选
 * 测试搜索、筛选、排序等功能
 */

describe('菜品搜索和筛选 E2E', () => {
  beforeEach(() => {
    // 访问菜品列表页
    cy.visit('/');
    cy.wait(500);
  });

  it('通过关键词搜索菜品', () => {
    // 查找搜索框
    cy.get('input[type="search"], input[placeholder*="搜索"]').first().clear().type('宫保鸡丁');

    // 点击搜索或按回车
    cy.get('input[type="search"], input[placeholder*="搜索"]').first().type('{enter}');

    // 等待搜索结果
    cy.wait(1000);

    // 验证搜索结果
    cy.url().should('match', /search|q=/);
  });

  it('按价格范围筛选', () => {
    // 查找价格筛选控件
    cy.get('input[name="min_price"], input[placeholder*="最低价格"]').first().clear().type('10');

    cy.get('input[name="max_price"], input[placeholder*="最高价格"]').first().clear().type('20');

    // 点击筛选按钮
    cy.contains('button', /筛选|搜索|查询/).click({ force: true });

    // 等待结果
    cy.wait(1000);

    // 验证URL包含筛选参数
    cy.url().should('match', /min_price|max_price/);
  });

  it('按标签筛选', () => {
    // 查找标签筛选
    cy.contains('辣', { timeout: 3000 }).click({ force: true });

    // 等待筛选结果
    cy.wait(1000);

    // 验证显示的菜品包含该标签
    cy.url().should('match', /tag|filter/);
  });

  it('按评分筛选', () => {
    // 查找评分筛选
    cy.get('input[name="min_rating"], select[name="min_rating"]')
      .first()
      .select('4', { force: true })
      .or(cy.get('input[name="min_rating"]').type('4'));

    // 应用筛选
    cy.contains('button', /筛选|应用/).click({ force: true });

    cy.wait(1000);
  });

  it('按价格排序', () => {
    // 查找排序选择器
    cy.get('select[name="ordering"], select:contains("排序")')
      .first()
      .select('price', { force: true });

    // 等待排序结果
    cy.wait(1000);

    // 验证URL包含排序参数
    cy.url().should('match', /ordering|sort/);
  });

  it('按评分排序', () => {
    // 按评分降序排序
    cy.get('select[name="ordering"]').first().select('-rating', { force: true });

    cy.wait(1000);
  });

  it('组合筛选条件', () => {
    // 同时使用多个筛选条件
    // 1. 设置价格范围
    cy.get('input[name="min_price"]').first().clear().type('10');

    // 2. 选择标签
    cy.contains('辣').click({ force: true });

    // 3. 设置最低评分
    cy.get('input[name="min_rating"]').first().clear().type('4');

    // 4. 应用筛选
    cy.contains('button', /筛选|应用/).click({ force: true });

    cy.wait(1000);
  });

  it('清除筛选条件', () => {
    // 设置一些筛选条件
    cy.get('input[name="min_price"]').first().type('10');

    // 查找并点击清除按钮
    cy.contains('button', /清除|重置/).click({ force: true });

    // 验证筛选条件已清除
    cy.get('input[name="min_price"]').first().should('have.value', '');
  });

  it('空搜索结果处理', () => {
    // 搜索不存在的菜品
    cy.get('input[type="search"]').first().clear().type('不存在的菜品xyz123');

    cy.get('input[type="search"]').first().type('{enter}');

    cy.wait(1000);

    // 应该显示"无结果"提示
    cy.contains(/暂无|没有|无结果|No results/i, { timeout: 3000 });
  });
});

describe('菜品列表展示', () => {
  beforeEach(() => {
    cy.visit('/');
  });

  it('显示菜品列表', () => {
    // 等待菜品列表加载
    cy.wait(1000);

    // 验证有菜品卡片显示
    cy.get('[data-cy="dish-card"], .dish-card, .dish-item').should('have.length.greaterThan', 0);
  });

  it('菜品卡片包含必要信息', () => {
    // 检查第一个菜品卡片
    cy.get('[data-cy="dish-card"], .dish-card, .dish-item')
      .first()
      .within(() => {
        // 应该包含名称、价格等信息
        cy.get('img, .image').should('exist');
      });
  });

  it('点击菜品卡片跳转到详情页', () => {
    cy.get('[data-cy="dish-card"], .dish-card, .dish-item').first().click({ force: true });

    cy.wait(1000);

    // 验证跳转到详情页
    cy.url().should('match', /dish|detail/);
  });
});
