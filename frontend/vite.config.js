// frontend/vite.config.js
import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig(({ mode }) => {
  // Sube un nivel para leer el .env de la raíz del proyecto
  const env = loadEnv(mode, "../", "");

  return {
    plugins: [react()],
    server: {
      proxy: {
        "/api": env.API_BASE_URL || "http://localhost:8000",
      },
    },
  };
});
