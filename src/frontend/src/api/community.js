// 社区论坛 API
import request from './request'

const BASE_URL = '/v1'

// ============ 帖子相关接口 ============

/**
 * 获取帖子列表
 * @param {number} page - 页码，默认 1
 * @param {number} page_size - 每页数量，默认 20
 * @returns {Promise}
 */
export const getPostList = async (page = 1, page_size = 20) => {
  try {
    const response = await request.get(`${BASE_URL}/posts/`, {
      params: { page, page_size }
    })
    return response
  } catch (err) {
    throw err
  }
}

/**
 * 获取帖子详情
 * @param {number} postId - 帖子ID
 * @returns {Promise}
 */
export const getPostDetail = async (postId) => {
  try {
    const response = await request.get(`${BASE_URL}/posts/${postId}/`)
    return response
  } catch (err) {
    throw err
  }
}

/**
 * 创建帖子
 * @param {string} subject - 帖子标题
 * @param {string} content - 帖子内容
 * @param {Array<string>} images - 图片URL列表，可选，最多9张
 * @param {number} dish - 关联菜品ID，可选
 * @returns {Promise}
 */
export const createPost = async (subject, content, images = [], dish = null) => {
  try {
    const data = { subject, content }
    
    // 添加可选参数
    if (images && images.length > 0) {
      data.images = images
    }
    if (dish) {
      data.dish = dish
    }
    
    const response = await request.post(`${BASE_URL}/posts/create/`, data)
    return response
  } catch (err) {
    throw err
  }
}

/**
 * 删除帖子
 * @param {number} postId - 帖子ID
 * @returns {Promise}
 */
export const deletePost = async (postId) => {
  try {
    const response = await request.delete(`${BASE_URL}/posts/${postId}/delete/`)
    return response
  } catch (err) {
    throw err
  }
}

/**
 * 切换帖子点赞
 * @param {number} postId - 帖子ID
 * @returns {Promise}
 */
export const togglePostLike = async (postId) => {
  try {
    const response = await request.post(`${BASE_URL}/posts/${postId}/like/`, {})
    return response
  } catch (err) {
    throw err
  }
}

// ============ 评论相关接口 ============

/**
 * 获取帖子评论列表
 * @param {number} postId - 帖子ID
 * @param {number} page - 页码，默认 1
 * @param {number} page_size - 每页数量，默认 20
 * @returns {Promise}
 */
export const getCommentList = async (postId, page = 1, page_size = 20) => {
  try {
    const response = await request.get(`${BASE_URL}/posts/${postId}/comments/`, {
      params: { page, page_size }
    })
    return response
  } catch (err) {
    throw err
  }
}

/**
 * 创建评论
 * @param {number} postId - 帖子ID
 * @param {string} content - 评论内容
 * @param {Array<string>} images - 图片URL列表，可选，最多9张
 * @param {number} parent - 父评论ID，可选（用于回复）
 * @returns {Promise}
 */
export const createComment = async (postId, content, images = [], parent = null) => {
  try {
    const data = { post: postId, content }
    
    // 添加可选参数
    if (images && images.length > 0) {
      data.images = images
    }
    if (parent) {
      data.parent = parent
    }
    
    const response = await request.post(`${BASE_URL}/comments/create/`, data)
    return response
  } catch (err) {
    throw err
  }
}

/**
 * 删除评论
 * @param {number} commentId - 评论ID
 * @returns {Promise}
 */
export const deleteComment = async (commentId) => {
  try {
    const response = await request.delete(`${BASE_URL}/comments/${commentId}/delete/`)
    return response
  } catch (err) {
    throw err
  }
}

/**
 * 切换评论点赞
 * @param {number} commentId - 评论ID
 * @returns {Promise}
 */
export const toggleCommentLike = async (commentId) => {
  try {
    const response = await request.post(`${BASE_URL}/comments/${commentId}/like/`, {})
    return response
  } catch (err) {
    throw err
  }
}

// ============ 菜品相关接口 ============

/**
 * 搜索菜品
 * @param {string} keyword - 搜索关键词
 * @param {number} page - 页码，默认 1
 * @param {number} page_size - 每页数量，默认 10
 * @returns {Promise}
 */
export const searchDishes = async (keyword, page = 1, page_size = 10) => {
  try {
    const response = await request.get(`${BASE_URL}/dishes/`, {
      params: {
        search: keyword,
        page,
        page_size
      }
    })
    return response
  } catch (err) {
    throw err
  }
}

/**
 * 获取菜品详情
 * @param {number} dishId - 菜品ID
 * @returns {Promise}
 */
export const getDishDetail = async (dishId) => {
  try {
    const response = await request.get(`${BASE_URL}/dishes/${dishId}/`)
    return response
  } catch (err) {
    throw err
  }
}

// ============ 导出所有函数 ============

/**
 * 获取用户统计信息
 * @returns {Promise}
 */
export const getUserStats = async () => {
  try {
    const response = await request.get(`${BASE_URL}/profile/stats`)
    return response
  } catch (err) {
    throw err
  }
}

/**
 * 获取我的帖子
 * @param {number} page - 页码，默认 1
 * @param {number} page_size - 每页数量，默认 20
 * @returns {Promise}
 */
export const getMyPosts = async (page = 1, page_size = 20) => {
  try {
    const response = await request.get(`${BASE_URL}/profile/posts`, {
      params: { page, page_size }
    })
    return response
  } catch (err) {
    throw err
  }
}

/**
 * 获取我点赞的帖子
 * @param {number} page - 页码，默认 1
 * @param {number} page_size - 每页数量，默认 20
 * @returns {Promise}
 */
export const getLikedPosts = async (page = 1, page_size = 20) => {
  try {
    const response = await request.get(`${BASE_URL}/profile/posts/liked`, {
      params: { page, page_size }
    })
    return response
  } catch (err) {
    throw err
  }
}

/**
 * 获取我发布的评论
 * @param {number} page - 页码，默认 1
 * @param {number} page_size - 每页数量，默认 20
 * @returns {Promise}
 */
export const getMyComments = async (page = 1, page_size = 20) => {
  try {
    const response = await request.get(`${BASE_URL}/profile/comments`, {
      params: { page, page_size }
    })
    return response
  } catch (err) {
    throw err
  }
}

export default {
  getPostList,
  getPostDetail,
  createPost,
  deletePost,
  togglePostLike,
  getCommentList,
  createComment,
  deleteComment,
  toggleCommentLike,
  getUserStats,
  getMyPosts,
  getLikedPosts,
  getMyComments
}
