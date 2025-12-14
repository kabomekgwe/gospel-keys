/**
 * Assessment Interface Page
 *
 * Comprehensive assessment interface for diagnostic, milestone, and final assessments
 * with section navigation, question display, and results with feedback
 */

import { useState, useEffect } from 'react';
import { createFileRoute, useNavigate } from '@tanstack/react-router';
import { api } from '@/lib/api';
import {
  CheckCircle2,
  Circle,
  Clock,
  ArrowRight,
  ArrowLeft,
  Send,
  Award,
  TrendingUp,
  AlertCircle,
  BookOpen,
} from 'lucide-react';

export const Route = createFileRoute('/curriculum/assessment')({
  component: AssessmentInterface,
});

interface AssessmentQuestion {
  id: string;
  question: string;
  type: 'multiple_choice' | 'true_false' | 'short_answer';
  options?: string[];
  points: number;
}

interface AssessmentExercise {
  id: string;
  type: string;
  instruction: string;
  evaluation_criteria: string[];
  points: number;
}

interface AssessmentSection {
  section_id: string;
  title: string;
  weight: number;
  exercises?: AssessmentExercise[];
  questions?: AssessmentQuestion[];
}

interface Assessment {
  id: string;
  assessment_type: string;
  content: {
    title: string;
    duration_minutes: number;
    sections: AssessmentSection[];
  };
  created_at: string;
}

interface AssessmentResults {
  assessment_id: string;
  scores: Record<string, number>;
  overall_score: number;
  feedback: {
    strengths: string[];
    areas_for_improvement: string[];
    recommended_focus: string[];
  };
}

type ViewMode = 'taking' | 'results';

function AssessmentInterface() {
  const navigate = useNavigate();
  const [assessment, setAssessment] = useState<Assessment | null>(null);
  const [currentSectionIndex, setCurrentSectionIndex] = useState(0);
  const [currentItemIndex, setCurrentItemIndex] = useState(0);
  const [responses, setResponses] = useState<Record<string, any>>({});
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<ViewMode>('taking');
  const [results, setResults] = useState<AssessmentResults | null>(null);
  const [timeRemaining, setTimeRemaining] = useState<number | null>(null);

  useEffect(() => {
    loadCurrentAssessment();
  }, []);

  // Timer effect
  useEffect(() => {
    if (viewMode === 'taking' && timeRemaining !== null && timeRemaining > 0) {
      const interval = setInterval(() => {
        setTimeRemaining((prev) => (prev !== null && prev > 0 ? prev - 1 : 0));
      }, 1000);
      return () => clearInterval(interval);
    }
  }, [viewMode, timeRemaining]);

  // Auto-save responses
  useEffect(() => {
    const timer = setTimeout(() => {
      if (Object.keys(responses).length > 0) {
        localStorage.setItem('assessment_responses', JSON.stringify(responses));
      }
    }, 1000);
    return () => clearTimeout(timer);
  }, [responses]);

  const loadCurrentAssessment = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const data = await api.getCurrentAssessment();
      setAssessment(data);

      // Initialize timer if duration is specified
      if (data.content.duration_minutes) {
        setTimeRemaining(data.content.duration_minutes * 60);
      }

      // Load saved responses if any
      const saved = localStorage.getItem('assessment_responses');
      if (saved) {
        setResponses(JSON.parse(saved));
      }

      setIsLoading(false);
    } catch (err) {
      setError('No active assessment available');
      setIsLoading(false);
    }
  };

  const handleSubmitAssessment = async () => {
    if (!assessment) return;

    setIsSubmitting(true);

    try {
      const evaluationResults = await api.submitAssessmentResponses(assessment.id, responses);
      setResults(evaluationResults);
      setViewMode('results');
      localStorage.removeItem('assessment_responses');
      setIsSubmitting(false);
    } catch (err) {
      setError('Failed to submit assessment');
      setIsSubmitting(false);
    }
  };

  const handleResponseChange = (itemId: string, value: any) => {
    setResponses((prev) => ({
      ...prev,
      [itemId]: value,
    }));
  };

  const getCurrentSection = () => {
    if (!assessment) return null;
    return assessment.content.sections[currentSectionIndex];
  };

  const getCurrentItem = () => {
    const section = getCurrentSection();
    if (!section) return null;

    const allItems = [
      ...(section.exercises || []).map((e) => ({ ...e, itemType: 'exercise' as const })),
      ...(section.questions || []).map((q) => ({ ...q, itemType: 'question' as const })),
    ];

    return allItems[currentItemIndex] || null;
  };

  const getTotalItems = () => {
    const section = getCurrentSection();
    if (!section) return 0;
    return (section.exercises?.length || 0) + (section.questions?.length || 0);
  };

  const goToNextItem = () => {
    const totalItems = getTotalItems();
    if (currentItemIndex < totalItems - 1) {
      setCurrentItemIndex(currentItemIndex + 1);
    } else if (currentSectionIndex < (assessment?.content.sections.length || 0) - 1) {
      setCurrentSectionIndex(currentSectionIndex + 1);
      setCurrentItemIndex(0);
    }
  };

  const goToPreviousItem = () => {
    if (currentItemIndex > 0) {
      setCurrentItemIndex(currentItemIndex - 1);
    } else if (currentSectionIndex > 0) {
      setCurrentSectionIndex(currentSectionIndex - 1);
      const prevSection = assessment?.content.sections[currentSectionIndex - 1];
      const prevTotalItems =
        (prevSection?.exercises?.length || 0) + (prevSection?.questions?.length || 0);
      setCurrentItemIndex(prevTotalItems - 1);
    }
  };

  const isLastItem = () => {
    if (!assessment) return false;
    const isLastSection = currentSectionIndex === assessment.content.sections.length - 1;
    const isLastItemInSection = currentItemIndex === getTotalItems() - 1;
    return isLastSection && isLastItemInSection;
  };

  const getCompletionPercentage = () => {
    if (!assessment) return 0;
    const totalQuestions = assessment.content.sections.reduce(
      (sum, section) =>
        sum + (section.exercises?.length || 0) + (section.questions?.length || 0),
      0
    );
    const answeredQuestions = Object.keys(responses).length;
    return totalQuestions > 0 ? (answeredQuestions / totalQuestions) * 100 : 0;
  };

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow p-8 text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading assessment...</p>
        </div>
      </div>
    );
  }

  if (error || !assessment) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
          <div className="flex items-center gap-3 mb-4">
            <AlertCircle className="w-6 h-6 text-yellow-600" />
            <h2 className="text-lg font-semibold text-gray-900">No Active Assessment</h2>
          </div>
          <p className="text-gray-700 mb-4">
            You don't have any active assessments at the moment. Assessments are automatically
            generated at key milestones in your curriculum.
          </p>
          <button
            onClick={() => navigate({ to: '/curriculum/daily' })}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg"
          >
            Return to Practice
          </button>
        </div>
      </div>
    );
  }

  // Results View
  if (viewMode === 'results' && results) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          {/* Results Header */}
          <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg shadow-lg p-8 text-white mb-8">
            <div className="flex items-center gap-3 mb-4">
              <Award className="w-12 h-12" />
              <div>
                <h1 className="text-3xl font-bold">Assessment Complete!</h1>
                <p className="text-blue-100">Great job completing the assessment</p>
              </div>
            </div>
            <div className="bg-white/20 rounded-lg p-6 mt-6">
              <div className="text-center">
                <p className="text-sm uppercase tracking-wide mb-2">Overall Score</p>
                <p className="text-6xl font-bold">{results.overall_score.toFixed(1)}</p>
                <p className="text-sm mt-2">out of 10.0</p>
              </div>
            </div>
          </div>

          {/* Skill Scores */}
          <div className="bg-white rounded-lg shadow mb-6">
            <div className="border-b border-gray-200 px-6 py-4">
              <h2 className="text-xl font-bold text-gray-900">Skill Breakdown</h2>
            </div>
            <div className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {Object.entries(results.scores).map(([skill, score]) => (
                  <div key={skill} className="bg-gray-50 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="font-semibold text-gray-900 capitalize">
                        {skill.replace(/_/g, ' ')}
                      </h3>
                      <span className="text-2xl font-bold text-blue-600">{score.toFixed(1)}</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full ${
                          score >= 8
                            ? 'bg-green-600'
                            : score >= 6
                            ? 'bg-blue-600'
                            : score >= 4
                            ? 'bg-yellow-600'
                            : 'bg-red-600'
                        }`}
                        style={{ width: `${(score / 10) * 100}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Feedback */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            {/* Strengths */}
            <div className="bg-white rounded-lg shadow">
              <div className="border-b border-gray-200 px-6 py-4">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-5 h-5 text-green-600" />
                  <h2 className="text-lg font-bold text-gray-900">Strengths</h2>
                </div>
              </div>
              <div className="p-6">
                <ul className="space-y-2">
                  {results.feedback.strengths.map((strength, index) => (
                    <li key={index} className="flex items-start gap-2">
                      <CheckCircle2 className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                      <span className="text-gray-700">{strength}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Areas for Improvement */}
            <div className="bg-white rounded-lg shadow">
              <div className="border-b border-gray-200 px-6 py-4">
                <div className="flex items-center gap-2">
                  <TrendingUp className="w-5 h-5 text-orange-600" />
                  <h2 className="text-lg font-bold text-gray-900">Areas to Improve</h2>
                </div>
              </div>
              <div className="p-6">
                <ul className="space-y-2">
                  {results.feedback.areas_for_improvement.map((area, index) => (
                    <li key={index} className="flex items-start gap-2">
                      <AlertCircle className="w-5 h-5 text-orange-600 flex-shrink-0 mt-0.5" />
                      <span className="text-gray-700">{area}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>

          {/* Recommended Focus */}
          <div className="bg-white rounded-lg shadow mb-6">
            <div className="border-b border-gray-200 px-6 py-4">
              <div className="flex items-center gap-2">
                <BookOpen className="w-5 h-5 text-blue-600" />
                <h2 className="text-lg font-bold text-gray-900">Recommended Focus Areas</h2>
              </div>
            </div>
            <div className="p-6">
              <div className="flex flex-wrap gap-2">
                {results.feedback.recommended_focus.map((focus, index) => (
                  <span
                    key={index}
                    className="px-4 py-2 bg-blue-100 text-blue-800 rounded-full text-sm font-medium"
                  >
                    {focus.replace(/_/g, ' ')}
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-4">
            <button
              onClick={() => navigate({ to: '/curriculum/performance' })}
              className="flex-1 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg"
            >
              View Performance Dashboard
            </button>
            <button
              onClick={() => navigate({ to: '/curriculum/daily' })}
              className="flex-1 px-6 py-3 bg-gray-200 hover:bg-gray-300 text-gray-800 font-medium rounded-lg"
            >
              Continue Practice
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Taking Assessment View
  const currentSection = getCurrentSection();
  const currentItem = getCurrentItem();
  const completionPercentage = getCompletionPercentage();

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow mb-6">
          <div className="px-6 py-4">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h1 className="text-2xl font-bold text-gray-900">{assessment.content.title}</h1>
                <p className="text-sm text-gray-600 capitalize">{assessment.assessment_type} Assessment</p>
              </div>
              {timeRemaining !== null && (
                <div className="flex items-center gap-2 px-4 py-2 bg-blue-50 rounded-lg">
                  <Clock className="w-5 h-5 text-blue-600" />
                  <span className="font-mono text-lg font-bold text-blue-900">
                    {formatTime(timeRemaining)}
                  </span>
                </div>
              )}
            </div>

            {/* Progress Bar */}
            <div>
              <div className="flex items-center justify-between text-sm text-gray-600 mb-2">
                <span>Progress: {Math.round(completionPercentage)}%</span>
                <span>
                  Section {currentSectionIndex + 1} of {assessment.content.sections.length}
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${completionPercentage}%` }}
                />
              </div>
            </div>
          </div>

          {/* Section Navigation */}
          <div className="border-t border-gray-200 px-6 py-3 bg-gray-50">
            <div className="flex gap-2 overflow-x-auto">
              {assessment.content.sections.map((section, index) => (
                <button
                  key={section.section_id}
                  onClick={() => {
                    setCurrentSectionIndex(index);
                    setCurrentItemIndex(0);
                  }}
                  className={`px-4 py-2 rounded text-sm font-medium whitespace-nowrap transition-colors ${
                    index === currentSectionIndex
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  {section.title}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Question/Exercise Display */}
        {currentItem && currentSection && (
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <div className="mb-6">
              <div className="flex items-center justify-between mb-2">
                <h2 className="text-xl font-bold text-gray-900">{currentSection.title}</h2>
                <span className="text-sm text-gray-600">
                  {currentItemIndex + 1} of {getTotalItems()}
                </span>
              </div>
              <p className="text-sm text-gray-600">
                Weight: {(currentSection.weight * 100).toFixed(0)}% | Points: {currentItem.points}
              </p>
            </div>

            {currentItem.itemType === 'question' ? (
              <div className="space-y-4">
                <p className="text-lg text-gray-900">{currentItem.question}</p>

                {currentItem.type === 'multiple_choice' && currentItem.options && (
                  <div className="space-y-2">
                    {currentItem.options.map((option, index) => (
                      <label
                        key={index}
                        className="flex items-center gap-3 p-4 border-2 rounded-lg cursor-pointer hover:bg-gray-50 transition-colors"
                      >
                        <input
                          type="radio"
                          name={currentItem.id}
                          value={index}
                          checked={responses[currentItem.id] === index}
                          onChange={() => handleResponseChange(currentItem.id, index)}
                          className="w-5 h-5 text-blue-600"
                        />
                        <span className="text-gray-900">{option}</span>
                      </label>
                    ))}
                  </div>
                )}

                {currentItem.type === 'true_false' && (
                  <div className="space-y-2">
                    {['True', 'False'].map((option) => (
                      <label
                        key={option}
                        className="flex items-center gap-3 p-4 border-2 rounded-lg cursor-pointer hover:bg-gray-50 transition-colors"
                      >
                        <input
                          type="radio"
                          name={currentItem.id}
                          value={option}
                          checked={responses[currentItem.id] === option}
                          onChange={() => handleResponseChange(currentItem.id, option)}
                          className="w-5 h-5 text-blue-600"
                        />
                        <span className="text-gray-900">{option}</span>
                      </label>
                    ))}
                  </div>
                )}

                {currentItem.type === 'short_answer' && (
                  <textarea
                    value={responses[currentItem.id] || ''}
                    onChange={(e) => handleResponseChange(currentItem.id, e.target.value)}
                    className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    rows={4}
                    placeholder="Type your answer here..."
                  />
                )}
              </div>
            ) : (
              <div className="space-y-4">
                <div className="bg-blue-50 border-l-4 border-blue-400 p-4 rounded">
                  <p className="font-semibold text-gray-900 mb-2">Practical Exercise</p>
                  <p className="text-gray-700">{currentItem.instruction}</p>
                </div>

                {currentItem.evaluation_criteria && currentItem.evaluation_criteria.length > 0 && (
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2">Evaluation Criteria:</h4>
                    <ul className="list-disc list-inside space-y-1 text-gray-700">
                      {currentItem.evaluation_criteria.map((criteria, index) => (
                        <li key={index}>{criteria}</li>
                      ))}
                    </ul>
                  </div>
                )}

                <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                  <p className="text-sm text-gray-600 mb-3">Record your performance notes:</p>
                  <textarea
                    value={responses[currentItem.id] || ''}
                    onChange={(e) => handleResponseChange(currentItem.id, e.target.value)}
                    className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    rows={4}
                    placeholder="Describe your performance and any challenges..."
                  />
                </div>
              </div>
            )}
          </div>
        )}

        {/* Navigation Buttons */}
        <div className="flex gap-4">
          <button
            onClick={goToPreviousItem}
            disabled={currentSectionIndex === 0 && currentItemIndex === 0}
            className="px-6 py-3 bg-gray-200 hover:bg-gray-300 text-gray-800 font-medium rounded-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            <ArrowLeft className="w-5 h-5" />
            Previous
          </button>

          {!isLastItem() ? (
            <button
              onClick={goToNextItem}
              className="flex-1 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg flex items-center justify-center gap-2"
            >
              Next
              <ArrowRight className="w-5 h-5" />
            </button>
          ) : (
            <button
              onClick={handleSubmitAssessment}
              disabled={isSubmitting}
              className="flex-1 px-6 py-3 bg-green-600 hover:bg-green-700 text-white font-medium rounded-lg disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {isSubmitting ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  Submitting...
                </>
              ) : (
                <>
                  <Send className="w-5 h-5" />
                  Submit Assessment
                </>
              )}
            </button>
          )}
        </div>

        {/* Auto-save indicator */}
        <p className="text-xs text-gray-500 text-center mt-4">
          Your responses are automatically saved
        </p>
      </div>
    </div>
  );
}
