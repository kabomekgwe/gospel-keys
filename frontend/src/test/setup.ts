/**
 * Test Setup File
 * 
 * Configure testing utilities and global mocks
 */
import '@testing-library/jest-dom/vitest';
import { cleanup } from '@testing-library/react';
import { afterEach, vi } from 'vitest';

// Cleanup after each test
afterEach(() => {
    cleanup();
});

// Mock Web Audio API
const AudioContextMock = vi.fn(() => ({
    createOscillator: vi.fn(() => ({
        connect: vi.fn(),
        start: vi.fn(),
        stop: vi.fn(),
        disconnect: vi.fn(),
        type: 'triangle',
        frequency: { value: 440 },
    })),
    createGain: vi.fn(() => ({
        connect: vi.fn(),
        disconnect: vi.fn(),
        gain: {
            value: 1,
            setValueAtTime: vi.fn(),
            linearRampToValueAtTime: vi.fn(),
            cancelScheduledValues: vi.fn(),
        },
    })),
    destination: {},
    currentTime: 0,
    state: 'running',
    resume: vi.fn(),
    close: vi.fn(),
}));

// @ts-ignore
global.AudioContext = AudioContextMock;
// @ts-ignore
global.webkitAudioContext = AudioContextMock;

// Mock matchMedia
Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: vi.fn().mockImplementation((query: string) => ({
        matches: false,
        media: query,
        onchange: null,
        addListener: vi.fn(),
        removeListener: vi.fn(),
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        dispatchEvent: vi.fn(),
    })),
});

// Mock ResizeObserver
global.ResizeObserver = vi.fn().mockImplementation(() => ({
    observe: vi.fn(),
    unobserve: vi.fn(),
    disconnect: vi.fn(),
}));

// Mock IntersectionObserver
global.IntersectionObserver = vi.fn().mockImplementation(() => ({
    observe: vi.fn(),
    unobserve: vi.fn(),
    disconnect: vi.fn(),
}));

// Mock localStorage
const localStorageMock = (() => {
    let store: Record<string, string> = {};
    return {
        getItem: (key: string) => store[key] ?? null,
        setItem: (key: string, value: string) => {
            store[key] = value;
        },
        removeItem: (key: string) => {
            delete store[key];
        },
        clear: () => {
            store = {};
        },
    };
})();
Object.defineProperty(window, 'localStorage', { value: localStorageMock });

// Mock fetch
global.fetch = vi.fn();
