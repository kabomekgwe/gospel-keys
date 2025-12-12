import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import viteTsConfigPaths from 'vite-tsconfig-paths';

export default defineConfig({
    plugins: [
        react(),
        viteTsConfigPaths({
            projects: ['./tsconfig.json'],
        }),
    ],
    test: {
        globals: true,
        environment: 'jsdom',
        setupFiles: ['./src/test/setup.ts'],
        include: ['src/**/*.{test,spec}.{ts,tsx}'],
        exclude: ['node_modules', 'dist', '.output'],
        coverage: {
            provider: 'v8',
            reporter: ['text', 'html', 'lcov'],
            exclude: [
                'node_modules',
                'src/test',
                '**/*.d.ts',
                '**/routeTree.gen.ts',
            ],
        },
    },
});
