/**
 * Practice Dashboard Page - Gospel Keys Music Education Platform
 */
import { createFileRoute } from '@tanstack/react-router';
import PracticeSessionPage from '../../pages/PracticeSessionPage';

export const Route = createFileRoute('/practice/')({
    component: PracticeSessionPage,
});
