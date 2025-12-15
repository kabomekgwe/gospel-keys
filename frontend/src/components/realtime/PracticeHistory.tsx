/**
 * PracticeHistory Component
 * STORY-3.3: Frontend Visualization & Integration
 *
 * Displays a timeline of practice sessions with:
 * - Session list sorted by date
 * - Duration and status indicators
 * - Piece/genre information
 * - Expandable session details
 * - Pagination for large session counts
 */

import { useEffect, useState } from 'react';
import { realtimeAnalysisApi, type RealtimeSession } from '../../lib/api';

export interface PracticeHistoryProps {
  /** User ID to fetch sessions for */
  userId: number;
  /** Number of sessions to display per page */
  pageSize?: number;
  /** Filter by status */
  statusFilter?: 'active' | 'completed' | 'abandoned' | 'all';
  /** Color theme */
  theme?: 'light' | 'dark';
  /** Callback when session is selected */
  onSessionSelect?: (session: RealtimeSession) => void;
}

/**
 * Format duration in seconds to human-readable string
 */
function formatDuration(seconds: number | null | undefined): string {
  if (!seconds) return 'N/A';

  const hrs = Math.floor(seconds / 3600);
  const mins = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);

  if (hrs > 0) {
    return `${hrs}h ${mins}m`;
  } else if (mins > 0) {
    return `${mins}m ${secs}s`;
  } else {
    return `${secs}s`;
  }
}

/**
 * Format date to relative time (e.g., "2 hours ago")
 */
function formatRelativeTime(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffSecs = Math.floor(diffMs / 1000);
  const diffMins = Math.floor(diffSecs / 60);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffDays > 7) {
    return date.toLocaleDateString();
  } else if (diffDays > 0) {
    return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
  } else if (diffHours > 0) {
    return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
  } else if (diffMins > 0) {
    return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
  } else {
    return 'Just now';
  }
}

/**
 * Get status badge color
 */
function getStatusColor(status: string, isDark: boolean): string {
  switch (status) {
    case 'active':
      return isDark ? 'bg-green-900/20 text-green-400 border-green-700' : 'bg-green-50 text-green-700 border-green-200';
    case 'completed':
      return isDark ? 'bg-blue-900/20 text-blue-400 border-blue-700' : 'bg-blue-50 text-blue-700 border-blue-200';
    case 'abandoned':
      return isDark ? 'bg-gray-700 text-gray-400 border-gray-600' : 'bg-gray-100 text-gray-600 border-gray-300';
    default:
      return isDark ? 'bg-gray-700 text-gray-400 border-gray-600' : 'bg-gray-100 text-gray-600 border-gray-300';
  }
}

export function PracticeHistory({
  userId,
  pageSize = 10,
  statusFilter = 'all',
  theme = 'light',
  onSessionSelect,
}: PracticeHistoryProps) {
  const [sessions, setSessions] = useState<RealtimeSession[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedSessionId, setExpandedSessionId] = useState<string | null>(null);
  const [page, setPage] = useState<number>(0);
  const [hasMore, setHasMore] = useState<boolean>(true);

  // Fetch sessions
  useEffect(() => {
    const fetchSessions = async () => {
      setLoading(true);
      setError(null);

      try {
        const params: any = {
          userId,
          limit: pageSize,
          offset: page * pageSize,
        };

        if (statusFilter !== 'all') {
          params.status = statusFilter;
        }

        const fetchedSessions = await realtimeAnalysisApi.getUserSessions(params);
        setSessions(fetchedSessions);
        setHasMore(fetchedSessions.length === pageSize);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch sessions');
      } finally {
        setLoading(false);
      }
    };

    fetchSessions();
  }, [userId, page, pageSize, statusFilter]);

  const isDark = theme === 'dark';
  const bgColor = isDark ? 'bg-gray-800' : 'bg-white';
  const textColor = isDark ? 'text-gray-100' : 'text-gray-900';
  const mutedColor = isDark ? 'text-gray-400' : 'text-gray-600';
  const borderColor = isDark ? 'border-gray-700' : 'border-gray-200';
  const hoverColor = isDark ? 'hover:bg-gray-700' : 'hover:bg-gray-50';

  if (loading && sessions.length === 0) {
    return (
      <div className={`${bgColor} rounded-lg shadow-md p-6`}>
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500" />
          <span className={`ml-3 ${mutedColor}`}>Loading sessions...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`${bgColor} rounded-lg shadow-md p-6`}>
        <div className="text-center py-12">
          <p className="text-red-600 mb-2">Error loading sessions</p>
          <p className={`text-sm ${mutedColor}`}>{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`${bgColor} rounded-lg shadow-md p-4 space-y-3`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className={`text-lg font-semibold ${textColor}`}>Practice History</h3>
        <span className={`text-sm ${mutedColor}`}>
          {sessions.length} session{sessions.length !== 1 ? 's' : ''}
        </span>
      </div>

      {/* Session List */}
      {sessions.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-6xl mb-4">📝</div>
          <p className={`text-lg ${mutedColor}`}>No practice sessions yet</p>
          <p className={`text-sm ${mutedColor} mt-2`}>
            Start a session to track your practice progress!
          </p>
        </div>
      ) : (
        <div className="space-y-2">
          {sessions.map((session) => {
            const isExpanded = expandedSessionId === session.id;

            return (
              <div
                key={session.id}
                className={`border rounded-lg overflow-hidden ${borderColor} ${hoverColor} transition-colors`}
              >
                {/* Session Summary */}
                <button
                  onClick={() => {
                    setExpandedSessionId(isExpanded ? null : session.id);
                    if (!isExpanded && onSessionSelect) {
                      onSessionSelect(session);
                    }
                  }}
                  className="w-full p-3 text-left flex items-center justify-between"
                >
                  <div className="flex-1 space-y-1">
                    {/* Piece Name or Generic Label */}
                    <div className="flex items-center gap-2">
                      <h4 className={`font-semibold ${textColor}`}>
                        {session.piece_name || 'Practice Session'}
                      </h4>
                      {session.genre && (
                        <span className={`text-xs px-2 py-0.5 rounded ${mutedColor} border ${borderColor}`}>
                          {session.genre}
                        </span>
                      )}
                    </div>

                    {/* Date and Duration */}
                    <div className="flex items-center gap-4 text-sm">
                      <span className={mutedColor}>
                        {formatRelativeTime(session.started_at)}
                      </span>
                      <span className={mutedColor}>
                        {formatDuration(session.duration_seconds)}
                      </span>
                      {session.target_tempo && (
                        <span className={mutedColor}>
                          {session.target_tempo} BPM
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Status Badge */}
                  <div className="flex items-center gap-2">
                    <span
                      className={`text-xs px-2 py-1 rounded border ${getStatusColor(session.status, isDark)}`}
                    >
                      {session.status}
                    </span>
                    <svg
                      className={`w-5 h-5 transition-transform ${isExpanded ? 'rotate-180' : ''} ${mutedColor}`}
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M19 9l-7 7-7-7"
                      />
                    </svg>
                  </div>
                </button>

                {/* Expanded Details */}
                {isExpanded && (
                  <div className={`px-3 pb-3 border-t ${borderColor} space-y-2`}>
                    <div className="grid grid-cols-2 gap-3 text-sm pt-3">
                      <div>
                        <div className={`${mutedColor} text-xs uppercase tracking-wide mb-1`}>
                          Started
                        </div>
                        <div className={textColor}>
                          {new Date(session.started_at).toLocaleString()}
                        </div>
                      </div>

                      {session.ended_at && (
                        <div>
                          <div className={`${mutedColor} text-xs uppercase tracking-wide mb-1`}>
                            Ended
                          </div>
                          <div className={textColor}>
                            {new Date(session.ended_at).toLocaleString()}
                          </div>
                        </div>
                      )}

                      {session.difficulty_level && (
                        <div>
                          <div className={`${mutedColor} text-xs uppercase tracking-wide mb-1`}>
                            Difficulty
                          </div>
                          <div className={textColor}>
                            {session.difficulty_level}
                          </div>
                        </div>
                      )}

                      <div>
                        <div className={`${mutedColor} text-xs uppercase tracking-wide mb-1`}>
                          Chunks Processed
                        </div>
                        <div className={textColor}>
                          {session.chunks_processed}
                        </div>
                      </div>
                    </div>

                    {/* Session ID (for debugging) */}
                    <div className="text-xs">
                      <span className={mutedColor}>Session ID: </span>
                      <span className={`font-mono ${mutedColor}`}>
                        {session.id.substring(0, 8)}...
                      </span>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Pagination */}
      {sessions.length > 0 && (
        <div className="flex items-center justify-between pt-2">
          <button
            onClick={() => setPage((p) => Math.max(0, p - 1))}
            disabled={page === 0 || loading}
            className={`px-4 py-2 rounded text-sm font-medium transition-colors ${
              page === 0 || loading
                ? `${mutedColor} cursor-not-allowed`
                : `${textColor} ${hoverColor} border ${borderColor}`
            }`}
          >
            Previous
          </button>

          <span className={`text-sm ${mutedColor}`}>
            Page {page + 1}
          </span>

          <button
            onClick={() => setPage((p) => p + 1)}
            disabled={!hasMore || loading}
            className={`px-4 py-2 rounded text-sm font-medium transition-colors ${
              !hasMore || loading
                ? `${mutedColor} cursor-not-allowed`
                : `${textColor} ${hoverColor} border ${borderColor}`
            }`}
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}
