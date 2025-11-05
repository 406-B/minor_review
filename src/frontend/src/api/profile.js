// 示例 profile API（当前为前端 mock），后续应替换为真实后端接口
import request from './request'

// 从后端获取当前登录用户的个人资料
export const getProfile = async () => {
  const token = localStorage.getItem('jwt') || ''
  try {
    // API 文档: GET /api/v1/profile
    const data = await request.get('/v1/profile', {
      headers: { Authorization: token }
    })
    return data
  } catch (err) {
    // 将错误向上抛出，调用方处理
    throw err
  }
}

// 获取用户统计信息（点赞、评论、关注数）
export const getProfileStats = async () => {
  const token = localStorage.getItem('jwt') || ''
  try {
    // API 文档: GET /api/v1/profile/stats
    const data = await request.get('/v1/profile/stats', {
      headers: { Authorization: token }
    })
    return data
  } catch (err) {
    throw err
  }
}

// 为兼容原有页面接口，提供一个聚合方法，返回 user/published/interactions
export const getProfileSections = async () => {
  // 优先尝试从后端拉取真实用户信息和统计
  try {
    const user = await getProfile()
    const stats = await getProfileStats().catch(() => null)

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

export default { getProfile, getProfileStats, getProfileSections }
