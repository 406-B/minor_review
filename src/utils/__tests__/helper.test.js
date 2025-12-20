/**
 * 单元测试：工具函数
 * 测试 helper.js 中的基础工具函数
 */

import { add, subtract, multiply, divide } from '../helper';

describe('Math Helper Functions', () => {
  describe('add', () => {
    test('should add two positive numbers', () => {
      expect(add(2, 3)).toBe(5);
      expect(add(10, 20)).toBe(30);
    });

    test('should add negative numbers', () => {
      expect(add(-1, -1)).toBe(-2);
      expect(add(-5, -10)).toBe(-15);
    });

    test('should add mixed positive and negative numbers', () => {
      expect(add(-1, 1)).toBe(0);
      expect(add(10, -5)).toBe(5);
    });

    test('should handle zero', () => {
      expect(add(0, 5)).toBe(5);
      expect(add(5, 0)).toBe(5);
      expect(add(0, 0)).toBe(0);
    });

    test('should handle decimal numbers', () => {
      expect(add(1.5, 2.5)).toBe(4);
      expect(add(0.1, 0.2)).toBeCloseTo(0.3);
    });
  });

  describe('subtract', () => {
    test('should subtract two positive numbers', () => {
      expect(subtract(5, 3)).toBe(2);
      expect(subtract(20, 10)).toBe(10);
    });

    test('should subtract negative numbers', () => {
      expect(subtract(-5, -3)).toBe(-2);
      expect(subtract(-10, -5)).toBe(-5);
    });

    test('should handle zero', () => {
      expect(subtract(5, 0)).toBe(5);
      expect(subtract(0, 5)).toBe(-5);
      expect(subtract(0, 0)).toBe(0);
    });

    test('should result in negative when second number is larger', () => {
      expect(subtract(3, 5)).toBe(-2);
    });
  });

  describe('multiply', () => {
    test('should multiply two positive numbers', () => {
      expect(multiply(2, 3)).toBe(6);
      expect(multiply(5, 4)).toBe(20);
    });

    test('should multiply negative numbers', () => {
      expect(multiply(-2, 3)).toBe(-6);
      expect(multiply(-2, -3)).toBe(6);
    });

    test('should handle zero', () => {
      expect(multiply(0, 5)).toBe(0);
      expect(multiply(5, 0)).toBe(0);
      expect(multiply(0, 0)).toBe(0);
    });

    test('should handle decimal numbers', () => {
      expect(multiply(2.5, 2)).toBe(5);
      expect(multiply(1.5, 3)).toBe(4.5);
    });
  });

  describe('divide', () => {
    test('should divide two positive numbers', () => {
      expect(divide(6, 2)).toBe(3);
      expect(divide(20, 4)).toBe(5);
    });

    test('should divide negative numbers', () => {
      expect(divide(-6, 2)).toBe(-3);
      expect(divide(6, -2)).toBe(-3);
      expect(divide(-6, -2)).toBe(3);
    });

    test('should handle decimal results', () => {
      expect(divide(5, 2)).toBe(2.5);
      expect(divide(1, 3)).toBeCloseTo(0.333, 2);
    });

    test('should throw error when dividing by zero', () => {
      expect(() => divide(5, 0)).toThrow('Cannot divide by zero');
      expect(() => divide(0, 0)).toThrow('Cannot divide by zero');
    });

    test('should handle zero dividend', () => {
      expect(divide(0, 5)).toBe(0);
    });
  });
});
