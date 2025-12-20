/**
 * List API 封装
 * 使用 axios 调用后端 API
 *
 * 使用示例：
 * import { getCanteens, getDishDetail, rateDish } from '@/utils/api/listApi'
 *
 * // 获取食堂列表
 * const canteens = await getCanteens({ search: '第一' })
 *
 * // 获取菜品详情
 * const dish = await getDishDetail(1)
 *
 * // 给菜品评分（需要登录）
 * await rateDish(1, { rating: 4.5 })
 */

import axios from 'axios';

// 创建 axios 实例
const api = axios.create({
	baseURL: '/api', // 根据实际情况修改为后端地址，如 'http://localhost:8000/api'
	timeout: 10000,
	headers: {
		'Content-Type': 'application/json',
	},
});

// 请求拦截器 - 添加认证 token
api.interceptors.request.use(
	(config) => {
		// 统一支持多种 storage key，优先使用最新的 'jwt'
		let token = localStorage.getItem('jwt')
			|| localStorage.getItem('access_token')
			|| localStorage.getItem('token');
		if (token) {
			// 纠正可能已有 Bearer 前缀的情况
			if (token.toLowerCase().startsWith('bearer ')) {
				config.headers.Authorization = token;
			} else {
				config.headers.Authorization = `Bearer ${token}`;
			}
		} else {
			// 可选：开发环境下提示未登录
			if (import.meta && import.meta.env && import.meta.env.DEV) {
				console.warn('[listApi] 未找到JWT，部分需要登录的接口将返回403');
			}
		}
		return config;
	},
	(error) => Promise.reject(error)
);

// 响应拦截器 - 统一处理错误
api.interceptors.response.use(
	(response) => {
		// 统一处理响应格式
		// 如果后端返回的是 { code, message, data } 格式，直接返回 data
		if (response.data && typeof response.data === 'object' && 'data' in response.data) {
			return response.data;
		}
		return response.data;
	},
	(error) => {
		// 处理错误响应
		const message = error.response?.data?.message || error.message || '请求失败';

		// 处理 401 未授权
		if (error.response?.status === 401) {
			// 可以在这里跳转到登录页
			console.error('未授权，请先登录');
		}

		// 处理 403 禁止访问
		if (error.response?.status === 403) {
			console.error('没有权限访问该资源');
		}

		return Promise.reject({
			code: error.response?.status || 500,
			message,
			errors: error.response?.data?.errors || {},
		});
	}
);

// ==================== 食堂相关 API ====================

/**
 * 获取食堂楼层与窗口
 * @param {number|string} canteenId - 食堂ID
 * @returns {Promise<{code: number, message: string, data: Array}>}
 */
export const getCanteenFloors = (canteenId) => {
	return api.get(`/canteens/${canteenId}/floors/`);
};

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

// ==================== 菜品相关 API ====================

/**
 * 获取菜品列表
 * @param {Object} params - 查询参数
 * @param {number} params.canteen_id - 按食堂筛选
 * @param {number[]} params.tag_ids - 按标签筛选（可多个）
 * @param {number} params.min_rating - 最低评分
 * @param {number} params.min_price - 最低价格
 * @param {number} params.max_price - 最高价格
 * @param {string} params.search - 关键词搜索
 * @param {string} params.ordering - 排序方式：rating, -rating, view_count, -view_count, price, -price, name, -name
 * @returns {Promise<{code: number, message: string, data: Array}>}
 */
export const getDishes = (params = {}) => {
	return api.get('/dishes/', { params });
};

/**
 * 获取菜品详情
 * @param {number} dishId - 菜品 ID
 * @returns {Promise<{code: number, message: string, data: Object}>}
 */
export const getDishDetail = (dishId) => {
	return api.get(`/dishes/${dishId}/`);
};

/**
 * 获取热门菜品
 * @param {Object} params - 查询参数
 * @param {number} params.limit - 返回数量，默认 10
 * @returns {Promise<{code: number, message: string, data: Array}>}
 */
export const getHotDishes = (params = { limit: 10 }) => {
	return api.get('/dishes/hot/', { params });
};

/**
 * 获取新品菜品
 * @param {Object} params - 查询参数
 * @param {number} params.limit - 返回数量，默认 10
 * @returns {Promise<{code: number, message: string, data: Array}>}
 */
export const getNewDishes = (params = { limit: 10 }) => {
	return api.get('/dishes/new/', { params });
};

/**
 * 给菜品评分（需登录）
 * @param {number} dishId - 菜品 ID
 * @param {Object} data - 评分数据
 * @param {number} data.rating - 评分值，0-5
 * @returns {Promise<{code: number, message: string, data: {dish_id: number, new_rating: number}}>}
 */
export const rateDish = (dishId, data) => {
	return api.post(`/dishes/${dishId}/rate/`, data);
};

/**
 * 给菜品添加标签（需登录）
 * @param {number} dishId - 菜品 ID
 * @param {Object} data - 标签数据
 * @param {number[]} [data.tag_ids] - 现有标签ID列表
 * @param {string} [data.tag_name] - 新标签名称
 * @returns {Promise<{code: number, message: string, data: Object}>}
 */
export const addTagToDish = (dishId, data) => {
	return api.post(`/dishes/${dishId}/tags/`, data);
};

/**
 * 批准待审核标签（需管理员权限）
 * @param {number} dishId - 菜品 ID
 * @param {Object} data - 标签数据
 * @param {number[]} [data.tag_ids] - 要批准的标签ID列表，留空则批准所有
 * @returns {Promise<{code: number, message: string, data: Object}>}
 */
export const approvePendingTags = (dishId, data = {}) => {
	return api.post(`/dishes/${dishId}/tags/approve/`, data);
};

/**
 * 拒绝待审核标签（需管理员权限）
 * @param {number} dishId - 菜品 ID
 * @param {Object} data - 标签数据
 * @param {number[]} data.tag_ids - 要拒绝的标签ID列表
 * @returns {Promise<{code: number, message: string, data: Object}>}
 */
export const rejectPendingTags = (dishId, data) => {
	return api.post(`/dishes/${dishId}/tags/reject/`, data);
};

// ==================== 标签相关 API ====================

/**
 * 获取所有标签
 * @returns {Promise<{code: number, message: string, data: Array}>}
 */
export const getTags = () => {
	return api.get('/tags/');
};

/**
 * 创建新标签（需管理员权限）
 * @param {Object} data - 标签数据
 * @param {string} data.name - 标签名称
 * @returns {Promise<{code: number, message: string, data: Object}>}
 */
export const createTag = (data) => {
	return api.post('/tags/create/', data);
};

// ==================== 评论相关 API ====================

/**
 * 获取菜品评论列表
 * @param {number} dishId - 菜品 ID
 * @param {Object} params - 查询参数
 * @param {string} params.search - 搜索评论内容或用户名
 * @param {string} params.ordering - 排序方式：created_at, -created_at, likes_count, -likes_count
 * @returns {Promise<{code: number, message: string, data: {reviews: Array, total: number}}>}
 */
export const getReviews = (dishId, params = {}) => {
	return api.get(`/dishes/${dishId}/reviews/`, { params });
};

/**
 * 创建评论（需登录）
 * @param {number} dishId - 菜品 ID
 * @param {Object} data - 评论数据
 * @param {string} data.content - 评论内容（至少5个字符）
 * @param {string[]} [data.images] - 图片URL列表（最多9张）
 * @param {number} [data.rating_score] - 评分，1.0-5.0（可选）
 * @returns {Promise<{code: number, message: string, data: Object}>}
 */
export const createReview = (dishId, data) => {
	return api.post(`/dishes/${dishId}/reviews/create/`, data);
};

/**
 * 更新评论（需登录，仅本人）
 * @param {number} reviewId - 评论 ID
 * @param {Object} data - 评论数据（可部分更新）
 * @param {string} [data.content] - 评论内容
 * @param {string[]} [data.images] - 图片URL列表
 * @returns {Promise<{code: number, message: string, data: Object}>}
 */
export const updateReview = (reviewId, data) => {
	return api.put(`/reviews/${reviewId}/`, data);
};

/**
 * 部分更新评论（需登录，仅本人）
 * @param {number} reviewId - 评论 ID
 * @param {Object} data - 评论数据（可部分更新）
 * @returns {Promise<{code: number, message: string, data: Object}>}
 */
export const patchReview = (reviewId, data) => {
	return api.patch(`/reviews/${reviewId}/`, data);
};

/**
 * 删除评论（需登录，仅本人或管理员）
 * @param {number} reviewId - 评论 ID
 * @returns {Promise<{code: number, message: string}>}
 */
export const deleteReview = (reviewId) => {
	return api.delete(`/reviews/${reviewId}/delete/`);
};

/**
 * 点赞/取消点赞评论（需登录）
 * @param {number} reviewId - 评论 ID
 * @returns {Promise<{code: number, message: string, data: Object}>}
 */
export const likeReview = (reviewId) => {
	return api.post(`/reviews/${reviewId}/like/`);
};

/**
 * 获取我的评论（需登录）
 * @returns {Promise<{code: number, message: string, data: {reviews: Array, total: number}}>}
 */
export const getMyReviews = () => {
	return api.get('/reviews/my/');
};

// 导出默认 axios 实例，方便直接使用
export default api;

// ==================== 成就 / 打卡相关 API ====================

/**
 * 菜品打卡（需登录）
 * POST /dishes/{dishId}/check-in/
 * @param {number} dishId - 菜品ID
 * @param {Object} data - 可选参数，如 { notes: '好吃' }
 * @returns {Promise<{code:number, message:string, data:Object}>}
 */
export const checkInDish = (dishId, data = {}) => {
	return api.post(`/dishes/${dishId}/check-in/`, data);
};

/**
 * 获取用户菜品历史（需登录）
 * GET /user/dish-history/
 * @param {Object} params - { page, page_size, level, ordering }
 * @returns {Promise<{code:number, message:string, data:{histories:Array, total:number}}>} 
 */
export const getUserDishHistory = (params = {}) => {
	return api.get('/user/dish-history/', { params });
};

/** 可选：用户成就统计（需登录） */
export const getUserDishStats = () => {
	return api.get('/user/dish-stats/');
};

/** 可选：美食日历（需登录） */
export const getFoodCalendar = (params = {}) => {
	return api.get('/user/food-calendar/', { params });
};
