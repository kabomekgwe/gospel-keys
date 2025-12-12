import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { transcriptionApi, type TranscriptionJob } from './api';

export interface StoredJob extends TranscriptionJob {
    title?: string;
    created_at: string;
}

interface JobsState {
    // State
    jobs: StoredJob[];
    activePolling: Set<string>;

    // Actions
    addJob: (job: TranscriptionJob, title?: string) => void;
    updateJob: (jobId: string, updates: Partial<StoredJob>) => void;
    removeJob: (jobId: string) => void;
    clearCompleted: () => void;

    // Polling
    startPolling: (jobId: string) => void;
    stopPolling: (jobId: string) => void;
    pollJob: (jobId: string) => Promise<void>;
}

// Polling intervals by status
const POLL_INTERVALS = {
    pending: 3000,
    processing: 1500,
    complete: 0,
    error: 0,
};

export const useJobsStore = create<JobsState>()(
    persist(
        (set, get) => ({
            jobs: [],
            activePolling: new Set(),

            addJob: (job, title) => {
                const storedJob: StoredJob = {
                    ...job,
                    title: title || `Job ${job.job_id.slice(0, 8)}`,
                    created_at: new Date().toISOString(),
                };

                set((state) => ({
                    jobs: [storedJob, ...state.jobs],
                }));

                // Start polling if not complete/error
                if (job.status === 'pending' || job.status === 'processing') {
                    get().startPolling(job.job_id);
                }
            },

            updateJob: (jobId, updates) => {
                set((state) => ({
                    jobs: state.jobs.map((job) =>
                        job.job_id === jobId ? { ...job, ...updates } : job
                    ),
                }));
            },

            removeJob: (jobId) => {
                get().stopPolling(jobId);
                set((state) => ({
                    jobs: state.jobs.filter((job) => job.job_id !== jobId),
                }));
            },

            clearCompleted: () => {
                set((state) => ({
                    jobs: state.jobs.filter((job) =>
                        job.status !== 'complete' && job.status !== 'error'
                    ),
                }));
            },

            startPolling: (jobId) => {
                const { activePolling, pollJob } = get();

                if (activePolling.has(jobId)) return;

                const newPolling = new Set(activePolling);
                newPolling.add(jobId);
                set({ activePolling: newPolling });

                // Initial poll
                pollJob(jobId);
            },

            stopPolling: (jobId) => {
                const { activePolling } = get();
                const newPolling = new Set(activePolling);
                newPolling.delete(jobId);
                set({ activePolling: newPolling });
            },

            pollJob: async (jobId) => {
                const { activePolling, updateJob, stopPolling } = get();

                if (!activePolling.has(jobId)) return;

                try {
                    const status = await transcriptionApi.getStatus(jobId);

                    // Update job with new status
                    updateJob(jobId, {
                        status: status.status,
                        progress: status.progress,
                        current_step: status.current_step,
                        error_message: status.error_message,
                        result: status.result,
                    });

                    // Schedule next poll if still active
                    const interval = POLL_INTERVALS[status.status];
                    if (interval > 0 && activePolling.has(jobId)) {
                        setTimeout(() => get().pollJob(jobId), interval);
                    } else {
                        stopPolling(jobId);
                    }
                } catch (error) {
                    console.error(`Error polling job ${jobId}:`, error);
                    // Stop polling on error
                    stopPolling(jobId);
                    updateJob(jobId, {
                        status: 'error',
                        error_message: error instanceof Error ? error.message : 'Failed to get status',
                    });
                }
            },
        }),
        {
            name: 'piano-keys-jobs',
            storage: createJSONStorage(() => localStorage),
            partialize: (state) => ({
                jobs: state.jobs,
            }),
            // Resume polling for incomplete jobs on load
            onRehydrateStorage: () => (state) => {
                if (state) {
                    state.jobs.forEach((job) => {
                        if (job.status === 'pending' || job.status === 'processing') {
                            state.startPolling(job.job_id);
                        }
                    });
                }
            },
        }
    )
);
