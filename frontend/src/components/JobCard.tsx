/**
 * Job Card Component
 * 
 * Displays individual transcription job status with progress
 */
import { Link } from '@tanstack/react-router';
import { motion } from 'framer-motion';
import {
    Clock,
    CheckCircle2,
    AlertCircle,
    Loader2,
    ExternalLink,
    Music2,
    RefreshCw,
    Trash2,
} from 'lucide-react';
import type { TranscriptionJob } from '../lib/api';

export interface JobCardProps {
    job: TranscriptionJob;
    onRetry?: (jobId: string) => void;
    onDelete?: (jobId: string) => void;
}

function getStatusColor(status: TranscriptionJob['status']) {
    switch (status) {
        case 'complete':
            return 'text-green-400 bg-green-500/10 border-green-500/30';
        case 'error':
            return 'text-red-400 bg-red-500/10 border-red-500/30';
        case 'processing':
            return 'text-cyan-400 bg-cyan-500/10 border-cyan-500/30';
        case 'pending':
        default:
            return 'text-slate-400 bg-slate-500/10 border-slate-500/30';
    }
}

function getStatusIcon(status: TranscriptionJob['status']) {
    switch (status) {
        case 'complete':
            return <CheckCircle2 className="w-4 h-4" />;
        case 'error':
            return <AlertCircle className="w-4 h-4" />;
        case 'processing':
            return <Loader2 className="w-4 h-4 animate-spin" />;
        case 'pending':
        default:
            return <Clock className="w-4 h-4" />;
    }
}

function getStatusLabel(status: TranscriptionJob['status']) {
    switch (status) {
        case 'complete':
            return 'Complete';
        case 'error':
            return 'Failed';
        case 'processing':
            return 'Processing';
        case 'pending':
        default:
            return 'Pending';
    }
}

export function JobCard({ job, onRetry, onDelete }: JobCardProps) {
    const statusColor = getStatusColor(job.status);
    const statusIcon = getStatusIcon(job.status);
    const statusLabel = getStatusLabel(job.status);

    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="card p-4 hover:border-slate-600/50 transition-colors"
        >
            <div className="flex items-start gap-4">
                {/* Icon */}
                <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-cyan-500/20 to-violet-500/20 flex items-center justify-center flex-shrink-0">
                    <Music2 className="w-6 h-6 text-cyan-400" />
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-2 mb-2">
                        <div>
                            <h3 className="text-white font-medium truncate">
                                {job.result?.title || `Job ${job.job_id.slice(0, 8)}...`}
                            </h3>
                            <p className="text-slate-400 text-sm truncate">
                                ID: {job.job_id}
                            </p>
                        </div>

                        {/* Status badge */}
                        <span className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${statusColor}`}>
                            {statusIcon}
                            {statusLabel}
                        </span>
                    </div>

                    {/* Progress bar (for processing/pending) */}
                    {(job.status === 'processing' || job.status === 'pending') && (
                        <div className="mb-3">
                            <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
                                <span>{job.current_step || 'Starting...'}</span>
                                <span>{job.progress}%</span>
                            </div>
                            <div className="h-1.5 bg-slate-700 rounded-full overflow-hidden">
                                <motion.div
                                    className="h-full bg-gradient-to-r from-cyan-500 to-cyan-400"
                                    initial={{ width: 0 }}
                                    animate={{ width: `${job.progress}%` }}
                                    transition={{ duration: 0.3 }}
                                />
                            </div>
                        </div>
                    )}

                    {/* Error message */}
                    {job.status === 'error' && job.error_message && (
                        <div className="mb-3 p-2 bg-red-500/10 border border-red-500/20 rounded-lg">
                            <p className="text-red-400 text-sm">{job.error_message}</p>
                        </div>
                    )}

                    {/* Result info */}
                    {job.status === 'complete' && job.result && (
                        <div className="flex items-center gap-3 text-sm text-slate-400 mb-3">
                            <span>{job.result.note_count} notes</span>
                            <span>•</span>
                            <span>{job.result.chord_count} chords</span>
                            <span>•</span>
                            <span>{job.result.key_signature || 'Unknown key'}</span>
                        </div>
                    )}

                    {/* Actions */}
                    <div className="flex items-center gap-2">
                        {job.status === 'complete' && job.result && (
                            <Link
                                to={`/library/${job.result.song_id}`}
                                className="flex items-center gap-1.5 px-3 py-1.5 bg-cyan-500/20 text-cyan-400 rounded-lg text-sm hover:bg-cyan-500/30 transition-colors"
                            >
                                <ExternalLink className="w-3.5 h-3.5" />
                                View Song
                            </Link>
                        )}

                        {job.status === 'error' && onRetry && (
                            <motion.button
                                whileHover={{ scale: 1.02 }}
                                whileTap={{ scale: 0.98 }}
                                onClick={() => onRetry(job.job_id)}
                                className="flex items-center gap-1.5 px-3 py-1.5 bg-amber-500/20 text-amber-400 rounded-lg text-sm hover:bg-amber-500/30 transition-colors"
                            >
                                <RefreshCw className="w-3.5 h-3.5" />
                                Retry
                            </motion.button>
                        )}

                        {onDelete && job.status !== 'processing' && (
                            <motion.button
                                whileHover={{ scale: 1.02 }}
                                whileTap={{ scale: 0.98 }}
                                onClick={() => onDelete(job.job_id)}
                                className="flex items-center gap-1.5 px-3 py-1.5 text-slate-400 rounded-lg text-sm hover:bg-slate-700/50 hover:text-red-400 transition-colors"
                            >
                                <Trash2 className="w-3.5 h-3.5" />
                                Remove
                            </motion.button>
                        )}
                    </div>
                </div>
            </div>
        </motion.div>
    );
}
