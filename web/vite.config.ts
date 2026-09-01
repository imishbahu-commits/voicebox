import path from 'node:path';
import tailwindcss from '@tailwindcss/vite';
import react from '@vitejs/plugin-react';
import { defineConfig } from 'vite';
import { changelogPlugin } from '../app/plugins/changelog';

export default defineConfig({
  plugins: [react(), tailwindcss(), changelogPlugin(path.resolve(__dirname, '..'))],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, '../app/src'),
    },
  },
  server: {
    host: '0.0.0.0',
    // Arena serves the preview through a generated e2b.app hostname.
    allowedHosts: true,
    // Keep browser requests same-origin while forwarding API traffic to the
    // local Voicebox backend. This also makes the hosted dev preview usable;
    // browser code must never call 127.0.0.1 directly.
    proxy: {
      '^/(health|profiles|channels|generate|history|transcribe|llm|captures|capture|stories|effects|audio|samples|models|settings|tasks|backend|speak|mcp|events|cloud|shutdown|watchdog|memos)(?:/|$)': {
        target: 'http://127.0.0.1:17493',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: 'dist',
  },
});
