import { createFileRoute } from '@tanstack/react-router';
import { GenreTheoryExplorer } from '../../components/genres/GenreTheoryExplorer';

export const Route = createFileRoute('/genres/theory')({
    component: GenreTheoryPage,
});

function GenreTheoryPage() {
    return (
        <div className="container mx-auto px-4 py-8">
            <GenreTheoryExplorer />
        </div>
    );
}
