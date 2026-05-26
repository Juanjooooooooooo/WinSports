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
    test: {
      globals: true,
      environment: "jsdom",
      setupFiles: "./src/test/setup.jsx",
      // No procesamos CSS en tests (leaflet.css, theme.css) — irrelevante para
      // las aserciones y evita que jsdom intente parsear hojas de estilo.
      css: false,
    },
  };
});
