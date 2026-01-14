import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import path from "path";

export default defineConfig({
  plugins: [vue()],
  build: {
    outDir: "dist",
    emptyOutDir: true,
    rollupOptions: {
      external: ["node-fetch", "vm"],
    },
  },
  server: {
    port: 5173,
    open: false,
    fs: {
      // 允许访问项目根目录之外的文件
      allow: ["."],
    },
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "packages/renderer/src"),
      "@plugins": path.resolve(__dirname, "plugins"),
    },
  },
  publicDir: "public",
});
