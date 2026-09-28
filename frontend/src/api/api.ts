import axios from "axios";
import { API_BASE_URL } from "../config/config";
import { tokenStore } from "../utils/tokenStore";

const api = axios.create({
  baseURL: API_BASE_URL,
});

api.interceptors.request.use((config) => {
  const token = tokenStore.getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

/**
 * Response interceptor:
 * 1. Handles 401 by clearing invalid/expired session tokens.
 * 2. Automatically retries GET requests once on failure.
 */
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const config = error.config;

    if (error.response?.status === 401) {
      tokenStore.removeToken();
      localStorage.removeItem("ai_research_user");
      // If on a protected route, redirect to home/login
      if (window.location.pathname !== "/") {
        window.location.href = "/";
      }
      return Promise.reject(error);
    }

    if (
      config &&
      config.method === "get" &&
      !config._retried
    ) {
      config._retried = true;
      return api.request(config);
    }

    return Promise.reject(error);
  }
);

export default api;