import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(),tailwindcss()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    host: true,
    strictPort: true,
    port: 5173,
    hmr: {
      clientPort: 443,
    },
    watch: {
      usePolling: true,
    },
    allowedHosts: [
      '5173-itfapcv06uiu4stlon2dh-cf334fbd.manusvm.computer'
    ]
  }
})


