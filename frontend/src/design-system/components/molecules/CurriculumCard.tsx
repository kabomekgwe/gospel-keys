import React from 'react';
import Card from './Card';
import Badge from '../atoms/Badge';
import ProgressBar from '../atoms/ProgressBar';
import Button from '../atoms/Button';

/**
 * CurriculumCard Component - Learning Path Display
 *
 * Displays a curriculum/learning path with progress tracking.
 * Shows duration, lessons count, skill level, and enrollment status.
 */

export interface CurriculumCardProps {
  title: string;
  description: string;
  genre: 'gospel' | 'jazz' | 'blues' | 'neosoul' | 'classical' | 'multi';
  skillLevel: 'beginner' | 'intermediate' | 'advanced' | 'all-levels';
  duration: number; // weeks
  lessonsCount: number;
  enrolled?: boolean;
  progress?: number; // 0-100, only if enrolled
  onEnroll?: () => void;
  onContinue?: () => void;
  onView?: () => void;
  className?: string;
}

const CurriculumCard: React.FC<CurriculumCardProps> = ({
  title,
  description,
  genre,
  skillLevel,
  duration,
  lessonsCount,
  enrolled = false,
  progress = 0,
  onEnroll,
  onContinue,
  onView,
  className = '',
}) => {
  // Genre color mapping
  const genreColors: Record<string, string> = {
    gospel: 'bg-gradient-to-br from-primary-purple-500 to-primary-purple-700',
    jazz: 'bg-gradient-to-br from-status-warning-DEFAULT to-status-warning-dark',
    blues: 'bg-gradient-to-br from-status-info-DEFAULT to-status-info-dark',
    neosoul: 'bg-gradient-to-br from-pink-500 to-orange-500',
    classical: 'bg-gradient-to-br from-indigo-500 to-primary-purple-500',
    multi: 'bg-gradient-to-br from-primary-cyan-500 to-primary-purple-500',
  };

  // Skill level badge variant
  const skillLevelVariant: Record<string, 'success' | 'warning' | 'error' | 'default'> = {
    beginner: 'success',
    intermediate: 'warning',
    advanced: 'error',
    'all-levels': 'default',
  };

  return (
    <Card variant="elevated" padding="none" hover className={className}>
      {/* Hero section with gradient */}
      <div className={`h-32 ${genreColors[genre]} relative overflow-hidden`}>
        <div className="absolute inset-0 bg-black/20" />
        <div className="relative p-6 h-full flex flex-col justify-end">
          <Badge variant="default" size="sm" className="mb-2 w-fit">
            {genre === 'multi' ? 'Multi-Genre' : genre.toUpperCase()}
          </Badge>
          <h3 className="text-xl font-bold text-white">{title}</h3>
        </div>
      </div>

      {/* Content */}
      <div className="p-6">
        <p className="text-text-secondary text-sm mb-4 line-clamp-3">{description}</p>

        {/* Metadata */}
        <div className="flex flex-wrap gap-2 mb-4">
          <Badge variant={skillLevelVariant[skillLevel]} size="sm" outlined>
            {skillLevel.split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
          </Badge>
          <Badge variant="default" size="sm" outlined>
            {duration} {duration === 1 ? 'week' : 'weeks'}
          </Badge>
          <Badge variant="default" size="sm" outlined>
            {lessonsCount} {lessonsCount === 1 ? 'lesson' : 'lessons'}
          </Badge>
        </div>

        {/* Progress (if enrolled) */}
        {enrolled && (
          <div className="mb-4">
            <ProgressBar
              value={progress}
              variant="primary"
              size="md"
              showLabel
              label={`Progress: ${Math.round(progress)}%`}
            />
          </div>
        )}

        {/* Actions */}
        <div className="flex gap-2">
          {enrolled ? (
            <>
              <Button variant="primary" size="md" fullWidth onClick={onContinue}>
                Continue Learning
              </Button>
              <Button variant="ghost" size="md" onClick={onView}>
                View
              </Button>
            </>
          ) : (
            <>
              <Button variant="primary" size="md" fullWidth onClick={onEnroll}>
                Enroll Now
              </Button>
              <Button variant="ghost" size="md" onClick={onView}>
                Preview
              </Button>
            </>
          )}
        </div>
      </div>
    </Card>
  );
};

export default CurriculumCard;
