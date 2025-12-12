/**
 * Jobs Page - Track transcription progress
 * 
 * Uses Zustand store for real job tracking with polling
 */

import { createFileRoute, Link, useSearch } from '@tanstack/react-router';
import {
    Loader2,
    CheckCircle2,
    XCircle,
    Clock,
    Music2,
    ExternalLink,
    Trash2,
} from 'lucide-react';
import { motion } from 'framer-motion';
import { useJobsStore, type StoredJob } from '../lib/jobsStore';
import { useMemo } from 'react';

export const Route = createFileRoute('/jobs')({
    validateSearch: (search: Record<string, unknown>) => ({
        highlight: search.highlight as string | undefined,
    }),
    component: JobsPage,
});

function JobsPage() {
    const { highlight } = useSearch({ from: '/jobs' });
    const allJobs = useJobsStore((state) => state.jobs);
    const jobs = useMemo(
        () => allJobs.slice(0, 20).filter((job) => job && job.job_id),
        [allJobs]
    );
    const { removeJob, clearCompleted } = useJobsStore();

    const activeJobsCount = jobs.filter(
        (j) => j.status === 'pending' || j.status === 'downloading' || j.status === 'processing' || j.status === 'analyzing'
    ).length;

    const completedJobsCount = jobs.filter(
        (j) => j.status === 'complete' || j.status === 'error'
    ).length;

    const getStatusIcon = (status: StoredJob['status']) => {
        switch (status) {
            case 'pending':
                return <Clock className="w-5 h-5 text-slate-400" />;
            case 'downloading':
                return <Loader2 className="w-5 h-5 text-blue-400 animate-spin" />;
            case 'processing':
                return <Loader2 className="w-5 h-5 text-cyan-400 animate-spin" />;
            case 'analyzing':
                return <Loader2 className="w-5 h-5 text-purple-400 animate-spin" />;
            case 'complete':
                return <CheckCircle2 className="w-5 h-5 text-emerald-400" />;
            case 'error':
                return <XCircle className="w-5 h-5 text-red-400" />;
            case 'cancelled':
                return <XCircle className="w-5 h-5 text-slate-500" />;
            default:
                return <Clock className="w-5 h-5 text-slate-400" />;
        }
    };

    const getStatusColor = (status: StoredJob['status']) => {
        switch (status) {
            case 'pending':
                return 'text-slate-400';
            case 'downloading':
                return 'text-blue-400';
            case 'processing':
                return 'text-cyan-400';
            case 'analyzing':
                return 'text-purple-400';
            case 'complete':
                return 'text-emerald-400';
            case 'error':
                return 'text-red-400';
            case 'cancelled':
                return 'text-slate-500';
            default:
                return 'text-slate-400';
        }
    };

    const formatTime = (isoString: string) => {
        const date = new Date(isoString);
        const now = new Date();
        const diff = now.getTime() - date.getTime();

        if (diff < 60000) return 'Just now';
        if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
        if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
        return date.toLocaleDateString();
    };

    return (
        <div className="min-h-screen p-8">
            <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex items-center justify-between mb-8"
            >
                <div>
                    <h1 className="text-3xl font-bold mb-2">Transcription Jobs</h1>
                    <p className="text-slate-400">
                        {activeJobsCount > 0
                            ? `${activeJobsCount} active job${activeJobsCount > 1 ? 's' : ''}`
                            : 'Track the progress of your transcriptions'
                        }
                    </p>
                </div>

                <div className="flex items-center gap-3">
                    {completedJobsCount > 0 && (
                        <button
                            onClick={clearCompleted}
                            className="flex items-center gap-2 px-4 py-2 text-slate-400 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-colors"
                        >
                            <Trash2 className="w-4 h-4" />
                            Clear Completed
                        </button>
                    )}

                    <div className="flex items-center gap-2 px-3 py-1.5 bg-slate-800 rounded-lg">
                        {activeJobsCount > 0 && (
                            <span className="flex items-center gap-1.5">
                                <span className="w-2 h-2 bg-cyan-400 rounded-full animate-pulse" />
                                <span className="text-sm text-slate-300">{activeJobsCount} active</span>
                            </span>
                        )}
                    </div>
                </div>
            </motion.div>

            {jobs.length > 0 ? (
                <div className="space-y-4">
                    {jobs.map((job, index) => (
                        <motion.div
                            key={job.job_id}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: index * 0.05 }}
                            className={`
                glass-card rounded-xl p-6 transition-all
                ${highlight === job.job_id ? 'ring-2 ring-cyan-500' : ''}
              `}
                        >
                            <div className="flex items-start justify-between mb-4">
                                <div className="flex items-center gap-3">
                                    {getStatusIcon(job.status)}
                                    <div>
                                        <h3 className="font-medium text-white">
                                            {job.title || job.result?.title || `Job ${job.job_id.slice(0, 8)}`}
                                        </h3>
                                        <p className="text-sm text-slate-500">
                                            {formatTime(job.created_at)} • ID: {job.job_id.slice(0, 12)}...
                                        </p>
                                    </div>
                                </div>

                                <div className="flex items-center gap-3">
                                    <span className={`text-sm font-medium capitalize ${getStatusColor(job.status)}`}>
                                        {job.status}
                                    </span>

                                    <button
                                        onClick={() => removeJob(job.job_id)}
                                        className="p-1.5 text-slate-500 hover:text-red-400 hover:bg-red-500/10 rounded transition-colors"
                                        title="Remove job"
                                    >
                                        <Trash2 className="w-4 h-4" />
                                    </button>
                                </div>
                            </div>

                            {/* Progress Bar */}
                            {(job.status === 'pending' || job.status === 'downloading' || job.status === 'processing' || job.status === 'analyzing') && (
                                <div className="mb-3">
                                    <div className="flex justify-between text-sm mb-1">
                                        <span className="text-slate-400">{job.current_step || 'Starting...'}</span>
                                        <span className="text-slate-500">{job.progress}%</span>
                                    </div>
                                    <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                                        <motion.div
                                            initial={{ width: 0 }}
                                            animate={{ width: `${job.progress}%` }}
                                            className="h-full bg-gradient-to-r from-cyan-500 to-blue-500"
                                        />
                                    </div>
                                </div>
                            )}

                            {/* Error Message */}
                            {job.status === 'error' && job.error_message && (
                                <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3 text-red-400 text-sm mb-3">
                                    {job.error_message}
                                </div>
                            )}

                            {/* Complete Actions */}
                            {job.status === 'complete' && job.result && (
                                <div className="flex items-center gap-3 mt-4 pt-4 border-t border-slate-700">
                                    <div className="flex-1 flex items-center gap-4 text-sm text-slate-400">
                                        <span>{job.result.note_count} notes</span>
                                        <span>{job.result.chord_count} chords</span>
                                        {job.result.key_signature && <span>{job.result.key_signature}</span>}
                                        {job.result.tempo && <span>{Math.round(job.result.tempo)} BPM</span>}
                                    </div>

                                    <div className="flex gap-2">
                                        <Link
                                            to="/library/$songId"
                                            params={{ songId: job.result.song_id }}
                                            className="flex items-center gap-2 px-4 py-2 bg-cyan-500/20 text-cyan-400 rounded-lg hover:bg-cyan-500/30 transition-colors"
                                        >
                                            <Music2 className="w-4 h-4" />
                                            View Song
                                        </Link>
                                        <button className="flex items-center gap-2 px-4 py-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors">
                                            <ExternalLink className="w-4 h-4" />
                                            Export
                                        </button>
                                    </div>
                                </div>
                            )}
                        </motion.div>
                    ))}
                </div>
            ) : (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="glass-card rounded-xl p-12 text-center"
                >
                    <Clock className="w-12 h-12 text-slate-600 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-slate-400 mb-2">No transcription jobs</h3>
                    <p className="text-slate-500 mb-6">
                        Start a new transcription to see progress here
                    </p>
                    <Link
                        to="/upload"
                        className="inline-flex items-center gap-2 px-6 py-3 bg-cyan-500 hover:bg-cyan-600 text-white font-medium rounded-lg transition-colors"
                    >
                        Start Transcription
                    </Link>
                </motion.div>
            )}
        </div>
    );
}