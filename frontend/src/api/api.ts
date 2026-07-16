import axios from "axios";
import { API_BASE_URL } from "../config/config";

const api = axios.create({
  baseURL: API_BASE_URL,
});

/**
 * Retry interceptor: automatically retries GET requests once on failure.
 * Uploads (POST) and deletes are never auto-retried.
 */
api.interceptors.response.use(undefined, async (error) => {
  const config = error.config;

  if (
    config &&
    config.method === "get" &&
    !config._retried
  ) {
    config._retried = true;
    return api.request(config);
  }

  return Promise.reject(error);
});

export default api;