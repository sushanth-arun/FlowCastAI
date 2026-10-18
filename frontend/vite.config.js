import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://148.100.108.248:8000',
        changeOrigin: true
      },
      '/healthz': {
        target: 'http://148.100.108.248:8000',
        changeOrigin: true
      }
    }
  }
})
