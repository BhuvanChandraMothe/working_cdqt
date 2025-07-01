// src/api/axiosInstance.js
import axios from 'axios';
import { baseURL } from '../utilities/constants';

const axiosInstance = axios.create({
    baseURL,
});

// Add a request interceptor to include the Authorization header
axiosInstance.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        console.log(token)
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

export default axiosInstance;

