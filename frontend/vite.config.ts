import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { defineConfig, loadEnv } from 'vite'

export default defineConfig(({ mode }) => {
  const apiBaseUrl = loadEnv(mode, process.cwd(), 'VITE_API_BASE_URL').VITE_API_BASE_URL

  return {
    plugins: [react(), tailwindcss()],
    server: apiBaseUrl ? {
      proxy: {
        '/api': { target: apiBaseUrl, changeOrigin: true },
      },
    } : undefined,
  }
})
