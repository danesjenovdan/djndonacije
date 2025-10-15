import vue from "@vitejs/plugin-vue";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { defineConfig } from "vite";

const currentDir = dirname(fileURLToPath(import.meta.url));

// https://vitejs.dev/config/
export default defineConfig({
  clearScreen: false,
  server: {
    host: true,
    port: 3000,
    strictPort: true,
  },
  plugins: [vue()],
  resolve: {
    alias: {
      "@": resolve(currentDir, "src"),
      "~bootstrap": resolve(currentDir, "node_modules/bootstrap"),
    },
  },
  css: {
    preprocessorOptions: {
      scss: {
        silenceDeprecations: ["import"], // remove when updating to sass 3.0.0
        quietDeps: true, // remove when bootstrap is updated
      },
    },
  },
});
