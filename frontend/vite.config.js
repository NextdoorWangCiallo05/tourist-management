import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 8081,
    proxy: {
      '/api': { target: 'http://localhost:5000', changeOrigin: true }
    }
  },
  test: {
    environment: 'node',
    include: ['src/__tests__/unit/**/*.test.js']
  }
})
