import axios from "axios";

// Demo mode - set to true to work without backend
const DEMO_MODE = false;

const api = axios.create({
  baseURL: DEMO_MODE ? "http://localhost:3001" : "http://localhost:8888",
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: true, // Enable cookies for authentication
  timeout: 30000, // 30 second timeout for voice processing
});

// Request interceptor for cookie-based auth
api.interceptors.request.use(
  (config) => {
    // Cookies are automatically sent with withCredentials: true
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 || error.response?.status === 403) {
      // Clear any stored data and redirect to login
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      // Only redirect if not already on login page
      if (window.location.pathname !== '/login' && window.location.pathname !== '/register') {
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

export default api;
