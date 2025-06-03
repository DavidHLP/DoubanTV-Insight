import axios from 'axios';
import { ElMessage } from 'element-plus';

// 创建axios实例
const service = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000', // API的base_url
  timeout: 15000, // 请求超时时间
});

// 请求拦截器
service.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    console.log(error); // for debug
    return Promise.reject(error);
  }
);

// 响应拦截器
service.interceptors.response.use(
  (response) => {
    const res = response.data;
    // 如果返回的状态码不是200，说明接口请求失败
    if (response.status !== 200) {
      ElMessage({
        message: res.message || '网络错误',
        type: 'error',
        duration: 3 * 1000,
      });
      return Promise.reject(new Error(res.message || '网络错误'));
    } else {
      return res;
    }
  },
  (error) => {
    console.log('请求错误: ' + error);
    ElMessage({
      message: error.message || '网络请求失败',
      type: 'error',
      duration: 5 * 1000,
    });
    return Promise.reject(error);
  }
);

export default service;
