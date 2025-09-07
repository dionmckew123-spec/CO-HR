import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Vite configuration for the frontend. The ``VITE_API`` environment
// variable, injected via docker-compose, will determine the base URL
// used by the API helper. Hot module replacement is enabled by default.

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
  },
});