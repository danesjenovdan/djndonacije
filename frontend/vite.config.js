import { fileURLToPath } from "node:url";
import { resolve, dirname } from "node:path";

import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

const currentDir = dirname(fileURLToPath(import.meta.url));

// https://vitejs.dev/config/
export default defineConfig({
  server: {
    port: 3000,
    host: true,
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
