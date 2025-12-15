import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { MusicAIStudio } from '../MusicAIStudio';
import { ToolId } from '../components/StudioSidebar';

// Mock child components to isolate container logic
vi.mock('../components/StudioSidebar', () => ({
    StudioSidebar: ({ onSelectTool }: { onSelectTool: (id: ToolId) => void }) => (
        <div data-testid="sidebar">
            <button onClick={() => onSelectTool('progression')}>Select Progression</button>
            <button onClick={() => onSelectTool('licks')}>Select Licks</button>
        </div>
    ),
}));

vi.mock('../components/AgentPanel', () => ({
    AgentPanel: () => <div data-testid="agent-panel">Agent Panel</div>,
}));

vi.mock('../tools/ProgressionTool', () => ({
    ProgressionTool: () => <div data-testid="progression-tool">Progression Tool Content</div>,
}));

vi.mock('../tools/LicksTool', () => ({
    LicksTool: () => <div data-testid="licks-tool">Licks Tool Content</div>,
}));

// Mock other tools as needed, or let them be null if not clicked
vi.mock('../tools/VoicingTool', () => ({ VoicingTool: () => <div>Voicing Tool</div> }));
vi.mock('../tools/ExerciseTool', () => ({ ExerciseTool: () => <div>Exercise Tool</div> }));
vi.mock('../tools/AnalysisTool', () => ({ AnalysisTool: () => <div>Analysis Tool</div> }));
vi.mock('../tools/ArrangerTool', () => ({ ArrangerTool: () => <div>Arranger Tool</div> }));
vi.mock('../tools/ReharmonizerTool', () => ({ ReharmonizerTool: () => <div>Reharmonizer Tool</div> }));

// Mock hooks
vi.mock('../../../hooks/usePiano', () => ({
    usePiano: () => ({
        playChord: vi.fn(),
    }),
}));

// Mock lucide-react icons used in MusicAIStudio
vi.mock('lucide-react', () => ({
    Bot: () => <span data-testid="icon-bot" />,
}));

describe('MusicAIStudio Integration', () => {
    it('renders the layout correctly with default tool', () => {
        render(<MusicAIStudio />);

        // Sidebar should be present
        expect(screen.getByTestId('sidebar')).toBeInTheDocument();

        // Default tool (Progression) should be present
        expect(screen.getByTestId('progression-tool')).toBeInTheDocument();

        // Agent Panel should be present by default
        expect(screen.getByTestId('agent-panel')).toBeInTheDocument();
    });

    it('switches tools when sidebar items are clicked', async () => {
        render(<MusicAIStudio />);

        // Initially Progression
        expect(screen.getByTestId('progression-tool')).toBeInTheDocument();
        expect(screen.queryByTestId('licks-tool')).not.toBeInTheDocument();

        // Switch to Licks
        fireEvent.click(screen.getByText('Select Licks'));

        // Now Licks should be present
        // Use waitFor because AnimatePresence mode="wait" means old component exits before new one enters
        await waitFor(() => {
            expect(screen.getByTestId('licks-tool')).toBeInTheDocument();
        });
        // Progression might still be in DOM if AnimatePresence keeps it, 
        // but typically we check for the new one. 
        // With mode="wait", the old one leaves before new one enters.
        // Let's just check existence of new one.
    });

    it('toggles the agent panel', () => {
        render(<MusicAIStudio />);

        // Initial state: visible
        expect(screen.getByTestId('agent-panel')).toBeInTheDocument();

        // Find toggle button (title="Toggle AI Agents")
        const toggleBtn = screen.getByTitle('Toggle AI Agents');

        // Click to hide
        fireEvent.click(toggleBtn);
        expect(screen.queryByTestId('agent-panel')).not.toBeInTheDocument();

        // Click to show
        fireEvent.click(toggleBtn);
        expect(screen.getByTestId('agent-panel')).toBeInTheDocument();
    });
});
