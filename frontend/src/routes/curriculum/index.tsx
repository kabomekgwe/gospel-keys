import { createFileRoute } from '@tanstack/react-router';
import CurriculumBrowserPage from '../../pages/CurriculumBrowserPage';

export const Route = createFileRoute('/curriculum/')({
  component: CurriculumBrowserPage,
});
