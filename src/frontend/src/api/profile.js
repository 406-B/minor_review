// 示例 profile API（当前为前端 mock），后续应替换为真实后端接口
import request from './request'

// 从后端获取当前登录用户的个人资料
export const getProfile = async () => {
  try {
    // API 文档: GET /api/v1/profile
    // 统一由拦截器注入 Authorization
    const data = await request.get('/v1/profile')
    return data
  } catch (err) {
    // 将错误向上抛出，调用方处理
    throw err
  }
}

// 更新用户个人资料（昵称、头像）
export const updateProfile = async (formData) => {
  try {
    // API 文档: PUT /api/v1/profile/update
    // multipart/form-data 请求，拦截器会自动注入 Authorization
    const data = await request.put('/v1/profile/update', formData, {
      headers: { 
        'Content-Type': 'multipart/form-data'
      }
    })
    return data
  } catch (err) {
    throw err
  }
}

// 获取用户统计信息（点赞、评论、关注数）
export const getProfileStats = async () => {
  try {
    // API 文档: GET /api/v1/profile/stats
    const data = await request.get('/v1/profile/stats')
    return data
  } catch (err) {
    throw err
  }
}

// 为兼容原有页面接口，提供一个聚合方法，返回 user/published/interactions
export const getProfileSections = async () => {
  // 优先尝试从后端拉取真实用户信息和统计
  try {
  const userRes = await getProfile()
  const statsRes = await getProfileStats().catch(() => null)

  // 兼容后端可能返回 { code, data } 的格式
  const user = userRes && typeof userRes === 'object' && 'data' in userRes ? userRes.data : userRes
  const stats = statsRes && typeof statsRes === 'object' && 'data' in statsRes ? statsRes.data : statsRes

    // published / interactions 目前后端接口未提供（或未在文档中列出），保留前端示例数据
    const published = [
      { id: 1, title: '示例帖子一', createdAt: '2025-10-01 14:23' },
      { id: 2, title: '示例帖子二', createdAt: '2025-09-27 09:10' }
    ]

    const interactions = [
      { name: '我点赞的帖子', count: stats ? stats.liked_posts_count : 0, to: '/likes' },
      { name: '我评论的帖子', count: stats ? stats.commented_posts_count : 0, to: '/comments' },
      { name: '我关注的人', count: stats ? stats.following_count : 0, to: '/following' }
    ]

  return { user, published, interactions }
  } catch (err) {
    // 回退到前端 mock 数据，避免页面完全不可用
    return Promise.resolve({
      user: { name: 'Example User', email: 'example@example.com', avatar: '' },
      published: [
        { id: 1, title: '示例帖子一', createdAt: '2025-10-01 14:23' },
        { id: 2, title: '示例帖子二', createdAt: '2025-09-27 09:10' },
        { id: 3, title: '更早的帖子', createdAt: '2025-08-15 18:00' }
      ],
      interactions: [
        { name: '我点赞的帖子', count: 12, to: '/likes' },
        { name: '我评论的帖子', count: 4, to: '/comments' },
        { name: '我关注的人', count: 8, to: '/following' }
      ]
    })
  }
}

// ==================== 偏好标签与推荐相关 ====================

// 获取当前登录用户的偏好标签
export const getPreferenceTags = () => request.get('/v1/profile/preference-tags')

// 设置用户偏好标签（覆盖）
export const setPreferenceTags = (tagIds = []) => request.post('/v1/profile/preference-tags/set', { tag_ids: tagIds })

// 追加用户偏好标签
export const addPreferenceTags = (tagIds = []) => request.post('/v1/profile/preference-tags/add', { tag_ids: tagIds })

// 获取个性化推荐菜品（按偏好；若提供经纬度则为综合）
// params: { page?, page_size?, latitude?, longitude? }
export const getRecommendedDishes = (params = {}) => request.get('/v1/profile/recommended-dishes', { params })

// 获取附近推荐菜品（按位置）
// params: { latitude, longitude, page?, page_size? }
export const getNearbyRecommendedDishes = (params) => request.get('/v1/profile/nearby-dishes', { params })

export default { 
  getProfile, updateProfile, getProfileStats, getProfileSections,
  getPreferenceTags, setPreferenceTags, addPreferenceTags,
  getRecommendedDishes, getNearbyRecommendedDishes,
}
