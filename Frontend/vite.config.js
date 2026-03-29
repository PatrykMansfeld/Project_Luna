import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// Konfiguracja Vite — bundler i dev server dla frontu
export default defineConfig({
  plugins: [vue()], // Plugin obsługujący pliki .vue (Single File Components)

  server: {
    // Proxy — przekierowuje requesty /api/* na backend FastAPI (port 8000)
    // Dzięki temu frontend i backend mogą działać na różnych portach
    // bez problemów z CORS podczas developmentu
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000', // Adres backendu
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''), // Usuwa prefix /api przed przekazaniem do backendu
      },
    },
  },
})
