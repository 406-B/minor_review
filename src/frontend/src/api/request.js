import axios from 'axios';

const service = axios.create({
  baseURL: '/api', // 根据实际后端地址调整
  timeout: 5000
});

// 请求拦截器
service.interceptors.request.use(
  config => {
    // 自动添加JWT token
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  error => Promise.reject(error)
);

// 响应拦截器
service.interceptors.response.use(
  response => response.data,
  error => Promise.reject(error)
);

export default service;
