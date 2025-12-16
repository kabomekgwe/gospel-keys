import React, { useState } from 'react';
import { Header } from '../design-system/components/organisms';
import { Container, Stack, Grid } from '../design-system/components/templates';
import { Button, Badge, ProgressBar } from '../design-system/components/atoms';
import { Card, CurriculumCard } from '../design-system/components/molecules';
import {
  useCurriculumTemplates,
  useActiveCurriculum,
  useEnrollCurriculum,
  type CurriculumTemplate,
} from '../hooks/useCurriculum';

/**
 * CurriculumBrowserPage - Browse and Enroll in Curricula
 *
 * Features:
 * - View all available curriculum templates
 * - Filter by genre and skill level
 * - See active curriculum progress
 * - Enroll in new curricula
 * - Generate custom AI curricula
 */

const CurriculumBrowserPage: React.FC = () => {
  const [selectedGenre, setSelectedGenre] = useState<string>('all');
  const [selectedLevel, setSelectedLevel] = useState<string>('all');

  // Fetch data using React Query hooks
  const { data: templates, isLoading: templatesLoading, error: templatesError } = useCurriculumTemplates();
  const { data: activeCurriculum, isLoading: activeLoading } = useActiveCurriculum();
  const enrollMutation = useEnrollCurriculum();

  // Filter templates
  const filteredTemplates = React.useMemo(() => {
    if (!templates) return [];

    return templates.filter((template) => {
      const matchesGenre = selectedGenre === 'all' || template.genre === selectedGenre;
      const matchesLevel = selectedLevel === 'all' || template.skill_level === selectedLevel;
      return matchesGenre && matchesLevel;
    });
  }, [templates, selectedGenre, selectedLevel]);

  const handleEnroll = async (templateId: string) => {
    try {
      await enrollMutation.mutateAsync(templateId);
      // Success feedback could be added here
    } catch (error) {
      console.error('Failed to enroll:', error);
      // Error feedback could be added here
    }
  };

  const genres = [
    { value: 'all', label: 'All Genres' },
    { value: 'gospel', label: 'Gospel' },
    { value: 'jazz', label: 'Jazz' },
    { value: 'blues', label: 'Blues' },
    { value: 'neosoul', label: 'Neo-Soul' },
    { value: 'classical', label: 'Classical' },
  ];

  const levels = [
    { value: 'all', label: 'All Levels' },
    { value: 'beginner', label: 'Beginner' },
    { value: 'intermediate', label: 'Intermediate' },
    { value: 'advanced', label: 'Advanced' },
  ];

  return (
    <div className="min-h-screen bg-background-dark">
      <Header currentPath="/curriculum" />

      {/* Page Header */}
      <section className="py-12 bg-gradient-to-br from-background-dark via-background-card to-background-dark border-b border-border-default">
        <Container>
          <Stack spacing={6}>
            <div>
              <h1 className="text-5xl font-extrabold text-text-primary mb-4">
                Curriculum Library
              </h1>
              <p className="text-xl text-text-secondary max-w-3xl">
                Structured learning paths designed to take you from beginner to advanced.
                Choose a curriculum or let our AI create one tailored to your goals.
              </p>
            </div>

            {/* Filters */}
            <Stack direction="horizontal" spacing={4} wrap className="mt-4">
              {/* Genre Filter */}
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-2">
                  Genre
                </label>
                <select
                  value={selectedGenre}
                  onChange={(e) => setSelectedGenre(e.target.value)}
                  className="px-4 py-2 bg-background-card border border-border-default rounded-DEFAULT text-text-primary focus:outline-none focus:ring-2 focus:ring-primary-cyan-500"
                >
                  {genres.map((genre) => (
                    <option key={genre.value} value={genre.value}>
                      {genre.label}
                    </option>
                  ))}
                </select>
              </div>

              {/* Level Filter */}
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-2">
                  Skill Level
                </label>
                <select
                  value={selectedLevel}
                  onChange={(e) => setSelectedLevel(e.target.value)}
                  className="px-4 py-2 bg-background-card border border-border-default rounded-DEFAULT text-text-primary focus:outline-none focus:ring-2 focus:ring-primary-cyan-500"
                >
                  {levels.map((level) => (
                    <option key={level.value} value={level.value}>
                      {level.label}
                    </option>
                  ))}
                </select>
              </div>

              {/* Generate AI Curriculum Button */}
              <div className="ml-auto">
                <label className="block text-sm font-medium text-text-secondary mb-2 opacity-0">
                  Actions
                </label>
                <Button variant="primary" size="md">
                  🤖 Generate Custom Curriculum
                </Button>
              </div>
            </Stack>
          </Stack>
        </Container>
      </section>

      {/* Active Curriculum */}
      {!activeLoading && activeCurriculum && (
        <section className="py-12 bg-background-card/30 border-b border-border-default">
          <Container>
            <Stack spacing={6}>
              <div className="flex items-center justify-between">
                <h2 className="text-3xl font-bold text-text-primary">
                  Your Active Curriculum
                </h2>
                <Badge variant="primary" size="lg">
                  In Progress
                </Badge>
              </div>

              <Card variant="elevated" padding="lg">
                <Stack spacing={6}>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="text-2xl font-bold text-text-primary mb-2">
                        {activeCurriculum.title}
                      </h3>
                      <p className="text-text-secondary mb-4">
                        {activeCurriculum.description}
                      </p>
                      <Stack direction="horizontal" spacing={2}>
                        <Badge variant="default" outlined>
                          {activeCurriculum.duration_weeks} weeks
                        </Badge>
                        <Badge variant="default" outlined>
                          {activeCurriculum.modules?.length || 0} modules
                        </Badge>
                      </Stack>
                    </div>
                    <Button variant="primary" size="lg">
                      Continue Learning →
                    </Button>
                  </div>

                  <ProgressBar
                    value={activeCurriculum.progress_percentage || 0}
                    variant="primary"
                    size="lg"
                    showLabel
                    label={`Overall Progress: ${Math.round(activeCurriculum.progress_percentage || 0)}%`}
                  />
                </Stack>
              </Card>
            </Stack>
          </Container>
        </section>
      )}

      {/* Browse Curricula */}
      <section className="py-16">
        <Container>
          <Stack spacing={6}>
            <div className="flex items-center justify-between">
              <h2 className="text-3xl font-bold text-text-primary">
                {selectedGenre === 'all' ? 'All Curricula' : `${genres.find(g => g.value === selectedGenre)?.label} Curricula`}
              </h2>
              <Badge variant="default" size="lg">
                {filteredTemplates.length} {filteredTemplates.length === 1 ? 'curriculum' : 'curricula'}
              </Badge>
            </div>

            {/* Loading State */}
            {templatesLoading && (
              <div className="text-center py-12">
                <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-cyan-500"></div>
                <p className="text-text-secondary mt-4">Loading curricula...</p>
              </div>
            )}

            {/* Error State */}
            {templatesError && (
              <Card variant="bordered" padding="lg">
                <Stack spacing={4} align="center">
                  <div className="text-6xl">⚠️</div>
                  <div className="text-center">
                    <h3 className="text-xl font-bold text-text-primary mb-2">
                      Failed to Load Curricula
                    </h3>
                    <p className="text-text-secondary">
                      {templatesError instanceof Error ? templatesError.message : 'An error occurred'}
                    </p>
                  </div>
                  <Button variant="primary" onClick={() => window.location.reload()}>
                    Retry
                  </Button>
                </Stack>
              </Card>
            )}

            {/* Curricula Grid */}
            {!templatesLoading && !templatesError && filteredTemplates.length > 0 && (
              <Grid cols={3} gap={6}>
                {filteredTemplates.map((template) => (
                  <CurriculumCard
                    key={template.id}
                    id={template.id}
                    title={template.title}
                    description={template.description}
                    genre={template.genre as any}
                    skillLevel={template.skill_level as any}
                    duration={template.duration_weeks}
                    lessonsCount={template.lessons_count}
                    enrolled={template.is_enrolled}
                    onEnroll={() => handleEnroll(template.id)}
                    onView={() => console.log('View', template.id)}
                  />
                ))}
              </Grid>
            )}

            {/* Empty State */}
            {!templatesLoading && !templatesError && filteredTemplates.length === 0 && (
              <Card variant="bordered" padding="lg">
                <Stack spacing={4} align="center" className="py-8">
                  <div className="text-6xl">🎵</div>
                  <div className="text-center">
                    <h3 className="text-xl font-bold text-text-primary mb-2">
                      No Curricula Found
                    </h3>
                    <p className="text-text-secondary">
                      Try adjusting your filters or generate a custom curriculum with AI.
                    </p>
                  </div>
                  <Button
                    variant="primary"
                    onClick={() => {
                      setSelectedGenre('all');
                      setSelectedLevel('all');
                    }}
                  >
                    Clear Filters
                  </Button>
                </Stack>
              </Card>
            )}
          </Stack>
        </Container>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-primary-cyan-500 to-primary-purple-500">
        <Container>
          <Stack spacing={6} align="center" className="text-center">
            <h2 className="text-4xl font-bold text-white">
              Can't Find What You're Looking For?
            </h2>
            <p className="text-xl text-white/90 max-w-2xl">
              Let our AI create a personalized curriculum based on your specific goals,
              skill level, and musical interests.
            </p>
            <Button variant="secondary" size="lg">
              Generate Custom Curriculum
            </Button>
          </Stack>
        </Container>
      </section>
    </div>
  );
};

export default CurriculumBrowserPage;
