import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.js',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html', 'lcov'],
      exclude: [
        'node_modules/',
        'src/test/',
        '**/*.config.js',
        '**/*.test.{js,jsx}',
        '**/main.jsx',
      ],
      thresholds: {
        statements: 80,
        branches: 75,
        functions: 80,
        lines: 80,
      },
    },
    css: true,
    include: ['**/__tests__/**/*.{test,spec}.{js,jsx}', '**/*.{test,spec}.{js,jsx}'],
  },
});
