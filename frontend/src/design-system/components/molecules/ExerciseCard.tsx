import React from 'react';
import Card from './Card';
import Badge from '../atoms/Badge';
import ProgressCircle from '../atoms/ProgressCircle';
import Button from '../atoms/Button';

/**
 * ExerciseCard Component - Music Exercise Display
 *
 * Specialized card for displaying practice exercises.
 * Shows exercise metadata, difficulty, progress, and actions.
 */

export interface ExerciseCardProps {
  title: string;
  description: string;
  genre: 'gospel' | 'jazz' | 'blues' | 'neosoul' | 'classical';
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  duration: number; // minutes
  progress?: number; // 0-100
  completed?: boolean;
  bpm?: number;
  onStart?: () => void;
  onContinue?: () => void;
  className?: string;
}

const ExerciseCard: React.FC<ExerciseCardProps> = ({
  title,
  description,
  genre,
  difficulty,
  duration,
  progress = 0,
  completed = false,
  bpm,
  onStart,
  onContinue,
  className = '',
}) => {
  // Genre color mapping
  const genreColors: Record<string, { badge: string; gradient: string }> = {
    gospel: { badge: 'secondary', gradient: 'from-primary-purple-500 to-primary-purple-700' },
    jazz: { badge: 'warning', gradient: 'from-status-warning-DEFAULT to-status-warning-dark' },
    blues: { badge: 'info', gradient: 'from-status-info-DEFAULT to-status-info-dark' },
    neosoul: { badge: 'error', gradient: 'from-pink-500 to-orange-500' },
    classical: { badge: 'primary', gradient: 'from-indigo-500 to-primary-purple-500' },
  };

  // Difficulty color mapping
  const difficultyVariant: Record<string, 'success' | 'warning' | 'error'> = {
    beginner: 'success',
    intermediate: 'warning',
    advanced: 'error',
  };

  const genreColor = genreColors[genre] || genreColors.gospel;

  return (
    <Card
      variant="elevated"
      padding="md"
      hover
      interactive={!completed}
      onClick={completed ? undefined : (onContinue || onStart)}
      className={className}
    >
      {/* Header with genre gradient */}
      <div className={`-mt-6 -mx-6 mb-4 p-4 bg-gradient-to-r ${genreColor.gradient}`}>
        <div className="flex items-start justify-between">
          <div>
            <Badge variant={genreColor.badge as any} size="sm" className="mb-2">
              {genre.toUpperCase()}
            </Badge>
            <h3 className="text-lg font-bold text-white">{title}</h3>
          </div>
          <ProgressCircle
            value={progress}
            size="sm"
            variant={completed ? 'success' : 'primary'}
          />
        </div>
      </div>

      {/* Description */}
      <p className="text-text-secondary text-sm mb-4 line-clamp-2">{description}</p>

      {/* Metadata */}
      <div className="flex flex-wrap gap-2 mb-4">
        <Badge variant={difficultyVariant[difficulty]} size="sm" outlined>
          {difficulty.charAt(0).toUpperCase() + difficulty.slice(1)}
        </Badge>
        <Badge variant="default" size="sm" outlined>
          {duration} min
        </Badge>
        {bpm && (
          <Badge variant="default" size="sm" outlined>
            {bpm} BPM
          </Badge>
        )}
      </div>

      {/* Actions */}
      <div className="flex gap-2">
        {completed ? (
          <Button variant="success" size="sm" fullWidth>
            ✓ Completed
          </Button>
        ) : progress > 0 ? (
          <Button variant="primary" size="sm" fullWidth onClick={onContinue}>
            Continue ({Math.round(progress)}%)
          </Button>
        ) : (
          <Button variant="primary" size="sm" fullWidth onClick={onStart}>
            Start Exercise
          </Button>
        )}
      </div>
    </Card>
  );
};

export default ExerciseCard;
