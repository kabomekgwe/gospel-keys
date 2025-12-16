import { createFileRoute, useNavigate, Link } from '@tanstack/react-router';
import {
  useCreateDefaultCurriculum,
  useCurriculumTemplates,
  useGenerateCurriculum
} from '../hooks/useCurriculum';
import { useToast } from '../components/ui/toast';
import { PageHeader } from '@/components/ui/page-header';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ArrowLeft, Sparkles, FileText, Clock, Target, Zap, Brain } from 'lucide-react';
import { useState } from 'react';

export const Route = createFileRoute('/curriculum/new')({
  component: NewCurriculumPage,
});

function NewCurriculumPage() {
  const navigate = useNavigate();
  const { addToast } = useToast();
  const { data: templates, isLoading: templatesLoading } = useCurriculumTemplates();
  const createDefault = useCreateDefaultCurriculum();
  const generateCurriculum = useGenerateCurriculum();

  const [mode, setMode] = useState<'template' | 'custom'>('template');
  const [customTitle, setCustomTitle] = useState('');
  const [customWeeks, setCustomWeeks] = useState(12);

  const handleCreateFromTemplate = async (templateKey: string) => {
    try {
      addToast({
        title: 'Creating curriculum...',
        description: 'Setting up your new curriculum from template',
        variant: 'info',
        duration: 3000,
      });

      const curriculum = await createDefault.mutateAsync({ template_key: templateKey });

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

  const handleGenerateCustom = async () => {
    try {
      addToast({
        title: 'Generating curriculum...',
        description: 'AI is creating your personalized curriculum. This may take 30-60 seconds.',
        variant: 'info',
        duration: 5000,
      });

      const curriculum = await generateCurriculum.mutateAsync({
        title: customTitle,
        duration_weeks: customWeeks,
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

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-6">
            {templates?.map((template) => {
              // Determine genre variant for styling
              const genreKey = template.key.split('_')[0]; // gospel, jazz, neosoul, etc.
              const variantMap: Record<string, any> = {
                gospel: 'gospel',
                jazz: 'jazz',
                neosoul: 'neosoul',
              };
              const cardVariant = variantMap[genreKey] || 'interactive';

              return (
                <Card
                  key={template.key}
                  variant={cardVariant}
                  className="h-full hover:shadow-2xl transition-all duration-300 border-2"
                >
                  <CardHeader>
                    <div className="flex items-start justify-between mb-3">
                      <CardTitle as="h3" className="text-xl">
                        {template.title}
                      </CardTitle>
                      <Badge variant="default" className="shrink-0">
                        {template.weeks}w
                      </Badge>
                    </div>
                    <CardDescription className="line-clamp-2 min-h-[2.5rem]">
                      {template.description}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex items-center gap-4 text-sm">
                      <div className="flex items-center gap-2 text-slate-600 dark:text-slate-400">
                        <Clock className="size-4" />
                        <span>{template.weeks} weeks</span>
                      </div>
                      <div className="flex items-center gap-2 text-slate-600 dark:text-slate-400">
                        <FileText className="size-4" />
                        <span>Expert designed</span>
                      </div>
                    </div>
                    {/* Feature list based on template */}
                    <div className="space-y-1.5">
                      <p className="text-xs font-medium text-slate-700 dark:text-slate-300">Includes:</p>
                      <ul className="text-xs text-slate-600 dark:text-slate-400 space-y-1">
                        <li className="flex items-start gap-2">
                          <span className="text-green-500 mt-0.5">✓</span>
                          <span>Structured learning path</span>
                        </li>
                        <li className="flex items-start gap-2">
                          <span className="text-green-500 mt-0.5">✓</span>
                          <span>Practice exercises & drills</span>
                        </li>
                        <li className="flex items-start gap-2">
                          <span className="text-green-500 mt-0.5">✓</span>
                          <span>Progressive difficulty</span>
                        </li>
                      </ul>
                    </div>
                  </CardContent>
                  <CardFooter>
                    <Button
                      onClick={() => handleCreateFromTemplate(template.key)}
                      disabled={createDefault.isPending}
                      variant="primary"
                      size="lg"
                      className="w-full"
                    >
                      {createDefault.isPending ? 'Creating...' : 'Select This Template'}
                    </Button>
                  </CardFooter>
                </Card>
              );
            })}
          </div>
        </div>
      )}

      {/* Custom Mode */}
      {mode === 'custom' && (
        <div className="max-w-4xl">
          <div className="mb-8">
            <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">
              AI-Powered Curriculum
            </h3>
            <p className="text-slate-600 dark:text-slate-400">
              Let our AI create a personalized curriculum tailored to your unique learning style, goals, and musical interests.
              The AI analyzes your skill profile and designs a comprehensive learning path just for you.
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left: Form */}
            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Brain className="size-5 text-purple-600" />
                  Curriculum Details
                </CardTitle>
                <CardDescription>
                  Tell us about your learning goals and we'll create a custom curriculum
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div>
                  <label className="block text-sm font-semibold text-slate-900 dark:text-white mb-2">
                    Curriculum Title *
                  </label>
                  <input
                    type="text"
                    value={customTitle}
                    onChange={(e) => setCustomTitle(e.target.value)}
                    placeholder="e.g., Gospel Piano Mastery, Jazz Improvisation Journey"
                    className="w-full px-4 py-3 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-white placeholder:text-slate-400 focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-colors"
                  />
                  <p className="mt-1.5 text-xs text-slate-500 dark:text-slate-400">
                    Choose a name that reflects your musical goals
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-semibold text-slate-900 dark:text-white mb-2">
                    Duration (weeks)
                  </label>
                  <div className="flex items-center gap-4">
                    <input
                      type="range"
                      value={customWeeks}
                      onChange={(e) => setCustomWeeks(Number(e.target.value))}
                      min={4}
                      max={52}
                      step={4}
                      className="flex-1 h-2 bg-slate-200 dark:bg-slate-700 rounded-lg appearance-none cursor-pointer accent-purple-600"
                    />
                    <Badge variant="default" className="text-base px-3 py-1 min-w-[4rem] text-center">
                      {customWeeks}w
                    </Badge>
                  </div>
                  <div className="flex justify-between mt-2 text-xs text-slate-500 dark:text-slate-400">
                    <span>4 weeks (Sprint)</span>
                    <span>52 weeks (Year-long)</span>
                  </div>
                  <p className="mt-1.5 text-xs text-slate-500 dark:text-slate-400">
                    Recommended: 12-24 weeks for comprehensive learning
                  </p>
                </div>
              </CardContent>
              <CardFooter className="flex flex-col gap-3">
                <Button
                  onClick={handleGenerateCustom}
                  disabled={!customTitle || generateCurriculum.isPending}
                  variant="primary"
                  size="xl"
                  className="w-full"
                >
                  <Sparkles className="size-5 mr-2" />
                  {generateCurriculum.isPending ? 'Generating Your Curriculum...' : 'Generate My Curriculum'}
                </Button>
                {!customTitle && (
                  <p className="text-xs text-center text-slate-500 dark:text-slate-400">
                    Enter a curriculum title to continue
                  </p>
                )}
              </CardFooter>
            </Card>

            {/* Right: AI Features */}
            <div className="space-y-6">
              <Card className="border-purple-200 dark:border-purple-900 bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-950/20 dark:to-pink-950/20">
                <CardHeader>
                  <div className="flex items-center gap-2 mb-2">
                    <Sparkles className="size-5 text-purple-600 dark:text-purple-400" />
                    <CardTitle className="text-base">AI-Powered</CardTitle>
                  </div>
                  <CardDescription className="text-purple-900 dark:text-purple-100">
                    Our AI analyzes your skill profile to create a personalized learning path
                  </CardDescription>
                </CardHeader>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-base flex items-center gap-2">
                    <Target className="size-4 text-blue-600" />
                    What You'll Get
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex items-start gap-3">
                    <div className="flex size-6 shrink-0 items-center justify-center rounded-full bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400">
                      <span className="text-xs">✓</span>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-slate-900 dark:text-white">Custom modules</p>
                      <p className="text-xs text-slate-600 dark:text-slate-400">Tailored to your skill level</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className="flex size-6 shrink-0 items-center justify-center rounded-full bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400">
                      <span className="text-xs">✓</span>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-slate-900 dark:text-white">Progressive lessons</p>
                      <p className="text-xs text-slate-600 dark:text-slate-400">Build skills incrementally</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className="flex size-6 shrink-0 items-center justify-center rounded-full bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400">
                      <span className="text-xs">✓</span>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-slate-900 dark:text-white">Practice exercises</p>
                      <p className="text-xs text-slate-600 dark:text-slate-400">Reinforce concepts</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-blue-50 dark:bg-blue-950/20 border-blue-200 dark:border-blue-900">
                <CardContent className="pt-6">
                  <div className="flex items-start gap-3">
                    <Zap className="size-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="text-sm font-medium text-blue-900 dark:text-blue-100 mb-1">
                        Generation Time
                      </p>
                      <p className="text-xs text-blue-700 dark:text-blue-300">
                        AI generation typically takes 30-60 seconds. We're creating a complete curriculum with multiple modules, lessons, and exercises.
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
