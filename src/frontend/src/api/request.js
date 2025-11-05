import axios from 'axios';

/**
 * axios 实例，统一 API 请求入口
 * 可在此配置 baseURL、超时、拦截器等
 */
export const api = axios.create({
  baseURL: '/api', // 根据实际后端地址调整
  timeout: 5000
});

// 请求拦截器
api.interceptors.request.use(
  config => {
    // 可在此添加 token 等
    return config;
  },
  error => Promise.reject(error)
);

// 响应拦截器
api.interceptors.response.use(
  response => response.data,
  error => Promise.reject(error)
);
