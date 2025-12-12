/**
 * Jobs Store Tests
 */
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useJobsStore } from './jobsStore';
import { transcriptionApi, type TranscriptionJob } from './api';

// Mock transcriptionApi
vi.mock('./api', async () => {
    const actual = await vi.importActual('./api');
    return {
        ...actual,
        transcriptionApi: {
            getStatus: vi.fn().mockImplementation(() => Promise.resolve({
                status: 'processing',
                progress: 50
            })),
        },
    };
});

describe('jobsStore', () => {
    beforeEach(() => {
        // Reset store
        useJobsStore.setState({
            jobs: [],
            isPolling: false,
            activePolling: new Set(), // Changed from isPolling: false
            pollInterval: null,
        });
        vi.clearAllMocks();
    });

    describe('initial state', () => {
        it('starts with empty jobs array', () => {
            const state = useJobsStore.getState();
            expect(state.jobs).toEqual([]);
        });

        it('starts with polling disabled', () => {
            const state = useJobsStore.getState();
            expect(state.activePolling.size).toBe(0);
        });
    });

    describe('addJob', () => {
        it('adds a new job to the list', () => {
            const { addJob } = useJobsStore.getState();

            const job: any = {
                job_id: 'job-1',
                type: 'transcribe',
                status: 'pending',
                progress: 0,
                current_step: 'init',
                created_at: new Date().toISOString()
            };

            addJob(job);

            const state = useJobsStore.getState();
            expect(state.jobs).toHaveLength(1);
            expect(state.jobs[0].job_id).toBe('job-1');
        });

        it('adds multiple jobs', () => {
            const { addJob } = useJobsStore.getState();

            const job1: any = { job_id: 'job-1', type: 'transcribe', status: 'pending', progress: 0, current_step: 'init', created_at: new Date().toISOString() };
            const job2: any = { job_id: 'job-2', type: 'analyze', status: 'pending', progress: 0, current_step: 'init', created_at: new Date().toISOString() };

            addJob(job1);
            addJob(job2);

            const state = useJobsStore.getState();
            expect(state.jobs).toHaveLength(2);
        });
    });

    describe('updateJob', () => {
        it('updates existing job', () => {
            const { addJob, updateJob } = useJobsStore.getState();

            const job: any = { job_id: 'job-1', type: 'transcribe', status: 'pending', progress: 0, current_step: 'init', created_at: new Date().toISOString() };
            addJob(job);
            updateJob('job-1', { status: 'processing', progress: 50 });

            const state = useJobsStore.getState();
            expect(state.jobs[0].status).toBe('processing');
            expect(state.jobs[0].progress).toBe(50);
        });

        it('does not error on non-existent job', () => {
            const { updateJob } = useJobsStore.getState();

            expect(() => {
                updateJob('non-existent', { status: 'complete' });
            }).not.toThrow();
        });
    });

    describe('removeJob', () => {
        it('removes job by ID', () => {
            const { addJob, removeJob } = useJobsStore.getState();

            const job1: any = { job_id: 'job-1', type: 'transcribe', status: 'pending', progress: 0, current_step: 'init', created_at: new Date().toISOString() };
            const job2: any = { job_id: 'job-2', type: 'analyze', status: 'pending', progress: 0, current_step: 'init', created_at: new Date().toISOString() };

            addJob(job1);
            addJob(job2);

            removeJob('job-1');

            const state = useJobsStore.getState();
            expect(state.jobs).toHaveLength(1);
            expect(state.jobs[0].job_id).toBe('job-2');
        });
    });

    describe('clearCompleted', () => {
        it('removes all completed jobs', () => {
            const { addJob, updateJob, clearCompleted } = useJobsStore.getState();

            const job1: any = { job_id: 'job-1', type: 'transcribe', status: 'pending', progress: 0, current_step: 'init', created_at: new Date().toISOString() };
            const job2: any = { job_id: 'job-2', type: 'analyze', status: 'pending', progress: 0, current_step: 'init', created_at: new Date().toISOString() };

            addJob(job1);
            addJob(job2);

            updateJob('job-1', { status: 'complete', progress: 100 });
            clearCompleted();

            const state = useJobsStore.getState();
            expect(state.jobs).toHaveLength(1);
            expect(state.jobs[0].job_id).toBe('job-2');
        });
    });

    describe('active jobs', () => {
        it('can filter active jobs manually', () => {
            const { addJob, updateJob } = useJobsStore.getState();

            const job1: any = { job_id: 'job-1', type: 'transcribe', status: 'processing', progress: 50, current_step: 'transcribing', created_at: new Date().toISOString() };
            const job2: any = { job_id: 'job-2', type: 'analyze', status: 'complete', progress: 100, current_step: 'done', created_at: new Date().toISOString() };

            addJob(job1);
            addJob(job2);

            // Manually filter as getActiveJobs is a hook/selector not state method
            const state = useJobsStore.getState();
            const activeJobs = state.jobs.filter(j => j.status !== 'complete' && j.status !== 'error');

            expect(activeJobs).toHaveLength(1);
            expect(activeJobs[0].job_id).toBe('job-1');
        });
    });
});
