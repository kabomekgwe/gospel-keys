import React from 'react';
import { Link } from '@tanstack/react-router';
import { Header } from '../design-system/components/organisms';
import { Container, Stack, Grid } from '../design-system/components/templates';
import { Button, Badge, ProgressCircle } from '../design-system/components/atoms';
import { Card, ExerciseCard, CurriculumCard } from '../design-system/components/molecules';

/**
 * HomePage - Main landing/dashboard page
 *
 * Features:
 * - Hero section with CTA
 * - Quick stats overview
 * - Featured curricula
 * - Recent practice sessions
 * - Genre showcase
 */

const HomePage: React.FC = () => {
  // Mock data - will be replaced with real API calls
  const userStats = {
    level: 5,
    xp: 2340,
    nextLevelXp: 3000,
    streak: 7,
    completedExercises: 45,
  };

  const featuredCurricula = [
    {
      id: '1',
      title: 'Gospel Keys Essentials',
      description: 'Master fundamental gospel piano techniques with authentic voicings and progressions',
      genre: 'gospel' as const,
      skillLevel: 'beginner' as const,
      duration: 12,
      lessonsCount: 36,
      enrolled: true,
      progress: 65,
    },
    {
      id: '2',
      title: 'Jazz Improvisation Bootcamp',
      description: 'Learn jazz theory, improvisation techniques, and standards analysis',
      genre: 'jazz' as const,
      skillLevel: 'intermediate' as const,
      duration: 10,
      lessonsCount: 40,
      enrolled: false,
    },
    {
      id: '3',
      title: 'Neo-Soul Harmony Mastery',
      description: 'Explore contemporary gospel and neo-soul chord progressions',
      genre: 'neosoul' as const,
      skillLevel: 'intermediate' as const,
      duration: 8,
      lessonsCount: 24,
      enrolled: false,
    },
  ];

  const recentExercises = [
    {
      id: '1',
      title: 'Seventh Chord Voicings',
      description: 'Practice maj7, min7, and dom7 voicings in all keys',
      genre: 'gospel' as const,
      difficulty: 'beginner' as const,
      duration: 15,
      progress: 80,
      bpm: 120,
    },
    {
      id: '2',
      title: 'ii-V-I Progressions',
      description: 'Master the most important progression in jazz',
      genre: 'jazz' as const,
      difficulty: 'intermediate' as const,
      duration: 20,
      progress: 45,
      bpm: 140,
    },
  ];

  const genres = [
    { name: 'Gospel', color: 'from-primary-purple-500 to-primary-purple-700', count: 120 },
    { name: 'Jazz', color: 'from-status-warning-DEFAULT to-status-warning-dark', count: 95 },
    { name: 'Blues', color: 'from-status-info-DEFAULT to-status-info-dark', count: 68 },
    { name: 'Neo-Soul', color: 'from-pink-500 to-orange-500', count: 82 },
    { name: 'Classical', color: 'from-indigo-500 to-primary-purple-500', count: 150 },
  ];

  return (
    <div className="min-h-screen bg-background-dark">
      <Header currentPath="/" />

      {/* Hero Section */}
      <section className="relative overflow-hidden py-20 bg-gradient-to-br from-background-dark via-background-card to-background-dark">
        <Container>
          <Stack spacing={8} align="center" className="text-center">
            <Badge variant="primary" size="lg" pill>
              🎹 AI-Powered Music Education
            </Badge>

            <h1 className="text-6xl font-extrabold text-text-primary max-w-4xl">
              Master Piano with{' '}
              <span className="bg-gradient-to-r from-primary-cyan-500 to-primary-purple-500 bg-clip-text text-transparent">
                Gospel Keys
              </span>
            </h1>

            <p className="text-xl text-text-secondary max-w-2xl">
              Learn gospel, jazz, blues, and more with personalized AI-generated curriculum,
              real-time feedback, and adaptive practice sessions.
            </p>

            <Stack direction="horizontal" spacing={4} className="mt-4">
              <Link to="/curriculum">
                <Button variant="primary" size="lg">
                  Browse Curriculum
                </Button>
              </Link>
              <Link to="/practice">
                <Button variant="ghost" size="lg">
                  Start Practicing
                </Button>
              </Link>
            </Stack>
          </Stack>
        </Container>

        {/* Decorative gradient orbs */}
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-primary-cyan-500/10 rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-primary-purple-500/10 rounded-full blur-3xl" />
      </section>

      {/* User Stats */}
      <section className="py-12 border-b border-border-default">
        <Container>
          <Grid cols={4} gap={6}>
            <Card variant="elevated" padding="lg">
              <Stack spacing={4} align="center">
                <ProgressCircle
                  value={(userStats.xp / userStats.nextLevelXp) * 100}
                  variant="primary"
                  size="lg"
                  label={<span className="text-2xl">L{userStats.level}</span>}
                />
                <div className="text-center">
                  <p className="text-sm text-text-muted">Level Progress</p>
                  <p className="text-lg font-bold text-text-primary">
                    {userStats.xp} / {userStats.nextLevelXp} XP
                  </p>
                </div>
              </Stack>
            </Card>

            <Card variant="elevated" padding="lg">
              <Stack spacing={4} align="center">
                <div className="w-16 h-16 bg-status-success-DEFAULT/20 rounded-full flex items-center justify-center">
                  <span className="text-3xl">🔥</span>
                </div>
                <div className="text-center">
                  <p className="text-sm text-text-muted">Day Streak</p>
                  <p className="text-3xl font-bold text-status-success-DEFAULT">
                    {userStats.streak}
                  </p>
                </div>
              </Stack>
            </Card>

            <Card variant="elevated" padding="lg">
              <Stack spacing={4} align="center">
                <div className="w-16 h-16 bg-primary-purple-500/20 rounded-full flex items-center justify-center">
                  <span className="text-3xl">✓</span>
                </div>
                <div className="text-center">
                  <p className="text-sm text-text-muted">Completed</p>
                  <p className="text-3xl font-bold text-text-primary">
                    {userStats.completedExercises}
                  </p>
                </div>
              </Stack>
            </Card>

            <Card variant="elevated" padding="lg">
              <Stack spacing={4} align="center">
                <div className="w-16 h-16 bg-primary-cyan-500/20 rounded-full flex items-center justify-center">
                  <span className="text-3xl">🎵</span>
                </div>
                <div className="text-center">
                  <p className="text-sm text-text-muted">Total Practice</p>
                  <p className="text-3xl font-bold text-text-primary">
                    {userStats.completedExercises * 15}m
                  </p>
                </div>
              </Stack>
            </Card>
          </Grid>
        </Container>
      </section>

      {/* Continue Learning */}
      {recentExercises.length > 0 && (
        <section className="py-16">
          <Container>
            <Stack spacing={6}>
              <div className="flex items-center justify-between">
                <h2 className="text-3xl font-bold text-text-primary">Continue Learning</h2>
                <Link to="/practice">
                  <Button variant="ghost" size="sm">View All →</Button>
                </Link>
              </div>

              <Grid cols={2} gap={6}>
                {recentExercises.map((exercise) => (
                  <ExerciseCard key={exercise.id} {...exercise} />
                ))}
              </Grid>
            </Stack>
          </Container>
        </section>
      )}

      {/* Featured Curricula */}
      <section className="py-16 bg-background-card/30">
        <Container>
          <Stack spacing={6}>
            <div className="flex items-center justify-between">
              <h2 className="text-3xl font-bold text-text-primary">Featured Curricula</h2>
              <Link to="/curriculum">
                <Button variant="ghost" size="sm">Browse All →</Button>
              </Link>
            </div>

            <Grid cols={3} gap={6}>
              {featuredCurricula.map((curriculum) => (
                <CurriculumCard key={curriculum.id} {...curriculum} />
              ))}
            </Grid>
          </Stack>
        </Container>
      </section>

      {/* Genres Showcase */}
      <section className="py-16">
        <Container>
          <Stack spacing={6}>
            <h2 className="text-3xl font-bold text-text-primary text-center">
              Explore Genres
            </h2>
            <p className="text-lg text-text-secondary text-center max-w-2xl mx-auto">
              Dive deep into different musical styles with genre-specific lessons,
              exercises, and theory concepts.
            </p>

            <Grid cols={5} gap={4} className="mt-8">
              {genres.map((genre) => (
                <Card
                  key={genre.name}
                  variant="elevated"
                  padding="md"
                  hover
                  interactive
                  className="cursor-pointer"
                >
                  <Stack spacing={4} align="center">
                    <div className={`w-full h-24 bg-gradient-to-br ${genre.color} rounded-md`} />
                    <h3 className="text-lg font-bold text-text-primary">{genre.name}</h3>
                    <Badge variant="default" size="sm">
                      {genre.count} lessons
                    </Badge>
                  </Stack>
                </Card>
              ))}
            </Grid>
          </Stack>
        </Container>
      </section>

      {/* Footer CTA */}
      <section className="py-20 bg-gradient-to-r from-primary-cyan-500 to-primary-purple-500">
        <Container>
          <Stack spacing={6} align="center" className="text-center">
            <h2 className="text-4xl font-bold text-white">
              Ready to Transform Your Playing?
            </h2>
            <p className="text-xl text-white/90 max-w-2xl">
              Join thousands of musicians improving their skills with AI-powered practice and personalized feedback.
            </p>
            <Link to="/curriculum">
              <Button variant="secondary" size="lg">
                Get Started Free
              </Button>
            </Link>
          </Stack>
        </Container>
      </section>
    </div>
  );
};

export default HomePage;
