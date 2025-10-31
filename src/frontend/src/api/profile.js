// 示例 profile API（当前为前端 mock），后续应替换为真实后端接口
import request from './request'

export const getProfileSections = async () => {
  // TODO: 将来改为 request.get('/user/profile/sections') 等真实请求
  // 目前返回示例数据，便于页面开发
  return Promise.resolve({
    user: {
      name: 'Example User',
      email: 'example@example.com'
    },
    published: [
      { id: 1, title: '示例帖子一', createdAt: '2025-10-01 14:23' },
      { id: 2, title: '示例帖子二', createdAt: '2025-09-27 09:10' },
      { id: 3, title: '更早的帖子', createdAt: '2025-08-15 18:00' }
    ],
    interactions: [
      { name: '我点赞的帖子', count: 12, to: '/likes' },
      { name: '我评论的帖子', count: 4, to: '/comments' },
      { name: '我关注的人', count: 8, to: '/following' }
    ],
    // control panel 不需要数据，目前前端静态渲染
  })
}

export default { getProfileSections }
