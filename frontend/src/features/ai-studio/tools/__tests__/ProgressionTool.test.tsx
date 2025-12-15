import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { ProgressionTool } from '../ProgressionTool';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// Mock dependencies
vi.mock('lucide-react', () => ({
    Music: () => <span data-testid="icon-music" />,
    Play: () => <span data-testid="icon-play" />,
    Loader2: () => <span data-testid="icon-loader" />,
    Volume2: () => <span data-testid="icon-volume" />,
    RefreshCw: () => <span data-testid="icon-refresh" />,
    Wand2: () => <span data-testid="icon-wand" />,
    Settings2: () => <span data-testid="icon-settings" />,
    Info: () => <span data-testid="icon-info" />,
}));

const { mockGenerateProgression } = vi.hoisted(() => {
    return { mockGenerateProgression: vi.fn() };
});

vi.mock('../../../../lib/api', () => ({
    aiApi: {
        generateProgression: mockGenerateProgression,
    },
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

describe('ProgressionTool', () => {
    it('renders correctly', () => {
        renderWithProviders(<ProgressionTool onPlayChord={() => { }} />);
        expect(screen.getByText('Chord Progression Generator')).toBeInTheDocument();
        expect(screen.getByText('Key')).toBeInTheDocument();
        expect(screen.getByText('Style')).toBeInTheDocument();
    });

    it('triggers generation when button is clicked', async () => {
        const mockData = {
            progression: [
                { symbol: 'Cmaj7', notes: ['C', 'E', 'G', 'B'], midi_notes: [60, 64, 67, 71], function: 'I' },
            ],
            key: 'C',
            style: 'jazz',
            analysis: 'Nice changes',
        };
        mockGenerateProgression.mockResolvedValue(mockData);

        renderWithProviders(<ProgressionTool onPlayChord={() => { }} />);

        const generateButton = screen.getByRole('button', { name: /generate progression/i });
        expect(generateButton).not.toBeDisabled();
        fireEvent.click(generateButton);

        await waitFor(() => {
            expect(mockGenerateProgression).toHaveBeenCalled();
        });
    });
});
