import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { defineConfig, loadEnv } from 'vite'

export default defineConfig(({ mode }) => {
  const apiBaseUrl = loadEnv(mode, process.cwd(), 'VITE_API_BASE_URL').VITE_API_BASE_URL
  const assistantEnv = loadEnv(mode, process.cwd(), 'ASSISTANT_BASE_URL').ASSISTANT_BASE_URL
  // The assistant target is used only by Vite's server-side proxy.
  const assistantBaseUrl = assistantEnv || (mode === 'development'
    ? new URL(apiBaseUrl || 'http://localhost:8000').hostname === 'api'
      ? 'http://assistant:8001' : 'http://localhost:8001'
    : '')
  const proxy = {
    ...(apiBaseUrl ? {
      '/api': { target: apiBaseUrl, changeOrigin: true },
      '/auth': { target: apiBaseUrl, changeOrigin: true },
    } : {}),
    ...(assistantBaseUrl ? {
      '/assistant-api/chat': {
        target: assistantBaseUrl,
        changeOrigin: true,
        rewrite: (path: string) => path.replace(/^\/assistant-api\/chat(?=\?|$)/, '/chat'),
      },
    } : {}),
  }

  return {
    plugins: [react(), tailwindcss()],
    server: { proxy },
    preview: { proxy },
  }
})
