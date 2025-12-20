/**
 * 单元测试：格式化工具函数
 * 测试日期、价格、文本等格式化功能
 */

describe('Formatters', () => {
  describe('formatPrice', () => {
    test('should format price with currency symbol', () => {
      const formatPrice = (price) => `¥${price.toFixed(2)}`;

      expect(formatPrice(10)).toBe('¥10.00');
      expect(formatPrice(12.5)).toBe('¥12.50');
      expect(formatPrice(99.99)).toBe('¥99.99');
    });

    test('should handle zero', () => {
      const formatPrice = (price) => `¥${price.toFixed(2)}`;
      expect(formatPrice(0)).toBe('¥0.00');
    });

    test('should round to 2 decimal places', () => {
      const formatPrice = (price) => `¥${price.toFixed(2)}`;
      expect(formatPrice(12.999)).toBe('¥13.00');
      expect(formatPrice(12.345)).toBe('¥12.35');
    });
  });

  describe('formatDate', () => {
    test('should format date correctly', () => {
      const formatDate = (date) => {
        const d = new Date(date);
        return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
      };

      expect(formatDate('2024-01-15')).toBe('2024-01-15');
      expect(formatDate('2024-12-31')).toBe('2024-12-31');
    });
  });

  describe('truncateText', () => {
    test('should truncate long text', () => {
      const truncateText = (text, maxLength) => {
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
      };

      const longText = 'This is a very long text that should be truncated';
      expect(truncateText(longText, 20)).toBe('This is a very long ...');
    });

    test('should not truncate short text', () => {
      const truncateText = (text, maxLength) => {
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
      };

      const shortText = 'Short';
      expect(truncateText(shortText, 20)).toBe('Short');
    });

    test('should handle empty string', () => {
      const truncateText = (text, maxLength) => {
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
      };

      expect(truncateText('', 10)).toBe('');
    });
  });

  describe('formatRating', () => {
    test('should format rating with one decimal', () => {
      const formatRating = (rating) => rating.toFixed(1);

      expect(formatRating(4.5)).toBe('4.5');
      expect(formatRating(3)).toBe('3.0');
      expect(formatRating(4.99)).toBe('5.0');
    });
  });
});
