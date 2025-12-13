/**
 * Tutorial Viewer Component
 *
 * Displays comprehensive AI-generated tutorials for curriculum lessons
 * with collapsible sections, progress tracking, and practice integration
 */

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { ChevronDown, ChevronUp, BookOpen, Printer, Bookmark, CheckCircle2 } from 'lucide-react';

interface TutorialViewerProps {
  lessonId: string;
  lessonTitle: string;
  onPracticeExercise?: (exerciseId: string) => void;
}

interface TutorialSection {
  id: string;
  title: string;
  icon: string;
  content: any;
}

export function TutorialViewer({ lessonId, lessonTitle, onPracticeExercise }: TutorialViewerProps) {
  const [tutorial, setTutorial] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['overview']));
  const [readSections, setReadSections] = useState<Set<string>>(new Set());
  const [bookmarkedSections, setBookmarkedSections] = useState<Set<string>>(new Set());
  const [isPrintView, setIsPrintView] = useState(false);

  useEffect(() => {
    loadTutorial();
  }, [lessonId]);

  const loadTutorial = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const data = await api.getLessonTutorial(lessonId);
      setTutorial(data);
      setIsLoading(false);
    } catch (err) {
      setError('Failed to load tutorial');
      setIsLoading(false);
    }
  };

  const toggleSection = (sectionId: string) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(sectionId)) {
      newExpanded.delete(sectionId);
    } else {
      newExpanded.add(sectionId);
      // Mark as read when opened
      setReadSections(prev => new Set(prev).add(sectionId));
    }
    setExpandedSections(newExpanded);
  };

  const toggleBookmark = (sectionId: string) => {
    const newBookmarks = new Set(bookmarkedSections);
    if (newBookmarks.has(sectionId)) {
      newBookmarks.delete(sectionId);
    } else {
      newBookmarks.add(sectionId);
    }
    setBookmarkedSections(newBookmarks);
  };

  const expandAll = () => {
    const allSectionIds = sections.map(s => s.id);
    setExpandedSections(new Set(allSectionIds));
    setReadSections(new Set(allSectionIds));
  };

  const collapseAll = () => {
    setExpandedSections(new Set());
  };

  const handlePrint = () => {
    setIsPrintView(true);
    setTimeout(() => {
      window.print();
      setIsPrintView(false);
    }, 100);
  };

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow p-8 text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-gray-600">Loading tutorial...</p>
      </div>
    );
  }

  if (error || !tutorial) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800">
        {error || 'Tutorial not available'}
      </div>
    );
  }

  const sections: TutorialSection[] = [
    {
      id: 'overview',
      title: 'Overview',
      icon: '📚',
      content: tutorial.overview,
    },
    {
      id: 'theory',
      title: 'Theory',
      icon: '🎓',
      content: tutorial.theory,
    },
    {
      id: 'demonstration',
      title: 'Demonstration',
      icon: '🎹',
      content: tutorial.demonstration,
    },
    {
      id: 'practice_guide',
      title: 'Practice Guide',
      icon: '📝',
      content: tutorial.practice_guide,
    },
    {
      id: 'tips_and_tricks',
      title: 'Tips & Tricks',
      icon: '💡',
      content: tutorial.tips_and_tricks,
    },
    {
      id: 'common_mistakes',
      title: 'Common Mistakes',
      icon: '⚠️',
      content: tutorial.common_mistakes,
    },
    {
      id: 'next_steps',
      title: 'Next Steps',
      icon: '🎯',
      content: tutorial.next_steps,
    },
  ].filter(section => section.content);

  const progressPercentage = (readSections.size / sections.length) * 100;

  return (
    <div className={`bg-white rounded-lg shadow ${isPrintView ? 'print:shadow-none' : ''}`}>
      {/* Header */}
      <div className={`border-b border-gray-200 p-6 ${isPrintView ? 'print:border-b print:p-4' : ''}`}>
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <BookOpen className="w-6 h-6 text-blue-600" />
              <h2 className="text-2xl font-bold text-gray-900">{lessonTitle}</h2>
            </div>
            <p className="text-sm text-gray-600">
              Comprehensive Tutorial - {tutorial.overview?.duration_minutes || 'N/A'} minutes
            </p>
          </div>

          {/* Action Buttons */}
          <div className={`flex gap-2 ${isPrintView ? 'print:hidden' : ''}`}>
            <button
              onClick={expandAll}
              className="px-3 py-2 text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 rounded"
            >
              Expand All
            </button>
            <button
              onClick={collapseAll}
              className="px-3 py-2 text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 rounded"
            >
              Collapse All
            </button>
            <button
              onClick={handlePrint}
              className="px-3 py-2 text-sm bg-blue-100 hover:bg-blue-200 text-blue-700 rounded flex items-center gap-1"
            >
              <Printer className="w-4 h-4" />
              Print
            </button>
          </div>
        </div>

        {/* Progress Bar */}
        <div className={`${isPrintView ? 'print:hidden' : ''}`}>
          <div className="flex items-center justify-between text-sm text-gray-600 mb-2">
            <span>Progress: {readSections.size} / {sections.length} sections read</span>
            <span>{Math.round(progressPercentage)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progressPercentage}%` }}
            />
          </div>
        </div>
      </div>

      {/* Sections */}
      <div className="divide-y divide-gray-200">
        {sections.map((section) => {
          const isExpanded = isPrintView || expandedSections.has(section.id);
          const isRead = readSections.has(section.id);
          const isBookmarked = bookmarkedSections.has(section.id);

          return (
            <div key={section.id} className={`${isPrintView ? 'print:break-inside-avoid' : ''}`}>
              {/* Section Header */}
              <button
                onClick={() => toggleSection(section.id)}
                className={`w-full px-6 py-4 flex items-center justify-between hover:bg-gray-50 transition-colors ${isPrintView ? 'print:hidden' : ''}`}
              >
                <div className="flex items-center gap-3">
                  <span className="text-2xl">{section.icon}</span>
                  <h3 className="text-lg font-semibold text-gray-900">{section.title}</h3>
                  {isRead && <CheckCircle2 className="w-5 h-5 text-green-600" />}
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      toggleBookmark(section.id);
                    }}
                    className={`p-1 rounded ${isBookmarked ? 'text-yellow-500' : 'text-gray-400 hover:text-yellow-500'}`}
                  >
                    <Bookmark className={`w-5 h-5 ${isBookmarked ? 'fill-current' : ''}`} />
                  </button>
                  {isExpanded ? (
                    <ChevronUp className="w-5 h-5 text-gray-400" />
                  ) : (
                    <ChevronDown className="w-5 h-5 text-gray-400" />
                  )}
                </div>
              </button>

              {/* Print View Header */}
              {isPrintView && (
                <div className="px-6 py-3 bg-gray-50 print:bg-transparent border-b print:border-b">
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">{section.icon}</span>
                    <h3 className="text-lg font-semibold text-gray-900">{section.title}</h3>
                  </div>
                </div>
              )}

              {/* Section Content */}
              {isExpanded && (
                <div className="px-6 py-4 bg-gray-50 print:bg-white">
                  {renderSectionContent(section.id, section.content, onPracticeExercise, isPrintView)}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Footer */}
      {!isPrintView && (
        <div className="border-t border-gray-200 p-6 bg-gray-50">
          <div className="flex items-center justify-between">
            <p className="text-sm text-gray-600">
              {readSections.size === sections.length
                ? '✅ Tutorial completed! Ready to practice.'
                : `${sections.length - readSections.size} section(s) remaining`}
            </p>
            {bookmarkedSections.size > 0 && (
              <p className="text-sm text-gray-600">
                {bookmarkedSections.size} bookmarked section(s)
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

// Helper function to render section content
function renderSectionContent(
  sectionId: string,
  content: any,
  onPracticeExercise?: (exerciseId: string) => void,
  isPrintView: boolean = false
): JSX.Element {
  if (!content) return <p className="text-gray-500 italic">Content not available</p>;

  switch (sectionId) {
    case 'overview':
      return (
        <div className="space-y-4">
          {content.what_you_will_learn && (
            <div>
              <h4 className="font-semibold text-gray-900 mb-2">What You'll Learn:</h4>
              <ul className="list-disc list-inside space-y-1 text-gray-700">
                {content.what_you_will_learn.map((item: string, i: number) => (
                  <li key={i}>{item}</li>
                ))}
              </ul>
            </div>
          )}
          {content.learning_outcomes && (
            <div>
              <h4 className="font-semibold text-gray-900 mb-2">Learning Outcomes:</h4>
              <ul className="list-disc list-inside space-y-1 text-gray-700">
                {content.learning_outcomes.map((item: string, i: number) => (
                  <li key={i}>{item}</li>
                ))}
              </ul>
            </div>
          )}
          <div className="flex gap-4 text-sm text-gray-600">
            {content.duration_minutes && <span>⏱️ {content.duration_minutes} minutes</span>}
            {content.difficulty && <span>📊 {content.difficulty}</span>}
          </div>
        </div>
      );

    case 'theory':
      return (
        <div className="space-y-4">
          {content.summary && <p className="text-gray-700">{content.summary}</p>}
          {content.key_points && (
            <div>
              <h4 className="font-semibold text-gray-900 mb-2">Key Points:</h4>
              <ul className="list-disc list-inside space-y-1 text-gray-700">
                {content.key_points.map((point: string, i: number) => (
                  <li key={i}>{point}</li>
                ))}
              </ul>
            </div>
          )}
          {content.examples && (
            <div>
              <h4 className="font-semibold text-gray-900 mb-2">Examples:</h4>
              <div className="space-y-2">
                {content.examples.map((example: any, i: number) => (
                  <div key={i} className="bg-white p-3 rounded border border-gray-200">
                    {typeof example === 'string' ? (
                      <p className="text-gray-700">{example}</p>
                    ) : (
                      <>
                        {example.title && <p className="font-medium text-gray-900">{example.title}</p>}
                        {example.description && <p className="text-gray-700 text-sm">{example.description}</p>}
                      </>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      );

    case 'demonstration':
      return (
        <div className="space-y-4">
          {content.description && <p className="text-gray-700">{content.description}</p>}
          {content.example_progressions && (
            <div>
              <h4 className="font-semibold text-gray-900 mb-2">Example Progressions:</h4>
              <div className="space-y-2">
                {content.example_progressions.map((prog: string, i: number) => (
                  <div key={i} className="bg-blue-50 px-4 py-2 rounded text-blue-900 font-mono text-sm">
                    {prog}
                  </div>
                ))}
              </div>
            </div>
          )}
          {content.reference_exercises && onPracticeExercise && (
            <div>
              <h4 className="font-semibold text-gray-900 mb-2">Practice Exercises:</h4>
              <div className="space-y-2">
                {content.reference_exercises.map((exerciseId: string, i: number) => (
                  <button
                    key={i}
                    onClick={() => onPracticeExercise(exerciseId)}
                    className={`w-full text-left px-4 py-3 bg-white border border-blue-300 rounded hover:bg-blue-50 transition-colors ${isPrintView ? 'print:hidden' : ''}`}
                  >
                    <span className="text-blue-600 font-medium">Practice Exercise {i + 1}</span>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      );

    case 'practice_guide':
      return (
        <div className="space-y-4">
          {content.warm_up && (
            <div>
              <h4 className="font-semibold text-gray-900 mb-2">Warm-up:</h4>
              <ul className="list-disc list-inside space-y-1 text-gray-700">
                {content.warm_up.map((item: string, i: number) => (
                  <li key={i}>{item}</li>
                ))}
              </ul>
            </div>
          )}
          {content.steps && (
            <div>
              <h4 className="font-semibold text-gray-900 mb-3">Practice Steps:</h4>
              <div className="space-y-3">
                {content.steps.map((step: any, i: number) => (
                  <div key={i} className="bg-white p-4 rounded border border-gray-200">
                    <div className="flex items-start gap-3">
                      <div className="flex-shrink-0 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold">
                        {step.step || i + 1}
                      </div>
                      <div className="flex-1">
                        {step.title && <h5 className="font-semibold text-gray-900 mb-1">{step.title}</h5>}
                        <p className="text-gray-700 mb-2">{step.instruction}</p>
                        {step.duration_minutes && (
                          <p className="text-sm text-gray-600">⏱️ {step.duration_minutes} minutes</p>
                        )}
                        {step.success_criteria && (
                          <p className="text-sm text-green-700 mt-2">✓ Success: {step.success_criteria}</p>
                        )}
                        {step.common_challenges && (
                          <p className="text-sm text-yellow-700 mt-1">⚠️ Challenge: {step.common_challenges}</p>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
          {content.cool_down && (
            <div>
              <h4 className="font-semibold text-gray-900 mb-2">Cool-down:</h4>
              <ul className="list-disc list-inside space-y-1 text-gray-700">
                {content.cool_down.map((item: string, i: number) => (
                  <li key={i}>{item}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      );

    case 'tips_and_tricks':
      return (
        <div className="space-y-3">
          {Array.isArray(content) ? (
            content.map((tip: any, i: number) => (
              <div key={i} className="bg-yellow-50 border-l-4 border-yellow-400 p-4">
                {tip.category && <span className="text-xs font-semibold text-yellow-800 uppercase">{tip.category}</span>}
                <p className="text-gray-700 mt-1">{tip.tip || tip}</p>
              </div>
            ))
          ) : (
            <p className="text-gray-700">{JSON.stringify(content)}</p>
          )}
        </div>
      );

    case 'common_mistakes':
      return (
        <div className="space-y-3">
          {Array.isArray(content) ? (
            content.map((mistake: any, i: number) => (
              <div key={i} className="bg-red-50 border-l-4 border-red-400 p-4">
                <p className="text-gray-900 font-medium mb-1">❌ {mistake.mistake}</p>
                <p className="text-gray-700 text-sm">✅ Fix: {mistake.fix}</p>
              </div>
            ))
          ) : (
            <p className="text-gray-700">{JSON.stringify(content)}</p>
          )}
        </div>
      );

    case 'next_steps':
      return (
        <div className="space-y-4">
          {content.preview && (
            <div>
              <h4 className="font-semibold text-gray-900 mb-2">What's Next:</h4>
              <p className="text-gray-700">{content.preview}</p>
            </div>
          )}
          {content.optional_practice && (
            <div>
              <h4 className="font-semibold text-gray-900 mb-2">Optional Practice:</h4>
              <ul className="list-disc list-inside space-y-1 text-gray-700">
                {content.optional_practice.map((item: string, i: number) => (
                  <li key={i}>{item}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      );

    default:
      return <pre className="text-sm text-gray-700 whitespace-pre-wrap">{JSON.stringify(content, null, 2)}</pre>;
  }
}
