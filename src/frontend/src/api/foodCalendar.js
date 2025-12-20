/**
 * 美食日历 API
 * 用于获取用户的菜品打卡历史记录
 */
import request from './request'

const BASE_URL = '/v1/profile'

/**
 * 获取打卡历史（按日期范围或月份）
 * @param {Object} params - 查询参数
 * @param {string} params.start_date - 开始日期 YYYY-MM-DD
 * @param {string} params.end_date - 结束日期 YYYY-MM-DD
 * @param {number} params.year - 年份
 * @param {number} params.month - 月份 (1-12)
 * @returns {Promise}
 */
export const getCheckInHistory = async (params = {}) => {
  try {
    const response = await request.get(`${BASE_URL}/check-in-history`, { params })
    return response
  } catch (err) {
    throw err
  }
}

/**
 * 获取月度打卡概览（快速查看哪些日期有打卡）
 * @param {number} year - 年份
 * @param {number} month - 月份 (1-12)
 * @returns {Promise}
 */
export const getCheckInCalendar = async (year, month) => {
  try {
    const response = await request.get(`${BASE_URL}/check-in-calendar`, {
      params: { year, month }
    })
    return response
  } catch (err) {
    throw err
  }
}

/**
 * 获取最近N天的打卡历史
 * @param {number} days - 天数，默认7天
 * @returns {Promise}
 */
export const getRecentCheckIns = async (days = 7) => {
  try {
    const endDate = new Date()
    const startDate = new Date(endDate)
    startDate.setDate(startDate.getDate() - (days - 1))
    
    const params = {
      start_date: formatDate(startDate),
      end_date: formatDate(endDate)
    }
    
    return await getCheckInHistory(params)
  } catch (err) {
    throw err
  }
}

/**
 * 格式化日期为 YYYY-MM-DD
 * @param {Date} date 
 * @returns {string}
 */
function formatDate(date) {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

export default {
  getCheckInHistory,
  getCheckInCalendar,
  getRecentCheckIns
}
