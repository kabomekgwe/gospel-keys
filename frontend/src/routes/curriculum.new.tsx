import { createFileRoute, useNavigate, Link } from '@tanstack/react-router';
import {
  useCreateDefaultCurriculum,
  useCreateCurriculumFromTemplate,
  useCurriculumTemplates,
  useGenerateCurriculum
} from '../hooks/useCurriculum';
import { useToast } from '../components/ui/toast';
import { PageHeader } from '@/components/ui/page-header';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ArrowLeft, Sparkles, FileText, Clock, Target, Brain, Music, ChevronRight, ChevronLeft, Check } from 'lucide-react';
import { useState } from 'react';

export const Route = createFileRoute('/curriculum/new')({
  component: NewCurriculumPage,
});

// Genre options with icons and descriptions
const GENRES = [
  { id: 'gospel', label: 'Gospel', emoji: '⛪', desc: 'Traditional & contemporary church music' },
  { id: 'jazz', label: 'Jazz', emoji: '🎷', desc: 'Standards, improvisation & bebop' },
  { id: 'blues', label: 'Blues', emoji: '🎸', desc: '12-bar blues, turnarounds & licks' },
  { id: 'classical', label: 'Classical', emoji: '🎼', desc: 'Technique, repertoire & theory' },
  { id: 'neosoul', label: 'Neo-Soul', emoji: '💜', desc: 'R&B, soul & modern grooves' },
  { id: 'worship', label: 'Worship', emoji: '🙌', desc: 'Contemporary praise & worship' },
  { id: 'latin', label: 'Latin', emoji: '💃', desc: 'Bossa nova, salsa & Afro-Cuban' },
];

// Skill level options
const SKILL_LEVELS = [
  { id: 'beginner', label: 'Beginner', desc: 'New to piano or just starting' },
  { id: 'intermediate', label: 'Intermediate', desc: '1-3 years experience' },
  { id: 'advanced', label: 'Advanced', desc: '3+ years, comfortable with theory' },
];

// Learning goals
const GOALS = [
  { id: 'church', label: 'Play in church/worship band' },
  { id: 'improvise', label: 'Improvise freely' },
  { id: 'standards', label: 'Learn jazz standards' },
  { id: 'byear', label: 'Play by ear' },
  { id: 'compose', label: 'Write my own songs' },
  { id: 'accompany', label: 'Accompany singers' },
  { id: 'technique', label: 'Improve technique' },
  { id: 'theory', label: 'Understand music theory' },
];

function NewCurriculumPage() {
  const navigate = useNavigate();
  const { addToast } = useToast();
  const { data: templates, isLoading: templatesLoading } = useCurriculumTemplates();
  const createDefault = useCreateDefaultCurriculum();
  const createFromTemplate = useCreateCurriculumFromTemplate();
  const generateCurriculum = useGenerateCurriculum();

  const [mode, setMode] = useState<'template' | 'custom'>('template');

  // Wizard state
  const [wizardStep, setWizardStep] = useState(1);
  const [selectedGenre, setSelectedGenre] = useState<string>('');
  const [skillLevel, setSkillLevel] = useState<string>('');
  const [canReadMusic, setCanReadMusic] = useState<string>('');
  const [yearsExperience, setYearsExperience] = useState<string>('');
  const [selectedGoals, setSelectedGoals] = useState<string[]>([]);
  const [daysPerWeek, setDaysPerWeek] = useState(3);
  const [sessionLength, setSessionLength] = useState<string>('30min');
  const [customWeeks, setCustomWeeks] = useState(12);

  const TOTAL_STEPS = 5;

  const handleCreateFromTemplate = async (templateId: string, type: 'default' | 'dynamic') => {
    try {
      addToast({
        title: 'Creating curriculum...',
        description: `Setting up your new curriculum from ${type} template`,
        variant: 'info',
        duration: 3000,
      });

      let curriculum;
      if (type === 'default') {
        curriculum = await createDefault.mutateAsync({ template_key: templateId });
      } else {
        curriculum = await createFromTemplate.mutateAsync({ template_id: templateId });
      }

      addToast({
        title: 'Curriculum created!',
        description: 'Your new curriculum is ready',
        variant: 'success',
      });

      navigate({ to: '/curriculum/$curriculumId', params: { curriculumId: curriculum.id } });
    } catch (error) {
      console.error('Failed to create curriculum:', error);

      let errorMessage = 'An unexpected error occurred';
      if (error instanceof Error) {
        errorMessage = error.message;
      }

      addToast({
        title: 'Failed to create curriculum',
        description: errorMessage,
        variant: 'error',
        duration: 7000,
      });
    }
  };

  const toggleGoal = (goalId: string) => {
    setSelectedGoals(prev =>
      prev.includes(goalId)
        ? prev.filter(g => g !== goalId)
        : [...prev, goalId]
    );
  };

  const buildCurriculumTitle = () => {
    const genre = GENRES.find(g => g.id === selectedGenre);
    const level = SKILL_LEVELS.find(l => l.id === skillLevel);
    if (genre && level) {
      return `${genre.label} Piano: ${level.label} Journey`;
    }
    return 'My Custom Curriculum';
  };

  const handleGenerateCustom = async () => {
    try {
      addToast({
        title: 'Generating curriculum...',
        description: 'AI is creating your personalized curriculum. This may take 30-60 seconds.',
        variant: 'info',
        duration: 5000,
      });

      // Build a rich title based on wizard selections
      const title = buildCurriculumTitle();

      const curriculum = await generateCurriculum.mutateAsync({
        title,
        duration_weeks: customWeeks,
        // Pass wizard data for full personalization
        genre: selectedGenre,
        skill_level: skillLevel,
        goals: selectedGoals,
        days_per_week: daysPerWeek,
        session_length: sessionLength,
      });

      addToast({
        title: 'Curriculum generated!',
        description: 'Your AI-powered curriculum is ready',
        variant: 'success',
      });

      navigate({ to: '/curriculum/$curriculumId', params: { curriculumId: curriculum.id } });
    } catch (error) {
      console.error('Failed to generate curriculum:', error);

      let errorMessage = 'An unexpected error occurred';
      if (error instanceof Error) {
        errorMessage = error.message;
      }

      addToast({
        title: 'Failed to generate curriculum',
        description: errorMessage,
        variant: 'error',
        duration: 7000,
      });
    }
  };

  const canProceedToNextStep = () => {
    switch (wizardStep) {
      case 1: return selectedGenre !== '';
      case 2: return skillLevel !== '' && canReadMusic !== '' && yearsExperience !== '';
      case 3: return selectedGoals.length > 0;
      case 4: return true;
      case 5: return true;
      default: return false;
    }
  };

  if (templatesLoading) {
    return <div className="text-center py-8">Loading templates...</div>;
  }

  return (
    <div>
      {/* Back Button */}
      <Link
        to="/curriculum"
        className="inline-flex items-center gap-2 text-sm text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white mb-6 transition-colors"
      >
        <ArrowLeft className="size-4" />
        Back to curriculum
      </Link>

      {/* Page Header */}
      <PageHeader
        title="Create New Curriculum"
        description="Choose a template or generate a personalized curriculum with AI"
      />

      {/* Mode Toggle */}
      <div className="flex gap-3 mb-8">
        <Button
          onClick={() => setMode('template')}
          variant={mode === 'template' ? 'primary' : 'outline'}
          size="lg"
          className="flex-1"
        >
          <FileText className="size-4 mr-2" />
          From Template
        </Button>
        <Button
          onClick={() => setMode('custom')}
          variant={mode === 'custom' ? 'primary' : 'outline'}
          size="lg"
          className="flex-1"
        >
          <Sparkles className="size-4 mr-2" />
          AI Generated
        </Button>
      </div>

      {/* Template Mode */}
      {mode === 'template' && (
        <div>
          <div className="mb-8">
            <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">
              Pre-Built Templates
            </h3>
            <p className="text-slate-600 dark:text-slate-400">
              Choose from expertly designed curriculum templates created by professional music educators.
              Each template includes structured modules, lessons, and exercises tailored to specific genres and skill levels.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {templates?.map((template) => {
              // Determine genre variant for styling
              const genreKey = template.id.split('_')[0];
              const variantMap: Record<string, any> = {
                gospel: 'gospel',
                jazz: 'jazz',
                neosoul: 'neosoul',
                blues: 'default',
                classical: 'default',
                latin: 'default',
                modern: 'neosoul',
                worship: 'gospel',
                berklee: 'jazz',
              };
              const cardVariant = variantMap[genreKey] || 'interactive';

              return (
                <Card
                  key={template.id}
                  variant={cardVariant}
                  className="h-full hover:shadow-2xl transition-all duration-300 border-2"
                >
                  <CardHeader>
                    <div className="flex items-start justify-between mb-3">
                      <CardTitle as="h3" className="text-lg">
                        {template.title}
                      </CardTitle>
                      <Badge variant="default" className="shrink-0">
                        {template.weeks}w
                      </Badge>
                    </div>
                    <CardDescription className="line-clamp-2 min-h-[2.5rem] text-sm">
                      {template.description}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="flex items-center gap-4 text-xs">
                      <div className="flex items-center gap-1.5 text-slate-600 dark:text-slate-400">
                        <Clock className="size-3.5" />
                        <span>{template.weeks} weeks</span>
                      </div>
                      <div className="flex items-center gap-1.5 text-slate-600 dark:text-slate-400">
                        <FileText className="size-3.5" />
                        <span>{template.type === 'default' ? 'Expert designed' : 'Dynamic Template'}</span>
                      </div>
                    </div>
                  </CardContent>
                  <CardFooter>
                    <Button
                      onClick={() => handleCreateFromTemplate(template.id, template.type)}
                      disabled={createDefault.isPending || createFromTemplate.isPending}
                      variant="primary"
                      size="default"
                      className="w-full"
                    >
                      {createDefault.isPending || createFromTemplate.isPending ? 'Creating...' : 'Select Template'}
                    </Button>
                  </CardFooter>
                </Card>
              );
            })}
          </div>
        </div>
      )}

      {/* Custom Mode - AI Wizard */}
      {mode === 'custom' && (
        <div className="max-w-3xl mx-auto">
          {/* Progress Bar */}
          <div className="mb-8">
            <div className="flex justify-between mb-2">
              {[1, 2, 3, 4, 5].map((step) => (
                <div
                  key={step}
                  className={`flex items-center justify-center size-8 rounded-full text-sm font-medium transition-colors ${step === wizardStep
                    ? 'bg-purple-600 text-white'
                    : step < wizardStep
                      ? 'bg-green-500 text-white'
                      : 'bg-slate-200 dark:bg-slate-700 text-slate-600 dark:text-slate-400'
                    }`}
                >
                  {step < wizardStep ? <Check className="size-4" /> : step}
                </div>
              ))}
            </div>
            <div className="h-2 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
              <div
                className="h-full bg-purple-600 transition-all duration-300"
                style={{ width: `${((wizardStep - 1) / (TOTAL_STEPS - 1)) * 100}%` }}
              />
            </div>
          </div>

          {/* Step 1: Genre Selection */}
          {wizardStep === 1 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Music className="size-5 text-purple-600" />
                  What style do you want to learn?
                </CardTitle>
                <CardDescription>
                  Choose the genre that excites you most. This helps us tailor your curriculum.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                  {GENRES.map((genre) => (
                    <button
                      key={genre.id}
                      onClick={() => setSelectedGenre(genre.id)}
                      className={`p-4 rounded-xl border-2 text-left transition-all ${selectedGenre === genre.id
                        ? 'border-purple-500 bg-purple-50 dark:bg-purple-950/30'
                        : 'border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600'
                        }`}
                    >
                      <div className="text-2xl mb-2">{genre.emoji}</div>
                      <div className="font-semibold text-slate-900 dark:text-white">{genre.label}</div>
                      <div className="text-xs text-slate-600 dark:text-slate-400 mt-1">{genre.desc}</div>
                    </button>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Step 2: Skill Assessment */}
          {wizardStep === 2 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Target className="size-5 text-purple-600" />
                  Tell us about your current level
                </CardTitle>
                <CardDescription>
                  This helps us start you at the right place—not too easy, not too hard.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-slate-900 dark:text-white mb-3">
                    What's your current skill level?
                  </label>
                  <div className="grid grid-cols-3 gap-3">
                    {SKILL_LEVELS.map((level) => (
                      <button
                        key={level.id}
                        onClick={() => setSkillLevel(level.id)}
                        className={`p-3 rounded-lg border-2 text-center transition-all ${skillLevel === level.id
                          ? 'border-purple-500 bg-purple-50 dark:bg-purple-950/30'
                          : 'border-slate-200 dark:border-slate-700 hover:border-slate-300'
                          }`}
                      >
                        <div className="font-medium text-slate-900 dark:text-white">{level.label}</div>
                        <div className="text-xs text-slate-600 dark:text-slate-400 mt-1">{level.desc}</div>
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-900 dark:text-white mb-3">
                    Can you read sheet music?
                  </label>
                  <div className="grid grid-cols-3 gap-3">
                    {[
                      { id: 'yes', label: 'Yes' },
                      { id: 'some', label: 'Somewhat' },
                      { id: 'no', label: 'No' },
                    ].map((opt) => (
                      <button
                        key={opt.id}
                        onClick={() => setCanReadMusic(opt.id)}
                        className={`p-3 rounded-lg border-2 text-center transition-all ${canReadMusic === opt.id
                          ? 'border-purple-500 bg-purple-50 dark:bg-purple-950/30'
                          : 'border-slate-200 dark:border-slate-700 hover:border-slate-300'
                          }`}
                      >
                        <div className="font-medium text-slate-900 dark:text-white">{opt.label}</div>
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-900 dark:text-white mb-3">
                    Years of piano experience?
                  </label>
                  <div className="grid grid-cols-4 gap-3">
                    {[
                      { id: '0-1', label: '0-1' },
                      { id: '1-3', label: '1-3' },
                      { id: '3-5', label: '3-5' },
                      { id: '5+', label: '5+' },
                    ].map((opt) => (
                      <button
                        key={opt.id}
                        onClick={() => setYearsExperience(opt.id)}
                        className={`p-3 rounded-lg border-2 text-center transition-all ${yearsExperience === opt.id
                          ? 'border-purple-500 bg-purple-50 dark:bg-purple-950/30'
                          : 'border-slate-200 dark:border-slate-700 hover:border-slate-300'
                          }`}
                      >
                        <div className="font-medium text-slate-900 dark:text-white">{opt.label}</div>
                      </button>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Step 3: Goals & Motivation */}
          {wizardStep === 3 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Sparkles className="size-5 text-purple-600" />
                  What do you want to achieve?
                </CardTitle>
                <CardDescription>
                  Select all that apply. This shapes the focus of your curriculum.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-3">
                  {GOALS.map((goal) => (
                    <button
                      key={goal.id}
                      onClick={() => toggleGoal(goal.id)}
                      className={`p-4 rounded-lg border-2 text-left transition-all flex items-center gap-3 ${selectedGoals.includes(goal.id)
                        ? 'border-purple-500 bg-purple-50 dark:bg-purple-950/30'
                        : 'border-slate-200 dark:border-slate-700 hover:border-slate-300'
                        }`}
                    >
                      <div
                        className={`size-5 rounded border-2 flex items-center justify-center ${selectedGoals.includes(goal.id)
                          ? 'border-purple-500 bg-purple-500'
                          : 'border-slate-300 dark:border-slate-600'
                          }`}
                      >
                        {selectedGoals.includes(goal.id) && <Check className="size-3 text-white" />}
                      </div>
                      <span className="text-sm font-medium text-slate-900 dark:text-white">{goal.label}</span>
                    </button>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Step 4: Time Commitment */}
          {wizardStep === 4 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Clock className="size-5 text-purple-600" />
                  How much time can you commit?
                </CardTitle>
                <CardDescription>
                  Be realistic—consistency beats intensity. We'll pace your curriculum accordingly.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-slate-900 dark:text-white mb-3">
                    Practice days per week: <span className="text-purple-600">{daysPerWeek} days</span>
                  </label>
                  <input
                    type="range"
                    value={daysPerWeek}
                    onChange={(e) => setDaysPerWeek(Number(e.target.value))}
                    min={1}
                    max={7}
                    className="w-full h-2 bg-slate-200 dark:bg-slate-700 rounded-lg appearance-none cursor-pointer accent-purple-600"
                  />
                  <div className="flex justify-between mt-2 text-xs text-slate-500">
                    <span>1 day</span>
                    <span>7 days</span>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-900 dark:text-white mb-3">
                    Session length
                  </label>
                  <div className="grid grid-cols-4 gap-3">
                    {[
                      { id: '15min', label: '15 min' },
                      { id: '30min', label: '30 min' },
                      { id: '1hr', label: '1 hour' },
                      { id: '1hr+', label: '1+ hours' },
                    ].map((opt) => (
                      <button
                        key={opt.id}
                        onClick={() => setSessionLength(opt.id)}
                        className={`p-3 rounded-lg border-2 text-center transition-all ${sessionLength === opt.id
                          ? 'border-purple-500 bg-purple-50 dark:bg-purple-950/30'
                          : 'border-slate-200 dark:border-slate-700 hover:border-slate-300'
                          }`}
                      >
                        <div className="font-medium text-slate-900 dark:text-white text-sm">{opt.label}</div>
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-900 dark:text-white mb-3">
                    Curriculum duration: <span className="text-purple-600">{customWeeks} weeks</span>
                  </label>
                  <input
                    type="range"
                    value={customWeeks}
                    onChange={(e) => setCustomWeeks(Number(e.target.value))}
                    min={4}
                    max={52}
                    step={4}
                    className="w-full h-2 bg-slate-200 dark:bg-slate-700 rounded-lg appearance-none cursor-pointer accent-purple-600"
                  />
                  <div className="flex justify-between mt-2 text-xs text-slate-500">
                    <span>4 weeks (Sprint)</span>
                    <span>52 weeks (Year-long)</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Step 5: Review & Generate */}
          {wizardStep === 5 && (
            <Card className="border-purple-200 dark:border-purple-900">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Brain className="size-5 text-purple-600" />
                  Ready to generate your curriculum!
                </CardTitle>
                <CardDescription>
                  Here's a summary of your learning profile:
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div className="p-3 bg-slate-50 dark:bg-slate-800 rounded-lg">
                    <div className="text-slate-500 dark:text-slate-400">Genre</div>
                    <div className="font-semibold text-slate-900 dark:text-white">
                      {GENRES.find(g => g.id === selectedGenre)?.label || '-'}
                    </div>
                  </div>
                  <div className="p-3 bg-slate-50 dark:bg-slate-800 rounded-lg">
                    <div className="text-slate-500 dark:text-slate-400">Level</div>
                    <div className="font-semibold text-slate-900 dark:text-white">
                      {SKILL_LEVELS.find(l => l.id === skillLevel)?.label || '-'}
                    </div>
                  </div>
                  <div className="p-3 bg-slate-50 dark:bg-slate-800 rounded-lg">
                    <div className="text-slate-500 dark:text-slate-400">Duration</div>
                    <div className="font-semibold text-slate-900 dark:text-white">{customWeeks} weeks</div>
                  </div>
                  <div className="p-3 bg-slate-50 dark:bg-slate-800 rounded-lg">
                    <div className="text-slate-500 dark:text-slate-400">Practice</div>
                    <div className="font-semibold text-slate-900 dark:text-white">{daysPerWeek}x/week</div>
                  </div>
                </div>
                <div className="p-3 bg-slate-50 dark:bg-slate-800 rounded-lg">
                  <div className="text-slate-500 dark:text-slate-400 mb-2">Goals</div>
                  <div className="flex flex-wrap gap-2">
                    {selectedGoals.map(goalId => {
                      const goal = GOALS.find(g => g.id === goalId);
                      return goal ? (
                        <Badge key={goalId} variant="default">{goal.label}</Badge>
                      ) : null;
                    })}
                  </div>
                </div>
              </CardContent>
              <CardFooter>
                <Button
                  onClick={handleGenerateCustom}
                  disabled={generateCurriculum.isPending}
                  variant="primary"
                  size="xl"
                  className="w-full"
                >
                  <Sparkles className="size-5 mr-2" />
                  {generateCurriculum.isPending ? 'Generating Your Curriculum...' : 'Generate My Curriculum'}
                </Button>
              </CardFooter>
            </Card>
          )}

          {/* Navigation Buttons */}
          <div className="flex justify-between mt-6">
            <Button
              onClick={() => setWizardStep(prev => Math.max(1, prev - 1))}
              disabled={wizardStep === 1}
              variant="outline"
              size="lg"
            >
              <ChevronLeft className="size-4 mr-1" />
              Back
            </Button>
            {wizardStep < TOTAL_STEPS ? (
              <Button
                onClick={() => setWizardStep(prev => Math.min(TOTAL_STEPS, prev + 1))}
                disabled={!canProceedToNextStep()}
                variant="primary"
                size="lg"
              >
                Next
                <ChevronRight className="size-4 ml-1" />
              </Button>
            ) : null}
          </div>
        </div>
      )}
    </div>
  );
}

