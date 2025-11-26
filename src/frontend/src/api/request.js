import axios from 'axios';

const service = axios.create({
  baseURL: '/api', // 根据实际后端地址调整
  timeout: 10000
});

// 请求拦截器
service.interceptors.request.use(
  config => {
    // 统一从 localStorage 注入 Bearer token；若调用方自带 Authorization，则只在缺失时补充
    const stored = localStorage.getItem('jwt');
    if (stored) {
      const bearer = stored.startsWith('Bearer ') ? stored : `Bearer ${stored}`;
      if (!config.headers.Authorization) {
        config.headers.Authorization = bearer;
      } else if (!String(config.headers.Authorization).toLowerCase().startsWith('bearer ')) {
        // 纠正非 Bearer 的裸 token
        config.headers.Authorization = bearer;
      }

      if (import.meta.env.DEV) {
        console.log('[请求] Authorization:', String(config.headers.Authorization).slice(0, 24) + '...');
      }
    } else if (import.meta.env.DEV) {
      console.warn('[请求] 未找到 JWT Token，可能触发401/403:', config.url);
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
