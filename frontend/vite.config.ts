import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
  server: {
    proxy: {
      "/chat": "http://127.0.0.1:8000",
      "/upload": "http://127.0.0.1:8000",
      "/documents": "http://127.0.0.1:8000",
      "/stream-chat": "http://127.0.0.1:8000",
      "/auth": "http://127.0.0.1:8000",
      "/conversations": "http://127.0.0.1:8000",
    },
  },
});