/**
 * Theory Lab Route
 *
 * Advanced theory exploration with interactive tools
 */
import { createFileRoute } from '@tanstack/react-router';
import { TheoryLab } from '../../components/theory/TheoryLab';

export const Route = createFileRoute('/theory/lab')({
    component: TheoryLabPage,
});

function TheoryLabPage() {
    return <TheoryLab />;
}
