import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// Get proxy target from environment
// In Docker: VITE_PROXY_TARGET=http://backend:8000
// Locally: defaults to http://localhost:8000
const PROXY_TARGET = process.env.VITE_PROXY_TARGET || 'http://localhost:8000'

console.log('🔧 Vite proxy target:', PROXY_TARGET)

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    host: '0.0.0.0',
    port: 3000,
    proxy: {
      '/api': {
        target: PROXY_TARGET,
        changeOrigin: true,
        secure: false,
        // Don't rewrite, keep /api prefix so backend receives /api/campaigns, etc.
        rewrite: (path) => path,
        configure: (proxy, _options) => {
          proxy.on('error', (err, _req, res) => {
            console.error('❌ Proxy error:', err);
            if (!res.headersSent) {
              res.writeHead(500, { 'Content-Type': 'application/json' });
              res.end(JSON.stringify({ error: 'Proxy error', details: err.message }));
            }
          });
          proxy.on('proxyReq', (proxyReq, req, _res) => {
            console.log('🔄 Proxying:', req.method, req.url, '→', PROXY_TARGET + req.url);
          });
          proxy.on('proxyRes', (proxyRes, req, _res) => {
            if (proxyRes.statusCode === 307 || proxyRes.statusCode === 308) {
              console.warn('⚠️  Redirect detected:', proxyRes.statusCode, 'for', req.url, 
                          '- This may cause issues. Check backend trailing slashes.');
            }
          });
        },
      },
    },
  },
})

