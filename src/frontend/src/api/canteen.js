/**
 * 食堂消费数据 API
 */
import request from './request'

const BASE_URL = '/api/v1/canteen'

/**
 * 获取消费数据
 * @returns {Promise}
 */
export const getConsumption = async () => {
  try {
    const response = await request.get(`${BASE_URL}/consumption/`)
    return response.data
  } catch (err) {
    throw err
  }
}

/**
 * 绑定学号
 * @param {string} idserial - 学号
 * @param {string} browserType - 浏览器类型 (chrome/firefox/edge/safari)
 * @returns {Promise}
 */
export const bindAccount = async (idserial, browserType = 'chrome') => {
  try {
    const response = await request.post(`${BASE_URL}/bind/`, {
      idserial,
      browser_type: browserType
    })
    return response.data
  } catch (err) {
    throw err
  }
}

/**
 * 刷新消费数据
 * @param {string} servicehall - 可选，servicehall cookie
 * @param {string} browserType - 可选，浏览器类型
 * @returns {Promise}
 */
export const refreshConsumption = async (servicehall = null, browserType = 'chrome') => {
  try {
    const data = {}
    if (servicehall) {
      data.servicehall = servicehall
    }
    if (browserType) {
      data.browser_type = browserType
    }
    const response = await request.post(`${BASE_URL}/refresh/`, data)
    return response.data
  } catch (err) {
    throw err
  }
}

/**
 * 解绑学号
 * @returns {Promise}
 */
export const unbindAccount = async () => {
  try {
    const response = await request.delete(`${BASE_URL}/unbind/`)
    return response.data
  } catch (err) {
    throw err
  }
}
