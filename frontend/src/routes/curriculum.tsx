import { createFileRoute, Link, Outlet, useLocation } from '@tanstack/react-router';
import { useActiveCurriculum, useCurriculumList } from '../hooks/useCurriculum';
import { PageHeader } from '@/components/ui/page-header';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { SkeletonHeader, SkeletonCard } from '@/components/ui/skeleton';
import { EmptyState } from '@/components/ui/empty-state';
import { BookOpen, Calendar, PlusCircle, TrendingUp, Target, Award } from 'lucide-react';

export const Route = createFileRoute('/curriculum')({
  component: CurriculumLayout,
});

function CurriculumLayout() {
  const location = useLocation();
  const { data: activeCurriculum, isLoading: activeLoading } = useActiveCurriculum();
  const { data: curriculumList, isLoading: listLoading } = useCurriculumList();

  // Check if we're on the /curriculum/new route
  const isCreatingNew = location.pathname === '/curriculum/new';

  if (activeLoading || listLoading) {
    return (
      <div className="px-6 py-8">
        <SkeletonHeader />
        <div className="mt-8">
          <SkeletonCard />
        </div>
      </div>
    );
  }

  const hasNoCurriculum = !activeCurriculum && (!curriculumList || curriculumList.length === 0);

  if (hasNoCurriculum) {
    return (
      <div className="px-6 py-8">
        <PageHeader
          title="My Curriculum"
          description="Personalized music education powered by AI"
        />
        <EmptyState
          icon="🎹"
          title="No curriculum yet"
          description="Create your first personalized curriculum to begin your music learning journey. Choose from templates or generate a custom curriculum with AI."
          action={{
            label: "Create Curriculum",
            href: "/curriculum/new"
          }}
          secondaryAction={{
            label: "Explore Genres",
            href: "/genres"
          }}
          size="lg"
        />
      </div>
    );
  }

  // If creating new curriculum, just render the outlet without the layout
  if (isCreatingNew) {
    return (
      <div className="px-6 py-8">
        <Outlet />
      </div>
    );
  }

  return (
    <div className="px-6 py-8">
      <PageHeader
        title="My Curriculum"
        description="Personalized music education powered by AI"
        actions={
          <Button asChild variant="primary">
            <Link to="/curriculum/new">
              <PlusCircle className="size-4 mr-2" />
              Create New
            </Link>
          </Button>
        }
      />

      {/* Active Curriculum Hero Card */}
      {activeCurriculum && (
        <Card variant="gradient" className="mb-8 overflow-hidden relative">
          <div className="absolute inset-0 bg-gradient-to-r from-purple-600 via-pink-600 to-blue-600 rounded-lg" />
          <div className="relative z-10">
            <CardHeader>
              <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <CardTitle className="text-white text-2xl">
                      {activeCurriculum.title}
                    </CardTitle>
                    <Badge variant="success" className="bg-white/20 text-white border-white/30">
                      Active
                    </Badge>
                  </div>
                  <CardDescription className="text-purple-100 mb-4">
                    {activeCurriculum.description}
                  </CardDescription>

                  {/* Stats Grid */}
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
                    <StatBox
                      icon={<Calendar className="size-5" />}
                      label="Current Week"
                      value={`${activeCurriculum.current_week}/${activeCurriculum.duration_weeks}`}
                    />
                    <StatBox
                      icon={<BookOpen className="size-5" />}
                      label="Modules"
                      value={activeCurriculum.modules.length.toString()}
                    />
                    <StatBox
                      icon={<Target className="size-5" />}
                      label="Progress"
                      value={`${Math.round((activeCurriculum.current_week / activeCurriculum.duration_weeks) * 100)}%`}
                    />
                    <StatBox
                      icon={<Award className="size-5" />}
                      label="Skill Level"
                      value="Intermediate"
                    />
                  </div>
                </div>

                <div className="flex flex-col gap-2">
                  <Button asChild variant="outline" size="lg" className="bg-white text-purple-600 hover:bg-purple-50 border-0">
                    <Link to="/curriculum/$curriculumId" params={{ curriculumId: activeCurriculum.id }}>
                      View Details
                    </Link>
                  </Button>
                  <Button asChild variant="ghost" size="lg" className="text-white hover:bg-white/10">
                    <Link to="/curriculum/daily">
                      <Calendar className="size-4 mr-2" />
                      Daily Practice
                    </Link>
                  </Button>
                </div>
              </div>
            </CardHeader>

            {/* Progress Bar */}
            <CardContent className="pt-0">
              <div className="bg-white/20 rounded-full h-3 overflow-hidden">
                <div
                  className="bg-white h-full rounded-full transition-all duration-500 shadow-lg"
                  style={{
                    width: `${(activeCurriculum.current_week / activeCurriculum.duration_weeks) * 100}%`
                  }}
                />
              </div>
              <p className="text-xs text-white/80 mt-2 text-right">
                Week {activeCurriculum.current_week} of {activeCurriculum.duration_weeks} • Keep it up!
              </p>
            </CardContent>
          </div>
        </Card>
      )}

      {/* Quick Stats Cards */}
      {activeCurriculum && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <QuickStatCard
            icon={<TrendingUp className="size-6 text-green-600" />}
            title="Weekly Streak"
            value="12 days"
            trend="+2 from last week"
            variant="success"
          />
          <QuickStatCard
            icon={<Target className="size-6 text-blue-600" />}
            title="Exercises Completed"
            value="48"
            trend="6 this week"
            variant="info"
          />
          <QuickStatCard
            icon={<Award className="size-6 text-purple-600" />}
            title="Achievements"
            value="7"
            trend="2 recent"
            variant="default"
          />
        </div>
      )}

      {/* Navigation Tabs */}
      <nav className="flex gap-1 mb-6 bg-slate-100 dark:bg-slate-800 p-1 rounded-lg inline-flex">
        <NavTab to="/curriculum" icon={<BookOpen className="size-4" />}>
          Overview
        </NavTab>
        <NavTab to="/curriculum/daily" icon={<Calendar className="size-4" />}>
          Daily Practice
        </NavTab>
        <NavTab to="/curriculum/new" icon={<PlusCircle className="size-4" />}>
          Create New
        </NavTab>
      </nav>

      {/* Outlet for nested routes */}
      <Outlet />
    </div>
  );
}

interface StatBoxProps {
  icon: React.ReactNode;
  label: string;
  value: string;
}

function StatBox({ icon, label, value }: StatBoxProps) {
  return (
    <div className="bg-white/10 backdrop-blur-sm rounded-lg p-3 border border-white/20">
      <div className="flex items-center gap-2 text-white/80 text-xs mb-1">
        {icon}
        <span>{label}</span>
      </div>
      <div className="text-white text-xl font-bold">{value}</div>
    </div>
  );
}

interface QuickStatCardProps {
  icon: React.ReactNode;
  title: string;
  value: string;
  trend: string;
  variant: "success" | "info" | "default";
}

function QuickStatCard({ icon, title, value, trend, variant }: QuickStatCardProps) {
  const variantClasses = {
    success: "border-green-200 bg-green-50 dark:border-green-900 dark:bg-green-950/20",
    info: "border-blue-200 bg-blue-50 dark:border-blue-900 dark:bg-blue-950/20",
    default: "border-purple-200 bg-purple-50 dark:border-purple-900 dark:bg-purple-950/20",
  };

  return (
    <Card variant="elevated" className={variantClasses[variant]}>
      <CardContent className="p-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <p className="text-sm text-slate-600 dark:text-slate-400 mb-1">{title}</p>
            <p className="text-3xl font-bold text-slate-900 dark:text-white mb-1">{value}</p>
            <p className="text-xs text-slate-500 dark:text-slate-500">{trend}</p>
          </div>
          <div className="rounded-full bg-white dark:bg-slate-800 p-3 shadow-sm">
            {icon}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

interface NavTabProps {
  to: string;
  icon: React.ReactNode;
  children: React.ReactNode;
}

function NavTab({ to, icon, children }: NavTabProps) {
  return (
    <Link
      to={to}
      className="flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium text-slate-600 hover:text-slate-900 hover:bg-white/50 transition-colors dark:text-slate-400 dark:hover:text-slate-100 dark:hover:bg-slate-700"
      activeProps={{
        className: "flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium bg-white text-purple-600 shadow-sm dark:bg-slate-700 dark:text-purple-400"
      }}
    >
      {icon}
      <span>{children}</span>
    </Link>
  );
}
