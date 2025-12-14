import { useState } from 'react';
import { Link } from '@tanstack/react-router';
import { ChevronDown, ChevronUp, CheckCircle, Target, Lock, Book } from 'lucide-react';
import type { CurriculumResponse } from '../../lib/api';

interface ModuleGridProps {
  curriculum: CurriculumResponse;
}

export function ModuleGrid({ curriculum }: ModuleGridProps) {
  const [expandedModules, setExpandedModules] = useState<Set<string>>(new Set());

  const toggleModule = (moduleId: string) => {
    setExpandedModules((prev) => {
      const next = new Set(prev);
      if (next.has(moduleId)) {
        next.delete(moduleId);
      } else {
        next.add(moduleId);
      }
      return next;
    });
  };

  const getStatusBadge = (completionPercentage: number) => {
    if (completionPercentage === 0) {
      return { text: 'Not Started', color: 'bg-gray-600 text-gray-300' };
    } else if (completionPercentage === 100) {
      return { text: 'Completed', color: 'bg-green-600 text-white' };
    } else {
      return { text: 'In Progress', color: 'bg-purple-600 text-white' };
    }
  };

  return (
    <div>
      <h2 className="text-2xl font-bold text-white mb-6">Curriculum Modules</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {curriculum.modules.map((module, index) => {
          const isExpanded = expandedModules.has(module.id);
          const status = getStatusBadge(module.completion_percentage);
          const isCurrentModule = index === 0; // Simplified - in real app, check actual current week

          return (
            <div
              key={module.id}
              className={`bg-gray-800/50 rounded-xl border transition-all ${
                isCurrentModule ? 'border-purple-500 ring-2 ring-purple-500/50' : 'border-gray-700'
              }`}
            >
              {/* Module Card Header */}
              <div className="p-6">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      {isCurrentModule && (
                        <div className="w-2 h-2 bg-purple-500 rounded-full animate-pulse"></div>
                      )}
                      <h3 className="text-lg font-semibold text-white">{module.title}</h3>
                    </div>
                    <p className="text-sm text-gray-400 mb-2">{module.theme}</p>
                    <p className="text-xs text-gray-500">
                      Weeks {module.start_week}-{module.end_week}
                    </p>
                  </div>
                  <span className={`px-2 py-1 rounded text-xs font-medium ${status.color}`}>
                    {status.text}
                  </span>
                </div>

                {/* Progress Bar */}
                <div className="mb-4">
                  <div className="flex justify-between text-xs text-gray-400 mb-2">
                    <span>Progress</span>
                    <span className="text-white font-medium">{module.completion_percentage}%</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full transition-all duration-500 ${
                        module.completion_percentage === 100
                          ? 'bg-green-500'
                          : 'bg-gradient-to-r from-purple-500 to-blue-500'
                      }`}
                      style={{ width: `${module.completion_percentage}%` }}
                    />
                  </div>
                </div>

                {/* Lesson Count */}
                <div className="flex items-center justify-between text-sm mb-4">
                  <div className="flex items-center gap-2 text-gray-400">
                    <Book className="w-4 h-4" />
                    <span>{module.lesson_count} lessons</span>
                  </div>
                  {isCurrentModule && (
                    <span className="text-xs text-purple-400 font-medium">Current Module</span>
                  )}
                </div>

                {/* Expand/Collapse Button */}
                <button
                  onClick={() => toggleModule(module.id)}
                  className="w-full px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition flex items-center justify-center gap-2 text-sm font-medium"
                >
                  {isExpanded ? (
                    <>
                      <ChevronUp className="w-4 h-4" />
                      Hide Lessons
                    </>
                  ) : (
                    <>
                      <ChevronDown className="w-4 h-4" />
                      View Lessons
                    </>
                  )}
                </button>
              </div>

              {/* Expanded Lesson List */}
              {isExpanded && (
                <div className="border-t border-gray-700 p-4 space-y-2 bg-gray-900/50">
                  {/* Mock lessons - in real app, fetch from API */}
                  {Array.from({ length: module.lesson_count }, (_, i) => {
                    const lessonNumber = i + 1;
                    const isCompleted = i < Math.floor(module.lesson_count * (module.completion_percentage / 100));
                    const isCurrent = i === Math.floor(module.lesson_count * (module.completion_percentage / 100)) && module.completion_percentage < 100;
                    const isLocked = i > Math.floor(module.lesson_count * (module.completion_percentage / 100)) + 1;

                    const lessonId = `${module.id}-lesson-${lessonNumber}`;

                    return isLocked ? (
                      <div
                        key={i}
                        className={`w-full p-3 rounded-lg border transition text-left ${
                          isCompleted
                            ? 'border-green-600/30 bg-green-600/10 hover:bg-green-600/20'
                            : isCurrent
                            ? 'border-purple-600/50 bg-purple-600/20 hover:bg-purple-600/30'
                            : isLocked
                            ? 'border-gray-700 bg-gray-800/50 opacity-50 cursor-not-allowed'
                            : 'border-gray-700 bg-gray-800/50 opacity-50 cursor-not-allowed'
                        }`}
                      >
                        <div className="flex items-center gap-3">
                          <div className="flex-shrink-0">
                            <Lock className="w-5 h-5 text-gray-500" />
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-white truncate">
                              Lesson {lessonNumber}: {module.theme} - Part {lessonNumber}
                            </p>
                            <div className="flex items-center gap-3 mt-1">
                              <p className="text-xs text-gray-400">
                                Week {module.start_week + Math.floor((i / module.lesson_count) * (module.end_week - module.start_week + 1))}
                              </p>
                              <span className="text-xs text-gray-500">•</span>
                              <p className="text-xs text-gray-400">
                                {Math.floor(Math.random() * 10 + 5)} exercises
                              </p>
                            </div>
                          </div>
                        </div>
                      </div>
                    ) : (
                      <Link
                        key={i}
                        to="/curriculum/lessons/$lessonId"
                        params={{ lessonId }}
                        className={`block w-full p-3 rounded-lg border transition text-left ${
                          isCompleted
                            ? 'border-green-600/30 bg-green-600/10 hover:bg-green-600/20'
                            : isCurrent
                            ? 'border-purple-600/50 bg-purple-600/20 hover:bg-purple-600/30'
                            : 'border-gray-700 bg-gray-800/50 hover:bg-gray-700/50'
                        }`}
                      >
                        <div className="flex items-center gap-3">
                          {/* Status Icon */}
                          <div className="flex-shrink-0">
                            {isCompleted ? (
                              <CheckCircle className="w-5 h-5 text-green-500" />
                            ) : isCurrent ? (
                              <Target className="w-5 h-5 text-purple-500" />
                            ) : (
                              <div className="w-5 h-5 rounded-full border-2 border-gray-600"></div>
                            )}
                          </div>

                          {/* Lesson Info */}
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-white truncate">
                              Lesson {lessonNumber}: {module.theme} - Part {lessonNumber}
                            </p>
                            <div className="flex items-center gap-3 mt-1">
                              <p className="text-xs text-gray-400">
                                Week {module.start_week + Math.floor((i / module.lesson_count) * (module.end_week - module.start_week + 1))}
                              </p>
                              <span className="text-xs text-gray-500">•</span>
                              <p className="text-xs text-gray-400">
                                {Math.floor(Math.random() * 10 + 5)} exercises
                              </p>
                            </div>
                          </div>

                          {/* Completion Badge */}
                          {isCompleted && (
                            <div className="flex-shrink-0">
                              <span className="text-xs text-green-400 font-medium">✓ Done</span>
                            </div>
                          )}
                          {isCurrent && (
                            <div className="flex-shrink-0">
                              <span className="text-xs text-purple-400 font-medium">Current</span>
                            </div>
                          )}
                        </div>
                      </Link>
                    );
                  })}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
