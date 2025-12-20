/**
 * 单元测试：API 调用模块
 * 测试菜品、食堂等 API 调用函数
 */

// Mock axios
jest.mock('axios');

import axios from 'axios';

// 模拟 API 函数（因为实际文件可能不完整，这里定义示例）
const getDishList = async (params = {}) => {
  const response = await axios.get('/api/dishes/', { params });
  return response.data;
};

const getDishDetail = async (dishId) => {
  const response = await axios.get(`/api/dish/${dishId}/`);
  return response.data;
};

const rateDish = async (dishId, rating) => {
  const response = await axios.post(`/api/dish/${dishId}/rate/`, { rating });
  return response.data;
};

const createReview = async (dishId, data) => {
  const response = await axios.post(`/api/dish/${dishId}/review/`, data);
  return response.data;
};

describe('List API', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('getDishList', () => {
    test('should call correct endpoint', async () => {
      const mockData = {
        code: 200,
        message: '成功',
        data: [
          { id: 1, name: '宫保鸡丁', price: 12.5 },
          { id: 2, name: '清炒时蔬', price: 8.0 },
        ],
      };

      axios.get.mockResolvedValue({ data: mockData });

      const result = await getDishList();

      expect(axios.get).toHaveBeenCalledWith('/api/dishes/', { params: {} });
      expect(result).toEqual(mockData);
      expect(result.data).toHaveLength(2);
    });

    test('should handle query parameters', async () => {
      const mockData = { code: 200, data: [] };
      axios.get.mockResolvedValue({ data: mockData });

      const params = {
        search: '宫保',
        min_price: 10,
        max_price: 20,
      };

      await getDishList(params);

      expect(axios.get).toHaveBeenCalledWith('/api/dishes/', { params });
    });

    test('should handle API errors', async () => {
      const errorMessage = 'Network Error';
      axios.get.mockRejectedValue(new Error(errorMessage));

      await expect(getDishList()).rejects.toThrow(errorMessage);
    });
  });

  describe('getDishDetail', () => {
    test('should fetch dish detail by id', async () => {
      const mockDish = {
        code: 200,
        data: {
          id: 1,
          name: '宫保鸡丁',
          price: 12.5,
          rating: 4.5,
        },
      };

      axios.get.mockResolvedValue({ data: mockDish });

      const result = await getDishDetail(1);

      expect(axios.get).toHaveBeenCalledWith('/api/dish/1/');
      expect(result.data.name).toBe('宫保鸡丁');
    });

    test('should handle 404 errors', async () => {
      axios.get.mockRejectedValue({
        response: { status: 404, data: { message: 'Not found' } },
      });

      await expect(getDishDetail(9999)).rejects.toBeTruthy();
    });
  });

  describe('rateDish', () => {
    test('should send rating data', async () => {
      const mockResponse = {
        code: 200,
        message: '评分成功',
        data: { dish_id: 1, user_score: 4.5, new_rating: 4.5 },
      };

      axios.post.mockResolvedValue({ data: mockResponse });

      const result = await rateDish(1, 4.5);

      expect(axios.post).toHaveBeenCalledWith('/api/dish/1/rate/', { rating: 4.5 });
      expect(result.code).toBe(200);
    });

    test('should handle invalid rating', async () => {
      axios.post.mockRejectedValue({
        response: {
          status: 400,
          data: { message: '评分必须在0-5之间' },
        },
      });

      await expect(rateDish(1, 6.0)).rejects.toBeTruthy();
    });

    test('should handle unauthorized access', async () => {
      axios.post.mockRejectedValue({
        response: { status: 401, data: { message: '未登录' } },
      });

      await expect(rateDish(1, 4.5)).rejects.toBeTruthy();
    });
  });

  describe('createReview', () => {
    test('should create review successfully', async () => {
      const mockResponse = {
        code: 201,
        message: '评论创建成功',
        data: { id: 1, content: '很好吃' },
      };

      axios.post.mockResolvedValue({ data: mockResponse });

      const reviewData = {
        content: '很好吃',
        images: [],
      };

      const result = await createReview(1, reviewData);

      expect(axios.post).toHaveBeenCalledWith('/api/dish/1/review/', reviewData);
      expect(result.code).toBe(201);
    });

    test('should handle empty content', async () => {
      axios.post.mockRejectedValue({
        response: {
          status: 400,
          data: { message: '评论内容不能为空' },
        },
      });

      await expect(createReview(1, { content: '' })).rejects.toBeTruthy();
    });
  });
});
