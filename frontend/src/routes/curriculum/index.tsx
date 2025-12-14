import { createFileRoute } from '@tanstack/react-router';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { curriculumApi, type CurriculumResponse, type CurriculumSummary } from '../../lib/api';
import { useState } from 'react';
import { GraduationCap, Sparkles, BookOpen, Target, Clock, ArrowRight, Play, CheckCircle, Music } from 'lucide-react';
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
  const queryClient = useQueryClient();
  const [showCatalog, setShowCatalog] = useState(false);

  const { data: activeCurriculum, isLoading: isLoadingActive, error: activeError } = useQuery({
    queryKey: ['curriculum', 'active'],
    queryFn: curriculumApi.getActiveCurriculum,
  });

  const { data: allCurriculums, isLoading: isLoadingList, error: listError } = useQuery({
    queryKey: ['curriculum', 'list'],
    queryFn: curriculumApi.listCurriculums,
  });

  const activateMutation = useMutation({
    mutationFn: curriculumApi.activateCurriculum,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['curriculum'] });
      setShowCatalog(false); // Close catalog after activation
    },
  });

  // Debug logging
  console.log('📚 Curriculum Page Debug:', {
    activeCurriculum,
    isLoadingActive,
    activeError,
    allCurriculums,
    isLoadingList,
    listError,
    showCatalog,
  });

  if (isLoadingActive || isLoadingList) {
    return <LoadingState />;
  }

  // If user wants to browse catalog or there's no active curriculum, show catalog
  if (showCatalog || !activeCurriculum) {
    return (
      <div className="relative">
        {activeCurriculum && (
          <div className="absolute top-6 right-6 z-10">
            <button
              onClick={() => setShowCatalog(false)}
              className="px-4 py-2 bg-gray-800 text-white font-medium rounded-lg hover:bg-gray-700 transition border border-gray-700"
            >
              ← Back to Dashboard
            </button>
          </div>
        )}
        <CurriculumCatalog
          curriculums={allCurriculums || []}
          onActivate={(id) => activateMutation.mutate(id)}
          isActivating={activateMutation.isPending}
        />
      </div>
    );
  }

  // Show the dashboard with browse button
  return (
    <div className="relative">
      <div className="absolute top-6 right-6 z-10">
        <button
          onClick={() => setShowCatalog(true)}
          className="px-4 py-2 bg-purple-600 text-white font-medium rounded-lg hover:bg-purple-500 transition"
        >
          Browse All Curriculums
        </button>
      </div>
      <DashboardView curriculum={activeCurriculum} />
    </div>
  );
}

function LoadingState() {
  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-purple-500 mx-auto mb-4"></div>
        <p className="text-gray-400 text-lg">Loading your learning path...</p>
      </div>
    </div>
  );
}

interface CurriculumCatalogProps {
  curriculums: CurriculumSummary[];
  onActivate: (id: string) => void;
  isActivating: boolean;
}

function CurriculumCatalog({ curriculums, onActivate, isActivating }: CurriculumCatalogProps) {
  const [showWizard, setShowWizard] = useState(false);

  // Group by "My Curriculums" (clones) vs "Available Paths" (globals)?
  // Since user has none active, list is likely just the 4 globals.
  // We can just display them all nicely.

  const getGradient = (title: string) => {
    if (title.includes('Neo-Soul')) return 'from-amber-600/20 to-pink-600/20 hover:from-amber-600/30 hover:to-pink-600/30 border-amber-600/30';
    if (title.includes('Jazz')) return 'from-blue-600/20 to-indigo-600/20 hover:from-blue-600/30 hover:to-indigo-600/30 border-blue-600/30';
    if (title.includes('Gospel')) return 'from-purple-600/20 to-fuchsia-600/20 hover:from-purple-600/30 hover:to-fuchsia-600/30 border-purple-600/30';
    return 'from-emerald-600/20 to-teal-600/20 hover:from-emerald-600/30 hover:to-teal-600/30 border-emerald-600/30';
  };

  const getIcon = (title: string) => {
    if (title.includes('Neo-Soul')) return <Sparkles className="w-8 h-8 text-amber-400" />;
    if (title.includes('Jazz')) return <Music className="w-8 h-8 text-blue-400" />;
    return <BookOpen className="w-8 h-8 text-purple-400" />;
  };

  return (
    <div className="min-h-screen bg-gray-900 p-6 md:p-12 overflow-y-auto">
      <div className="max-w-6xl mx-auto">

        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-4xl md:text-6xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-blue-400 mb-6">
            Choose Your Learning Path
          </h1>
          <p className="text-xl text-gray-400 max-w-2xl mx-auto">
            Select a world-class curriculum designed by experts, or use AI to generate a completely personalized custom path.
          </p>
        </div>

        {/* Global Curriculums Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-16">
          {curriculums.map((curr) => (
            <div
              key={curr.id}
              className={`relative group rounded-3xl p-8 border backdrop-blur-sm transition-all duration-300 hover:-translate-y-1 hover:shadow-2xl bg-gradient-to-br ${getGradient(curr.title)}`}
            >
              <div className="flex flex-col h-full justify-between">
                <div>
                  <div className="flex items-start justify-between mb-4">
                    <div className="p-3 bg-white/5 rounded-2xl backdrop-blur-md">
                      {getIcon(curr.title)}
                    </div>
                    <span className="px-3 py-1 rounded-full bg-white/5 text-xs text-white/70 font-medium">
                      {curr.duration_weeks} Weeks
                    </span>
                  </div>

                  <h3 className="text-2xl font-bold text-white mb-3 group-hover:text-purple-300 transition-colors">
                    {curr.title}
                  </h3>

                  <p className="text-gray-300 mb-6 text-sm leading-relaxed">
                    {curr.description || "Master the essentials with this comprehensive curriculum."}
                  </p>

                  {/* Features list (mock or extracted) */}
                  <div className="space-y-2 mb-8">
                    <div className="flex items-center gap-2 text-sm text-gray-400">
                      <CheckCircle className="w-4 h-4 text-green-500/50" />
                      <span>Structured Weekly Modules</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm text-gray-400">
                      <CheckCircle className="w-4 h-4 text-green-500/50" />
                      <span>Audio & MIDI Practice Files</span>
                    </div>
                  </div>
                </div>

                <button
                  onClick={() => onActivate(curr.id)}
                  disabled={isActivating}
                  className="w-full py-4 bg-white text-gray-900 font-bold rounded-xl hover:bg-gray-100 transition flex items-center justify-center gap-2 group-hover:shadow-lg hover:scale-[1.02] active:scale-[0.98]"
                >
                  <Play className="w-5 h-5 fill-current" />
                  Start Learning Path
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Divider */}
        <div className="relative flex py-8 items-center mb-12">
          <div className="flex-grow border-t border-gray-800"></div>
          <span className="flex-shrink mx-4 text-gray-500 font-medium text-sm uppercase tracking-widest">OR</span>
          <div className="flex-grow border-t border-gray-800"></div>
        </div>

        {/* AI Generator Option */}
        <div className="bg-gradient-to-r from-purple-900/40 to-indigo-900/40 border border-purple-500/30 rounded-3xl p-8 relative overflow-hidden text-center md:text-left md:flex items-center justify-between gap-8 group">
          <div className="absolute top-0 right-0 p-3 opacity-10 group-hover:opacity-20 transition">
            <Sparkles className="w-64 h-64 text-purple-400" />
          </div>

          <div className="relative z-10 max-w-2xl">
            <div className="flex items-center gap-3 mb-4 justify-center md:justify-start">
              <span className="px-3 py-1 rounded-full bg-purple-500/20 text-purple-300 text-xs font-bold uppercase tracking-wider border border-purple-500/30">
                Experimental
              </span>
              <h3 className="text-3xl font-bold text-white">AI Custom Generator</h3>
            </div>
            <p className="text-gray-300 mb-6 md:mb-0">
              Want something purely unique? Our AI Coach can generate a completely custom curriculum based on your specific prompts, skill profile, and musical influences.
            </p>
          </div>

          <div className="relative z-10">
            <button
              onClick={() => setShowWizard(true)}
              className="whitespace-nowrap px-8 py-4 bg-transparent border-2 border-purple-500 text-purple-100 font-bold rounded-xl hover:bg-purple-500 hover:text-white transition flex items-center justify-center gap-2"
            >
              <Sparkles className="w-5 h-5" />
              Generate Custom Path
            </button>
          </div>
        </div>

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
