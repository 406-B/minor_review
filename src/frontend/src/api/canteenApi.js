import { api } from './request'

// ==================== 食堂相关 API ====================

/**
 * 获取食堂列表
 * @param {Object} params - 查询参数
 * @param {string} params.search - 搜索食堂名称
 * @param {string} params.ordering - 排序方式：name, -name, created_at, -created_at
 * @returns {Promise<{code: number, message: string, data: Array}>}
 */
export const getCanteens = (params = {}) => {
  return api.get('/canteens/', { params });
};

/**
 * 获取食堂详情及菜品
 * @param {number} canteenId - 食堂 ID
 * @param {Object} params - 查询参数
 * @param {number[]} params.tag_ids - 按标签筛选（可多个）
 * @param {number} params.min_rating - 最低评分
 * @param {string} params.search - 关键词搜索
 * @param {string} params.ordering - 排序方式：rating, -rating, view_count, -view_count, price, -price, name, -name
 * @returns {Promise<{code: number, message: string, data: {canteen: Object, dishes: Array, dish_count: number}}>}
 */
export const getCanteenDetail = (canteenId, params = {}) => {
  return api.get(`/canteens/${canteenId}/`, { params });
};

// ==================== 楼层相关 API ====================
/**
 * 获取食堂楼层及窗口
 * @param {number} canteenId - 食堂 ID
 * @returns {Promise<{code: number, message: string, data: Array}>}
 */
export const getCanteenFloors = (canteenId) => {
  return api.get(`/canteens/${canteenId}/floors/`);
};
