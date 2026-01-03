import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'
import tailwindcss from '@tailwindcss/vite'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd() + '/../')

  // Note: for local dev + tunnel (Cloudflare/ngrok), we usually want runtime requests to stay on same-origin (/api),
  // but still need Vite's dev proxy to know where the backend is. Use VITE_DEV_PROXY_TARGET for proxy only.
  const apiBaseUrl = env.VITE_DEV_PROXY_TARGET || env.VITE_API_BASE_URL || 'http://localhost:8000'
  const port = parseInt(env.VITE_FRONTEND_PORT || '3015', 10)

  return {
    base: './',
    plugins: [react(), tailwindcss()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
      },
    },
    server: {
      host: '0.0.0.0',
      port: port,
      allowedHosts: true, // 允许任意域名访问
      proxy: {
        '/api': {
          target: apiBaseUrl,
          changeOrigin: true,
          rewrite: path => path.replace(/^\/api/, '/api'),
        },
        '/static': {
          target: apiBaseUrl,
          changeOrigin: true,
          rewrite: path => path.replace(/^\/static/, '/static'),
        },
        '/uploads': {
          target: apiBaseUrl,
          changeOrigin: true,
          rewrite: path => path.replace(/^\/uploads/, '/uploads'),
        },
      },
    },
  }
})
