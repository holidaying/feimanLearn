import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// 开发期由 Vite 托管前端，/api 反代到后端（默认 8000）
// 生产期后端 server/app.py 直接托管 web/dist，/api 同源，无需反代
export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    emptyOutDir: true,
  },
})
