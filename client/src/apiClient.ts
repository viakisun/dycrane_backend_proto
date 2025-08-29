import axios from 'axios';

const apiClient = axios.create({
  baseURL: '/api', // The proxy will handle the redirect to http://127.0.0.1:8000
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export default apiClient;
