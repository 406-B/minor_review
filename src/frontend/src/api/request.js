import axios from 'axios';

const service = axios.create({
  baseURL: '/api', // 根据实际后端地址调整
  timeout: 10000
});

// 请求拦截器
service.interceptors.request.use(
  config => {
    // 如果请求头中没有 Authorization，尝试从 localStorage 获取
    if (!config.headers.Authorization) {
      const token = localStorage.getItem('jwt');
      if (token) {
        // 如果 token 不包含 'Bearer ' 前缀，则添加
        config.headers.Authorization = token.startsWith('Bearer ') ? token : `Bearer ${token}`;
        
        // 开发环境下打印调试信息
        if (import.meta.env.DEV) {
          console.log('[请求] 已添加 Authorization 头:', config.headers.Authorization.substring(0, 20) + '...');
        }
      } else {
        // 开发环境下警告未登录
        if (import.meta.env.DEV) {
          console.warn('[请求] 未找到 JWT Token，请求可能失败:', config.url);
        }
      }
    }
    return config;
  },
  error => Promise.reject(error)
);

// 响应拦截器
service.interceptors.response.use(
  response => response.data,
  error => {
    // 处理错误响应
    if (error.response) {
      // 服务器返回了错误状态码
      const { status, data } = error.response;
      
      if (status === 401) {
        // 未授权，可能需要重新登录
        console.error('未授权，请重新登录');
        // 可以在这里添加跳转到登录页的逻辑
      } else if (status === 403) {
        console.error('无权限访问');
      } else if (status === 404) {
        console.error('请求的资源不存在');
      } else if (status >= 500) {
        console.error('服务器错误');
      }
      
      // 返回错误数据，让调用方处理
      return Promise.reject(error);
    } else if (error.request) {
      // 请求已发送但没有收到响应
      console.error('网络错误，请检查连接');
      return Promise.reject(new Error('网络错误'));
    } else {
      // 其他错误
      console.error('请求配置错误:', error.message);
      return Promise.reject(error);
    }
  }
);

export default service;
