import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

/**
 * Disable HTTP caching for everything this server hands out.
 *
 * The guard app is opened inside Telegram's in-app WebView, which caches a
 * WebApp aggressively by URL. With the unhashed dev-server module paths this
 * meant guards kept getting a *stale* version of the constraints form — an edit
 * looked like it succeeded but was never sent. `no-store` forces the WebView to
 * fetch fresh code every time. Applied to both the dev server and `vite preview`
 * (the latter is what is served in production via the cloudflared tunnel).
 */
function noCacheWebApp() {
  const attach = (server) => {
    server.middlewares.use((_req, res, next) => {
      res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate');
      res.setHeader('Pragma', 'no-cache');
      res.setHeader('Expires', '0');
      next();
    });
  };
  return {
    name: 'no-cache-webapp',
    configureServer: attach,
    configurePreviewServer: attach,
  };
}

export default defineConfig({
  plugins: [react(), noCacheWebApp()],
  server: {
    port: 3001,
    allowedHosts: ['app.safrasecure.uk', 'localhost', '.safrasecure.uk'],
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
});