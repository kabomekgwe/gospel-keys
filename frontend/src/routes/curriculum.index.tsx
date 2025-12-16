import { createFileRoute, Link } from '@tanstack/react-router';
import { useCurriculumList } from '../hooks/useCurriculum';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { SkeletonCurriculumCard } from '@/components/ui/skeleton';
import { EmptyState } from '@/components/ui/empty-state';
import { Clock, BookOpen, TrendingUp, Play } from 'lucide-react';

export const Route = createFileRoute('/curriculum/')({
  component: CurriculumOverview,
});

function CurriculumOverview() {
  const { data: curriculumList, isLoading } = useCurriculumList();

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <SkeletonCurriculumCard />
        <SkeletonCurriculumCard />
        <SkeletonCurriculumCard />
      </div>
    );
  }

  if (!curriculumList?.length) {
    return (
      <EmptyState
        icon="📚"
        title="No curriculums found"
        description="You haven't created any curriculums yet. Start your learning journey by creating your first curriculum."
        action={{
          label: "Create Curriculum",
          href: "/curriculum/new"
        }}
        secondaryAction={{
          label: "Explore Genres",
          href: "/genres"
        }}
      />
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 dark:text-white">
            All Curriculums
          </h2>
          <p className="text-sm text-slate-600 dark:text-slate-400">
            {curriculumList.length} {curriculumList.length === 1 ? 'curriculum' : 'curriculums'} total
          </p>
        </div>
        <Button asChild variant="outline">
          <Link to="/curriculum/new">Create New</Link>
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {curriculumList.map((curriculum) => (
          <CurriculumCard key={curriculum.id} curriculum={curriculum} />
        ))}
      </div>
    </div>
  );
}

interface CurriculumCardProps {
  curriculum: any;
}

function CurriculumCard({ curriculum }: CurriculumCardProps) {
  const progressPercentage = Math.round(curriculum.overall_progress || 0);
  const isActive = curriculum.status === 'active';
  const isCompleted = curriculum.status === 'completed';

  return (
    <Card
      variant={isActive ? "interactive" : "default"}
      className="h-full flex flex-col hover:shadow-xl transition-all duration-300 group"
    >
      <CardHeader>
        <div className="flex items-start justify-between mb-2">
          <CardTitle as="h3" className="text-lg group-hover:text-purple-600 transition-colors">
            {curriculum.title}
          </CardTitle>
          <Badge variant={
            isActive ? "active" :
            isCompleted ? "completed" :
            "draft"
          }>
            {curriculum.status}
          </Badge>
        </div>
        <CardDescription className="line-clamp-2 min-h-[2.5rem]">
          {curriculum.description}
        </CardDescription>
      </CardHeader>

      <CardContent className="flex-1">
        {/* Stats Grid */}
        <div className="grid grid-cols-2 gap-3 mb-4">
          <StatItem
            icon={<Clock className="size-4" />}
            label="Week"
            value={`${curriculum.current_week}/${curriculum.duration_weeks}`}
          />
          <StatItem
            icon={<BookOpen className="size-4" />}
            label="Modules"
            value={curriculum.module_count}
          />
        </div>

        {/* Progress Section */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-600 dark:text-slate-400 flex items-center gap-1">
              <TrendingUp className="size-3" />
              Progress
            </span>
            <span className="font-semibold text-slate-900 dark:text-white">
              {progressPercentage}%
            </span>
          </div>
          <div className="relative w-full bg-slate-200 dark:bg-slate-700 rounded-full h-2 overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-500 ${
                isCompleted
                  ? 'bg-gradient-to-r from-green-500 to-emerald-500'
                  : 'bg-gradient-to-r from-purple-500 to-pink-500'
              }`}
              style={{ width: `${progressPercentage}%` }}
            />
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-500">
            {isCompleted
              ? 'Completed! Well done!'
              : `${100 - progressPercentage}% remaining`}
          </p>
        </div>
      </CardContent>

      <CardFooter className="pt-0">
        <Button asChild variant={isActive ? "primary" : "outline"} className="w-full group-hover:scale-105 transition-transform">
          <Link to="/curriculum/$curriculumId" params={{ curriculumId: curriculum.id }}>
            <Play className="size-4 mr-2" />
            {isActive ? 'Continue Learning' : 'View Details'}
          </Link>
        </Button>
      </CardFooter>
    </Card>
  );
}

interface StatItemProps {
  icon: React.ReactNode;
  label: string;
  value: string | number;
}

function StatItem({ icon, label, value }: StatItemProps) {
  return (
    <div className="flex items-center gap-2 p-2 rounded-lg bg-slate-50 dark:bg-slate-800/50">
      <div className="text-purple-600 dark:text-purple-400">
        {icon}
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-xs text-slate-500 dark:text-slate-400">{label}</p>
        <p className="text-sm font-semibold text-slate-900 dark:text-white truncate">
          {value}
        </p>
      </div>
    </div>
  );
}
