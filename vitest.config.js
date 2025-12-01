import { defineConfig } from 'vitest/config';
import vue from '@vitejs/plugin-vue';
import path from 'path';

export default defineConfig({
  plugins: [vue()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/frontend/src/test-setup.js'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/frontend/src/test-setup.js',
        '**/*.spec.js',
        '**/*.test.js',
        '**/cypress/**',
      ],
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src/frontend/src'),
    },
  },
});
