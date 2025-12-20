// Example Jest unit test

describe('Helper Functions', () => {
  test('should pass basic test', () => {
    expect(true).toBe(true);
  });

  test('should calculate sum correctly', () => {
    const sum = (a, b) => a + b;
    expect(sum(2, 3)).toBe(5);
    expect(sum(-1, 1)).toBe(0);
  });

  test('should handle async operations', async () => {
    const asyncFunction = async () => {
      return new Promise((resolve) => {
        setTimeout(() => resolve('completed'), 10);
      });
    };

    const result = await asyncFunction();
    expect(result).toBe('completed');
  });
});
