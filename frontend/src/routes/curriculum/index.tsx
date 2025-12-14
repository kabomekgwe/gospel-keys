import { createFileRoute } from '@tanstack/react-router';
import { useQuery } from '@tanstack/react-query';
import { curriculumApi, type CurriculumResponse } from '../../lib/api';
import { useState } from 'react';
import { GraduationCap, Sparkles, BookOpen, Target } from 'lucide-react';
import { CurriculumWizard } from '../../components/curriculum/CurriculumWizard';
import { DashboardHeader } from '../../components/curriculum/DashboardHeader';
import { CurriculumStats } from '../../components/curriculum/CurriculumStats';
import { CurriculumTimeline } from '../../components/curriculum/CurriculumTimeline';
import { ModuleGrid } from '../../components/curriculum/ModuleGrid';
import { AICoach } from '../../components/curriculum/AICoach';

export const Route = createFileRoute('/curriculum/')({
  component: CurriculumDashboard,
});

function CurriculumDashboard() {
  const { data: curriculum, isLoading, error } = useQuery({
    queryKey: ['curriculum', 'active'],
    queryFn: curriculumApi.getActiveCurriculum,
  });

  if (isLoading) {
    return <LoadingState />;
  }

  if (!curriculum || error) {
    return <EmptyState />;
  }

  return <DashboardView curriculum={curriculum} />;
}

function LoadingState() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-purple-500 mx-auto mb-4"></div>
        <p className="text-gray-400 text-lg">Loading your curriculum...</p>
      </div>
    </div>
  );
}

function EmptyState() {
  const [showWizard, setShowWizard] = useState(false);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 p-6 flex items-center justify-center">
      <div className="max-w-4xl w-full">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-24 h-24 bg-purple-500/20 rounded-full mb-6">
            <GraduationCap className="w-12 h-12 text-purple-400" />
          </div>
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Start Your Personalized Learning Journey
          </h1>
          <p className="text-xl text-gray-300 mb-8 max-w-2xl mx-auto">
            Take a quick assessment and we'll create a 12-week curriculum tailored to your skill level and goals
          </p>
          <button
            onClick={() => setShowWizard(true)}
            className="px-8 py-4 bg-purple-600 text-white font-semibold text-lg rounded-lg hover:bg-purple-500 transition shadow-lg hover:shadow-xl inline-flex items-center gap-2"
          >
            <Sparkles className="w-5 h-5" />
            Create Your Curriculum
          </button>
        </div>

        {/* Feature Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-gray-800/50 p-6 rounded-xl border border-gray-700">
            <div className="w-12 h-12 bg-purple-500/20 rounded-lg flex items-center justify-center mb-4">
              <Target className="w-6 h-6 text-purple-400" />
            </div>
            <h3 className="text-lg font-semibold text-white mb-2">Personalized Path</h3>
            <p className="text-gray-400 text-sm">
              AI-generated curriculum based on your unique skill profile and learning goals
            </p>
          </div>

          <div className="bg-gray-800/50 p-6 rounded-xl border border-gray-700">
            <div className="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center mb-4">
              <BookOpen className="w-6 h-6 text-blue-400" />
            </div>
            <h3 className="text-lg font-semibold text-white mb-2">Spaced Repetition</h3>
            <p className="text-gray-400 text-sm">
              Smart scheduling ensures you practice exercises at the optimal time for retention
            </p>
          </div>

          <div className="bg-gray-800/50 p-6 rounded-xl border border-gray-700">
            <div className="w-12 h-12 bg-green-500/20 rounded-lg flex items-center justify-center mb-4">
              <Sparkles className="w-6 h-6 text-green-400" />
            </div>
            <h3 className="text-lg font-semibold text-white mb-2">Adaptive Learning</h3>
            <p className="text-gray-400 text-sm">
              Curriculum automatically adjusts difficulty based on your performance and progress
            </p>
          </div>
        </div>

        {/* Curriculum Wizard */}
        {showWizard && <CurriculumWizard onClose={() => setShowWizard(false)} />}
      </div>
    </div>
  );
}

function DashboardView({ curriculum }: { curriculum: CurriculumResponse }) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 p-6">
      <div className="max-w-7xl mx-auto">
        <DashboardHeader curriculum={curriculum} />
        <CurriculumStats curriculum={curriculum} />
        <CurriculumTimeline curriculum={curriculum} />
        <ModuleGrid curriculum={curriculum} />
      </div>
      <AICoach />
    </div>
  );
}
