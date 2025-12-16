import React, { useState } from 'react';
import { Header } from '../design-system/components/organisms';
import { Container, Stack, Grid } from '../design-system/components/templates';
import { Button, Badge, ProgressCircle } from '../design-system/components/atoms';
import { Card, ExerciseCard } from '../design-system/components/molecules';
import { useDailyPractice } from '../hooks/useCurriculum';
import { useExercises } from '../hooks/useExercises';

/**
 * PracticeSessionPage - Daily Practice Interface
 *
 * Features:
 * - Today's recommended exercises
 * - Practice streak tracking
 * - Quick practice mode
 * - Browse all exercises
 * - Performance analytics
 */

const PracticeSessionPage: React.FC = () => {
  const [selectedGenre, setSelectedGenre] = useState<string>('all');
  const [selectedDifficulty, setSelectedDifficulty] = useState<string>('all');

  // Fetch data
  const { data: dailyPractice, isLoading: dailyLoading } = useDailyPractice();
  const { data: exercises, isLoading: exercisesLoading } = useExercises({
    genre: selectedGenre !== 'all' ? selectedGenre : undefined,
    difficulty: selectedDifficulty !== 'all' ? selectedDifficulty : undefined,
  });

  const genres = [
    { value: 'all', label: 'All Genres', color: 'from-primary-cyan-500 to-primary-purple-500' },
    { value: 'gospel', label: 'Gospel', color: 'from-primary-purple-500 to-primary-purple-700' },
    { value: 'jazz', label: 'Jazz', color: 'from-status-warning-DEFAULT to-status-warning-dark' },
    { value: 'blues', label: 'Blues', color: 'from-status-info-DEFAULT to-status-info-dark' },
    { value: 'neosoul', label: 'Neo-Soul', color: 'from-pink-500 to-orange-500' },
    { value: 'classical', label: 'Classical', color: 'from-indigo-500 to-primary-purple-500' },
  ];

  // Mock stats - replace with real data
  const practiceStats = {
    todayMinutes: 45,
    weekMinutes: 180,
    streak: 7,
    target: 30,
  };

  return (
    <div className="min-h-screen bg-background-dark">
      <Header currentPath="/practice" />

      {/* Page Header with Stats */}
      <section className="py-12 bg-gradient-to-br from-background-dark via-background-card to-background-dark border-b border-border-default">
        <Container>
          <Grid cols={4} gap={6}>
            {/* Daily Goal */}
            <Card variant="elevated" padding="lg">
              <Stack spacing={4} align="center">
                <ProgressCircle
                  value={(practiceStats.todayMinutes / practiceStats.target) * 100}
                  variant="primary"
                  size="lg"
                  label={`${practiceStats.todayMinutes}m`}
                />
                <div className="text-center">
                  <p className="text-sm text-text-muted">Daily Goal</p>
                  <p className="text-lg font-bold text-text-primary">
                    {practiceStats.target} min
                  </p>
                </div>
              </Stack>
            </Card>

            {/* Streak */}
            <Card variant="elevated" padding="lg">
              <Stack spacing={4} align="center">
                <div className="w-16 h-16 bg-status-success-DEFAULT/20 rounded-full flex items-center justify-center">
                  <span className="text-3xl">🔥</span>
                </div>
                <div className="text-center">
                  <p className="text-sm text-text-muted">Current Streak</p>
                  <p className="text-3xl font-bold text-status-success-DEFAULT">
                    {practiceStats.streak} days
                  </p>
                </div>
              </Stack>
            </Card>

            {/* Week Total */}
            <Card variant="elevated" padding="lg">
              <Stack spacing={4} align="center">
                <div className="w-16 h-16 bg-primary-purple-500/20 rounded-full flex items-center justify-center">
                  <span className="text-3xl">📊</span>
                </div>
                <div className="text-center">
                  <p className="text-sm text-text-muted">This Week</p>
                  <p className="text-3xl font-bold text-text-primary">
                    {practiceStats.weekMinutes}m
                  </p>
                </div>
              </Stack>
            </Card>

            {/* Quick Practice */}
            <Card variant="glass" padding="lg" className="bg-gradient-to-br from-primary-cyan-500/20 to-primary-purple-500/20">
              <Stack spacing={4} align="center" justify="center" className="h-full">
                <Button variant="primary" size="lg" fullWidth>
                  🎹 Quick Practice
                </Button>
                <p className="text-xs text-text-muted text-center">
                  15 min session
                </p>
              </Stack>
            </Card>
          </Grid>
        </Container>
      </section>

      {/* Today's Practice */}
      {!dailyLoading && dailyPractice && dailyPractice.exercises?.length > 0 && (
        <section className="py-12 border-b border-border-default">
          <Container>
            <Stack spacing={6}>
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-3xl font-bold text-text-primary mb-2">
                    Today's Recommended Practice
                  </h2>
                  <p className="text-text-secondary">
                    Personalized exercises based on your learning progress
                  </p>
                </div>
                <Badge variant="primary" size="lg">
                  {dailyPractice.exercises.length} exercises
                </Badge>
              </div>

              <Grid cols={3} gap={6}>
                {dailyPractice.exercises.slice(0, 3).map((exercise: any, idx: number) => (
                  <ExerciseCard
                    key={idx}
                    title={exercise.title || 'Practice Exercise'}
                    description={exercise.description || ''}
                    genre={exercise.genre || 'gospel'}
                    difficulty={exercise.difficulty || 'beginner'}
                    duration={exercise.duration || 15}
                    progress={exercise.progress || 0}
                    bpm={exercise.bpm}
                  />
                ))}
              </Grid>
            </Stack>
          </Container>
        </section>
      )}

      {/* Browse by Genre */}
      <section className="py-16">
        <Container>
          <Stack spacing={6}>
            <div>
              <h2 className="text-3xl font-bold text-text-primary mb-2">
                Browse Exercises
              </h2>
              <p className="text-text-secondary">
                Find exercises by genre and difficulty level
              </p>
            </div>

            {/* Genre Tabs */}
            <div className="flex gap-2 overflow-x-auto pb-2">
              {genres.map((genre) => (
                <button
                  key={genre.value}
                  onClick={() => setSelectedGenre(genre.value)}
                  className={`
                    px-6 py-3 rounded-lg font-medium text-sm whitespace-nowrap
                    transition-all duration-fast
                    ${selectedGenre === genre.value
                      ? `bg-gradient-to-r ${genre.color} text-white shadow-lg`
                      : 'bg-background-card text-text-secondary hover:text-text-primary hover:bg-background-hover'
                    }
                  `}
                >
                  {genre.label}
                </button>
              ))}
            </div>

            {/* Difficulty Filter */}
            <Stack direction="horizontal" spacing={2}>
              {['all', 'beginner', 'intermediate', 'advanced'].map((level) => (
                <button
                  key={level}
                  onClick={() => setSelectedDifficulty(level)}
                  className="cursor-pointer"
                >
                  <Badge
                    variant={selectedDifficulty === level ? 'primary' : 'default'}
                    size="md"
                    outlined={selectedDifficulty !== level}
                  >
                    {level.charAt(0).toUpperCase() + level.slice(1)}
                  </Badge>
                </button>
              ))}
            </Stack>

            {/* Exercise Grid */}
            {exercisesLoading ? (
              <div className="text-center py-12">
                <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-cyan-500"></div>
                <p className="text-text-secondary mt-4">Loading exercises...</p>
              </div>
            ) : exercises && exercises.length > 0 ? (
              <Grid cols={3} gap={6}>
                {exercises.map((exercise) => (
                  <ExerciseCard
                    key={exercise.id}
                    title={exercise.title}
                    description={exercise.description}
                    genre={exercise.genre}
                    difficulty={exercise.difficulty}
                    duration={exercise.duration}
                    progress={exercise.progress}
                    bpm={exercise.bpm}
                    completed={exercise.completed}
                  />
                ))}
              </Grid>
            ) : (
              <Card variant="bordered" padding="lg">
                <Stack spacing={4} align="center" className="py-8">
                  <div className="text-6xl">🎵</div>
                  <div className="text-center">
                    <h3 className="text-xl font-bold text-text-primary mb-2">
                      No Exercises Found
                    </h3>
                    <p className="text-text-secondary">
                      Try selecting a different genre or difficulty level.
                    </p>
                  </div>
                  <Button
                    variant="primary"
                    onClick={() => {
                      setSelectedGenre('all');
                      setSelectedDifficulty('all');
                    }}
                  >
                    View All Exercises
                  </Button>
                </Stack>
              </Card>
            )}
          </Stack>
        </Container>
      </section>

      {/* Practice Tips */}
      <section className="py-16 bg-background-card/30">
        <Container>
          <Grid cols={3} gap={6}>
            <Card variant="glass" padding="lg">
              <Stack spacing={4}>
                <div className="text-4xl">🎯</div>
                <h3 className="text-xl font-bold text-text-primary">
                  Set Goals
                </h3>
                <p className="text-text-secondary">
                  Practice for at least 30 minutes daily to see consistent improvement.
                </p>
              </Stack>
            </Card>

            <Card variant="glass" padding="lg">
              <Stack spacing={4}>
                <div className="text-4xl">🔄</div>
                <h3 className="text-xl font-bold text-text-primary">
                  Use Repetition
                </h3>
                <p className="text-text-secondary">
                  Repeat difficult sections slowly before increasing tempo.
                </p>
              </Stack>
            </Card>

            <Card variant="glass" padding="lg">
              <Stack spacing={4}>
                <div className="text-4xl">📈</div>
                <h3 className="text-xl font-bold text-text-primary">
                  Track Progress
                </h3>
                <p className="text-text-secondary">
                  Review your practice stats to identify areas for improvement.
                </p>
              </Stack>
            </Card>
          </Grid>
        </Container>
      </section>
    </div>
  );
};

export default PracticeSessionPage;
