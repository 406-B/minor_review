/**
 * 集成测试：Profile API 调用
 * 测试个人资料相关API的完整调用流程
 */

import { describe, test, expect, beforeEach, vi } from 'vitest';
import axios from 'axios';

// Mock axios
vi.mock('axios');
import {
  getProfile,
  updateProfile,
  updatePassword,
  getUserStats,
  getMyPosts,
  getLikedPosts,
  getMyComments,
  getPreferenceTags,
  setPreferenceTags,
  getRecommendedDishes,
} from '../profile';

describe('Profile API', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('getProfile', () => {
    test('should fetch user profile successfully', async () => {
      const mockProfile = {
        id: 1,
        username: 'testuser',
        nickname: '测试用户',
        avatar: '/avatars/user1.jpg',
        created: '2024-01-01T00:00:00Z',
      };

      axios.get.mockResolvedValue({ data: mockProfile });

      const result = await getProfile();

      expect(axios.get).toHaveBeenCalledWith('/api/profile/');
      expect(result).toEqual(mockProfile);
    });

    test('should handle API errors', async () => {
      axios.get.mockRejectedValue(new Error('Network Error'));

      await expect(getProfile()).rejects.toThrow('Network Error');
    });

    test('should handle 401 unauthorized', async () => {
      axios.get.mockRejectedValue({
        response: { status: 401, data: { message: '未登录' } },
      });

      await expect(getProfile()).rejects.toBeTruthy();
    });
  });

  describe('updateProfile', () => {
    test('should update profile with nickname only', async () => {
      const updateData = { nickname: '新昵称' };
      const mockResponse = {
        message: '更新成功',
        data: { id: 1, nickname: '新昵称' },
      };

      axios.put.mockResolvedValue({ data: mockResponse });

      const result = await updateProfile(updateData);

      expect(axios.put).toHaveBeenCalledWith('/api/profile/', updateData);
      expect(result).toEqual(mockResponse);
    });

    test('should update profile with avatar file', async () => {
      const formData = new FormData();
      formData.append('nickname', '新昵称');
      formData.append('avatar', new File([''], 'avatar.jpg'));

      const mockResponse = { message: '更新成功' };
      axios.put.mockResolvedValue({ data: mockResponse });

      const result = await updateProfile(null, formData);

      expect(axios.put).toHaveBeenCalledWith('/api/profile/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      expect(result).toEqual(mockResponse);
    });

    test('should handle validation errors', async () => {
      axios.put.mockRejectedValue({
        response: { status: 400, data: { errors: { nickname: ['昵称过长'] } } },
      });

      await expect(updateProfile({ nickname: 'a'.repeat(100) })).rejects.toBeTruthy();
    });
  });

  describe('updatePassword', () => {
    test('should update password successfully', async () => {
      const passwordData = {
        old_password: 'oldpass123',
        new_password: 'newpass456',
        confirm_password: 'newpass456',
      };

      const mockResponse = { message: '密码修改成功' };
      axios.post.mockResolvedValue({ data: mockResponse });

      const result = await updatePassword(passwordData);

      expect(axios.post).toHaveBeenCalledWith('/api/profile/update-password/', passwordData);
      expect(result).toEqual(mockResponse);
    });

    test('should handle wrong old password', async () => {
      axios.post.mockRejectedValue({
        response: { status: 400, data: { message: '旧密码错误' } },
      });

      await expect(
        updatePassword({
          old_password: 'wrong',
          new_password: 'new',
          confirm_password: 'new',
        })
      ).rejects.toBeTruthy();
    });

    test('should handle password mismatch', async () => {
      axios.post.mockRejectedValue({
        response: { status: 400, data: { errors: { confirm_password: ['密码不一致'] } } },
      });

      await expect(
        updatePassword({
          old_password: 'old',
          new_password: 'new1',
          confirm_password: 'new2',
        })
      ).rejects.toBeTruthy();
    });
  });

  describe('getUserStats', () => {
    test('should fetch user statistics', async () => {
      const mockStats = {
        liked_posts_count: 5,
        commented_posts_count: 3,
        following_count: 2,
      };

      axios.get.mockResolvedValue({ data: mockStats });

      const result = await getUserStats();

      expect(axios.get).toHaveBeenCalledWith('/api/profile/stats/');
      expect(result).toEqual(mockStats);
    });
  });

  describe('getMyPosts', () => {
    test('should fetch user posts with pagination', async () => {
      const mockResponse = {
        code: 200,
        data: {
          posts: [
            { id: 1, subject: '我的帖子1' },
            { id: 2, subject: '我的帖子2' },
          ],
          pagination: {
            total: 5,
            page: 1,
            page_size: 20,
            total_pages: 1,
          },
        },
      };

      axios.get.mockResolvedValue({ data: mockResponse });

      const result = await getMyPosts(1, 20);

      expect(axios.get).toHaveBeenCalledWith('/api/profile/my-posts/', {
        params: { page: 1, page_size: 20 },
      });
      expect(result).toEqual(mockResponse);
    });

    test('should use default pagination parameters', async () => {
      const mockResponse = { code: 200, data: { posts: [], pagination: {} } };
      axios.get.mockResolvedValue({ data: mockResponse });

      await getMyPosts();

      expect(axios.get).toHaveBeenCalledWith('/api/profile/my-posts/', {
        params: { page: 1, page_size: 20 },
      });
    });
  });

  describe('getLikedPosts', () => {
    test('should fetch liked posts', async () => {
      const mockResponse = {
        code: 200,
        data: {
          posts: [{ id: 1, subject: '喜欢的帖子' }],
          pagination: { total: 1, page: 1, page_size: 20, total_pages: 1 },
        },
      };

      axios.get.mockResolvedValue({ data: mockResponse });

      const result = await getLikedPosts(1, 10);

      expect(axios.get).toHaveBeenCalledWith('/api/profile/liked-posts/', {
        params: { page: 1, page_size: 10 },
      });
      expect(result).toEqual(mockResponse);
    });
  });

  describe('getMyComments', () => {
    test('should fetch user comments', async () => {
      const mockResponse = {
        code: 200,
        data: {
          comments: [{ id: 1, content: '我的评论', post_subject: '帖子标题' }],
          pagination: { total: 1, page: 1, page_size: 20, total_pages: 1 },
        },
      };

      axios.get.mockResolvedValue({ data: mockResponse });

      const result = await getMyComments();

      expect(axios.get).toHaveBeenCalledWith('/api/profile/my-comments/', {
        params: { page: 1, page_size: 20 },
      });
      expect(result).toEqual(mockResponse);
    });
  });

  describe('getPreferenceTags', () => {
    test('should fetch user preference tags', async () => {
      const mockResponse = {
        code: 200,
        message: '获取偏好标签成功',
        data: [
          { id: 1, name: '辣' },
          { id: 2, name: '素食' },
        ],
      };

      axios.get.mockResolvedValue({ data: mockResponse });

      const result = await getPreferenceTags();

      expect(axios.get).toHaveBeenCalledWith('/api/profile/preference-tags/');
      expect(result).toEqual(mockResponse);
    });
  });

  describe('setPreferenceTags', () => {
    test('should set preference tags', async () => {
      const tagIds = [1, 2, 3];
      const mockResponse = {
        code: 200,
        message: '偏好标签设置成功',
        data: [
          { id: 1, name: '辣' },
          { id: 2, name: '甜' },
          { id: 3, name: '素食' },
        ],
      };

      axios.post.mockResolvedValue({ data: mockResponse });

      const result = await setPreferenceTags(tagIds);

      expect(axios.post).toHaveBeenCalledWith('/api/profile/preference-tags/', { tag_ids: tagIds });
      expect(result).toEqual(mockResponse);
    });

    test('should handle empty tag list', async () => {
      const mockResponse = { code: 200, message: '偏好标签设置成功', data: [] };
      axios.post.mockResolvedValue({ data: mockResponse });

      const result = await setPreferenceTags([]);

      expect(axios.post).toHaveBeenCalledWith('/api/profile/preference-tags/', { tag_ids: [] });
      expect(result).toEqual(mockResponse);
    });
  });

  describe('getRecommendedDishes', () => {
    test('should fetch recommended dishes', async () => {
      const mockResponse = {
        code: 200,
        message: '获取推荐菜品成功',
        data: {
          dishes: [
            { id: 1, name: '辣子鸡丁', price: 15.0 },
            { id: 2, name: '麻婆豆腐', price: 12.0 },
          ],
          total: 2,
          page: 1,
          page_size: 20,
          user_tags: [{ id: 1, name: '辣' }],
        },
      };

      axios.get.mockResolvedValue({ data: mockResponse });

      const result = await getRecommendedDishes(1, 20);

      expect(axios.get).toHaveBeenCalledWith('/api/profile/recommended-dishes/', {
        params: { page: 1, page_size: 20 },
      });
      expect(result).toEqual(mockResponse);
    });

    test('should handle no preferences set', async () => {
      axios.get.mockRejectedValue({
        response: { status: 404, data: { message: '用户未设置偏好标签' } },
      });

      await expect(getRecommendedDishes()).rejects.toBeTruthy();
    });
  });

  describe('Error handling', () => {
    test('should handle network errors', async () => {
      axios.get.mockRejectedValue(new Error('Network timeout'));

      await expect(getProfile()).rejects.toThrow('Network timeout');
    });

    test('should handle server errors', async () => {
      axios.get.mockRejectedValue({
        response: { status: 500, data: { message: '服务器内部错误' } },
      });

      await expect(getProfile()).rejects.toBeTruthy();
    });

    test('should handle authentication errors', async () => {
      axios.get.mockRejectedValue({
        response: { status: 401, data: { message: '认证失败' } },
      });

      await expect(getProfile()).rejects.toBeTruthy();
    });

    test('should handle validation errors', async () => {
      axios.post.mockRejectedValue({
        response: { status: 400, data: { errors: { tag_ids: ['标签ID无效'] } } },
      });

      await expect(setPreferenceTags([999])).rejects.toBeTruthy();
    });
  });

  describe('Request timeout', () => {
    test('should handle request timeouts', async () => {
      axios.get.mockImplementation(
        () =>
          new Promise((resolve, reject) => {
            setTimeout(() => reject(new Error('Timeout')), 100);
          })
      );

      const timeoutPromise = new Promise((resolve, reject) => {
        setTimeout(() => reject(new Error('Request timeout')), 50);
      });

      await expect(Promise.race([getProfile(), timeoutPromise])).rejects.toThrow('Request timeout');
    });
  });
});
