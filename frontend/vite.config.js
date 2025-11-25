import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    cors: {
      origin: ['http://localhost:5173'],
      credentials: true,
    },
    allowedHosts: ['unprolix-qualmishly-emile.ngrok-free.dev'],
  }
})
