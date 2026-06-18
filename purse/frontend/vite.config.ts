import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // Bind to all network interfaces, not just localhost, so devices on
    // the same LAN (e.g. a phone, for PWA "Add to Home Screen" testing)
    // can reach the dev server via the Mac's local IP.
    host: true,
  },
})
