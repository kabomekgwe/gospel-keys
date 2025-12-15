/**
 * AI Generator Page
 * 
 * Standalone page for AI-powered music theory generation
 */
import { createFileRoute } from '@tanstack/react-router';
import { MusicAIStudio } from '../../features/ai-studio/MusicAIStudio';

export const Route = createFileRoute('/generator/')({
    component: GeneratorPage,
});

function GeneratorPage() {
    return (
        <div className="h-screen bg-slate-950">
            <MusicAIStudio />
        </div>
    );
}
