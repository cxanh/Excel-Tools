import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [
    vue(),
    // 支持导入.py文件为原始文本
    {
      name: 'raw-py-loader',
      transform(code, id) {
        if (id.endsWith('.py')) {
          return {
            code: `export default ${JSON.stringify(code)}`,
            map: null
          }
        }
      }
    }
  ],
  root: 'packages/renderer',
  base: './',
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './packages/renderer/src'),
      '@plugins': path.resolve(__dirname, './plugins')
    }
  },
  optimizeDeps: {
    exclude: ['pyodide']
  },
  build: {
    outDir: path.resolve(__dirname, './packages/renderer/dist'),
    emptyOutDir: true,
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor': ['vue', 'vue-router', 'ant-design-vue']
        }
      }
    },
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: false,
        drop_debugger: true
      }
    }
  },
  server: {
    port: 5173,
    strictPort: true
  }
})
