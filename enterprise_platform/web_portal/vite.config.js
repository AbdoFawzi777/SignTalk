import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  base: './', // Relative base path ensures deployment on GitHub Pages, Vercel, Netlify, and custom domains
  server: {
    port: 5173,
    host: true
  }
})
