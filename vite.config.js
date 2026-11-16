import { defineConfig } from 'vite';

// base './' lets the build be served from any sub-path (e.g. GitHub Pages)
export default defineConfig({
  base: './',
  server: { port: 5174 },
  build: { target: 'es2020' },
});
