import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// El backend (FastAPI) corre en :8000. En dev, proxyeamos las rutas de la API
// para llamar con rutas relativas desde el frontend (:5173).
const API_PATHS = ["/businesses", "/jobs", "/zones", "/stats", "/health"];

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: Object.fromEntries(
      API_PATHS.map((p) => [p, { target: "http://localhost:8000", changeOrigin: true }])
    ),
  },
  build: {
    outDir: "dist",
    emptyOutDir: true,
  },
});
