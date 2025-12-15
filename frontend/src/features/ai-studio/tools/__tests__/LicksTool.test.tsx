import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { LicksTool } from '../LicksTool';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// Mock dependencies
vi.mock('lucide-react', () => ({
    Zap: () => <span data-testid="icon-zap" />,
    Play: () => <span data-testid="icon-play" />,
    Loader2: () => <span data-testid="icon-loader" />,
    Search: () => <span data-testid="icon-search" />,
}));

// Use vi.hoisted for the mock function
const { mockGenerateLicks } = vi.hoisted(() => {
    return { mockGenerateLicks: vi.fn() };
});

vi.mock('../../../../lib/api', () => ({
    aiApi: {
        generateLicks: mockGenerateLicks,
    },
}));

vi.mock('../../../../hooks/usePiano', () => ({
    usePiano: () => ({
        playScale: vi.fn(),
    }),
}));

const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            retry: false,
        },
    },
});

const renderWithProviders = (ui: React.ReactElement) => {
    return render(
        <QueryClientProvider client={queryClient}>
            {ui}
        </QueryClientProvider>
    );
};

describe('LicksTool', () => {
    it('renders correctly', () => {
        renderWithProviders(<LicksTool />);
        expect(screen.getByText('Lick Generator')).toBeInTheDocument();
        expect(screen.getByText('Style')).toBeInTheDocument();
        expect(screen.getByText('Difficulty')).toBeInTheDocument();
    });
});
