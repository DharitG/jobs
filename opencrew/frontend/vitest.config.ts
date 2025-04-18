/// <reference types="vitest" />
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom', // Use jsdom for simulating browser environment
    setupFiles: './src/tests/setup.ts', // Optional setup file (create if needed)
    // You might want to exclude certain files/folders
    // exclude: ['node_modules', 'dist', '.idea', '.git', '.cache'], 
  },
  resolve: {
    alias: {
      // Replicate the path alias from tsconfig.json
      '~': path.resolve(__dirname, './src'),
    },
  },
});
