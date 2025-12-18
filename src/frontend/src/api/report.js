/**
 * 举报相关API
 */

import request from './request'

/**
 * 举报内容
 * @param {Object} data 举报数据
 * @param {String|Number} data.content_id 内容ID
 * @param {String} data.content_type 内容类型：post/comment/review
 * @param {Array} data.reasons 举报原因数组：['political', 'obscene', 'advertisement', 'attack', 'other']
 * @param {String} data.description 补充说明（选择"其他"时必填）
 * @returns {Promise}
 */
export const reportContent = async (data) => {
  try {
    const response = await request.post('/v1/reports/', {
      content_id: data.content_id,
      content_type: data.content_type,
      reasons: data.reasons,
      description: data.description
    })
    return response
  } catch (err) {
    throw err
  }
}

/**
 * 获取我的举报记录
 * @returns {Promise}
 */
export const getMyReports = async () => {
  try {
    const response = await request.get('/v1/reports/my/')
    return response
  } catch (err) {
    throw err
  }
}

/**
 * 获取所有举报记录（管理员）
 * @param {Object} params 查询参数
 * @param {String} params.status 状态过滤：pending/approved/rejected
 * @param {String} params.content_type 内容类型过滤
 * @returns {Promise}
 */
export const getAllReports = async (params) => {
  try {
    const response = await request.get('/v1/reports/all/', { params })
    return response
  } catch (err) {
    throw err
  }
}

/**
 * 处理举报（管理员）
 * @param {Number} reportId 举报ID
 * @param {Object} data 处理数据
 * @param {String} data.action 处理动作：approve/reject
 * @param {String} data.admin_note 管理员备注
 * @returns {Promise}
 */
export const handleReport = async (reportId, data) => {
  try {
    const response = await request.post(`/v1/reports/${reportId}/handle/`, data)
    return response
  } catch (err) {
    throw err
  }
}
