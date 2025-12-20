/**
 * 食堂消费数据 API
 */
import request from './request'

const BASE_URL = '/v1/canteen'

/**
 * 获取消费数据
 * @returns {Promise}
 */
export const getConsumption = async () => {
  try {
    const response = await request.get(`${BASE_URL}/consumption/`)
    return response
  } catch (err) {
    throw err
  }
}

/**
 * 绑定学号
 * @param {string|null} idserial - 学号(可选,不填则系统自动提取)
 * @param {string} browserType - 浏览器类型 (chrome/firefox/edge/safari)
 * @returns {Promise}
 */
export const bindAccount = async (idserial = null, browserType = 'chrome') => {
  try {
    const data = { browser_type: browserType }
    if (idserial) {
      data.idserial = idserial
    }
    // 绑定操作需要等待用户手动登录，设置5分钟超时
    const response = await request.post(`${BASE_URL}/bind/`, data, {
      timeout: 300000 // 5分钟 = 300秒 = 300000毫秒
    })
    return response
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
    // 刷新时如果cookie失效可能需要重新登录，设置5分钟超时
    const response = await request.post(`${BASE_URL}/refresh/`, data, {
      timeout: 300000 // 5分钟
    })
    return response
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
    return response
  } catch (err) {
    throw err
  }
}

/**
 * 启动自动登录流程
 * @param {string} username - 学号
 * @param {string} password - 密码
 * @param {string} browserType - 浏览器类型 (chrome/firefox/edge)
 * @param {boolean} headless - 是否使用无头模式
 * @returns {Promise}
 */
export const startAutoLogin = async (username, password, browserType = 'chrome', headless = true) => {
  try {
    // 该接口可能会触发后端打开浏览器并等待用户操作，可能耗时较长，增加超时时间到5分钟
    const response = await request.post(`${BASE_URL}/auto-login/start/`, {
      idserial: username,
      password,
      browser_type: browserType,
      headless
    }, {
      timeout: 300000 // 5分钟
    })
    return response
  } catch (err) {
    throw err
  }
}

/**
 * 提交验证码
 * @param {string} sessionId - 会话 ID
 * @param {string} verificationCode - 验证码
 * @returns {Promise}
 */
export const submitVerificationCode = async (sessionId, verificationCode) => {
  try {
    const response = await request.post(`${BASE_URL}/auto-login/submit-code/`, {
      session_id: sessionId,
      verification_code: verificationCode
    })
    return response
  } catch (err) {
    throw err
  }
}

/**
 * 查询登录状态
 * @param {string} sessionId - 会话 ID
 * @returns {Promise}
 */
export const checkLoginStatus = async (sessionId) => {
  try {
    const response = await request.get(`${BASE_URL}/auto-login/status/`, {
      params: { session_id: sessionId }
    })
    return response
  } catch (err) {
    throw err
  }
}

/**
 * 使用 Cookie 获取消费数据
 * @param {string} idserial - 学号
 * @param {string} servicehall - servicehall cookie
 * @returns {Promise}
 */
export const fetchWithCookie = async (idserial, servicehall) => {
  try {
    const response = await request.post(`${BASE_URL}/fetch-with-cookie/`, {
      idserial,
      servicehall
    })
    return response  // 已经被拦截器解包过了，直接返回
  } catch (err) {
    throw err
  }
}
