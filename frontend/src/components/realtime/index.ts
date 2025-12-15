/**
 * Real-time Performance Monitoring & Progress Tracking Components
 * STORY-3.3: Frontend Visualization & Integration
 *
 * This module exports all real-time analysis and progress tracking components.
 *
 * Real-Time Monitoring Components (use with PerformanceMonitor):
 * - PitchVisualization: Real-time pitch accuracy with cents deviation
 * - RhythmGrid: Onset timing with metronome alignment
 * - DynamicsMeter: Velocity and dynamics tracking
 * - FeedbackPanel: AI-powered performance suggestions
 * - PerformanceMonitor: Parent component combining all real-time visualizations
 *
 * Progress Tracking Components (use with ProgressDashboard):
 * - PracticeHistory: Session timeline with expandable details
 * - AccuracyTrends: Line chart showing improvement over time
 * - SkillLevelChart: Radar chart for skill dimensions
 * - GoalTracking: Weekly goals and achievement badges
 * - ProgressDashboard: Parent component with tabbed navigation
 *
 * Usage Example:
 *
 * ```tsx
 * import { PerformanceMonitor, ProgressDashboard } from './components/realtime';
 *
 * function App() {
 *   return (
 *     <>
 *       {/* Real-time practice session *\/}
 *       <PerformanceMonitor
 *         userId={1}
 *         pieceName="Moonlight Sonata"
 *         genre="Classical"
 *         targetTempo={120}
 *         difficultyLevel="advanced"
 *         theme="dark"
 *       />
 *
 *       {/* Progress overview *\/}
 *       <ProgressDashboard
 *         userId={1}
 *         theme="dark"
 *         defaultView="overview"
 *       />
 *     </>
 *   );
 * }
 * ```
 */

// Real-Time Monitoring Components
export { PitchVisualization } from './PitchVisualization';
export type { PitchVisualizationProps } from './PitchVisualization';

export { RhythmGrid } from './RhythmGrid';
export type { RhythmGridProps } from './RhythmGrid';

export { DynamicsMeter } from './DynamicsMeter';
export type { DynamicsMeterProps } from './DynamicsMeter';

export { FeedbackPanel } from './FeedbackPanel';
export type { FeedbackPanelProps } from './FeedbackPanel';

export { PerformanceMonitor } from './PerformanceMonitor';
export type { PerformanceMonitorProps } from './PerformanceMonitor';

// Progress Tracking Components
export { PracticeHistory } from './PracticeHistory';
export type { PracticeHistoryProps } from './PracticeHistory';

export { AccuracyTrends } from './AccuracyTrends';
export type { AccuracyTrendsProps } from './AccuracyTrends';

export { SkillLevelChart } from './SkillLevelChart';
export type { SkillLevelChartProps } from './SkillLevelChart';

export { GoalTracking } from './GoalTracking';
export type { GoalTrackingProps } from './GoalTracking';

export { ProgressDashboard } from './ProgressDashboard';
export type { ProgressDashboardProps } from './ProgressDashboard';
