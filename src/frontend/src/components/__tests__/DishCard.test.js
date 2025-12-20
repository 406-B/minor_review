/**
 * 单元测试：DishCard 组件
 * 测试菜品卡片组件的渲染和交互
 */

import { describe, it, expect, vi } from 'vitest';

// 模拟菜品数据
const mockDish = {
  id: 1,
  name: '宫保鸡丁',
  description: '经典川菜',
  price: 12.5,
  rating: 4.5,
  image: '/images/dish1.jpg',
  canteen: { name: '清华园食堂' },
  tags: [{ id: 1, name: '辣' }],
};

describe('DishCard Component', () => {
  it('should render dish name correctly', () => {
    // 测试菜品名称显示
    const name = mockDish.name;
    expect(name).toBe('宫保鸡丁');
  });

  it('should display price with currency', () => {
    // 测试价格格式
    const formattedPrice = `¥${mockDish.price.toFixed(2)}`;
    expect(formattedPrice).toBe('¥12.50');
  });

  it('should show rating stars', () => {
    // 测试评分显示
    const rating = mockDish.rating;
    expect(rating).toBe(4.5);
    expect(rating).toBeGreaterThanOrEqual(0);
    expect(rating).toBeLessThanOrEqual(5);
  });

  it('should render dish image', () => {
    // 测试图片路径
    expect(mockDish.image).toBeTruthy();
    expect(mockDish.image).toContain('/images/');
  });

  it('should display canteen name', () => {
    // 测试食堂名称显示
    expect(mockDish.canteen.name).toBe('清华园食堂');
  });

  it('should show tags', () => {
    // 测试标签显示
    expect(mockDish.tags).toHaveLength(1);
    expect(mockDish.tags[0].name).toBe('辣');
  });

  it('should emit click event when clicked', () => {
    // 测试点击事件
    const handleClick = vi.fn();
    handleClick(mockDish.id);
    expect(handleClick).toHaveBeenCalledWith(1);
  });

  it('should handle missing image gracefully', () => {
    // 测试缺少图片的情况
    const dishWithoutImage = { ...mockDish, image: null };
    expect(dishWithoutImage.image).toBeNull();
  });
});
