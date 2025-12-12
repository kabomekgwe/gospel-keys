/**
 * API Client Tests
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import {
    libraryApi,
    transcriptionApi,
    notesApi,
    analysisApi
} from './api';

// Mock fetch
const mockFetch = vi.fn();
global.fetch = mockFetch;

describe('API Module', () => {
    beforeEach(() => {
        mockFetch.mockReset();
    });

    describe('libraryApi', () => {
        it('listSongs > fetches songs from correct endpoint', async () => {
            const mockSongs = [{ id: '1', title: 'Test Song' }];
            mockFetch.mockResolvedValue({
                ok: true,
                json: async () => mockSongs,
            });

            const result = await libraryApi.listSongs();

            expect(result).toEqual(mockSongs);
            expect(mockFetch).toHaveBeenCalledWith(
                expect.stringContaining('http://localhost:8009/api/v1/library/songs')
            );
        });

        it('listSongs > passes query parameters correctly', async () => {
            mockFetch.mockResolvedValue({
                ok: true,
                json: async () => [],
            });

            await libraryApi.listSongs({ limit: 10, tag: 'jazz' });

            expect(mockFetch).toHaveBeenCalledWith(
                expect.stringContaining('limit=10')
            );
            expect(mockFetch).toHaveBeenCalledWith(
                expect.stringContaining('tag=jazz')
            );
        });

        it('getSong > fetches single song by ID', async () => {
            const mockSong = { id: 'test-id', title: 'Test Song' };
            mockFetch.mockResolvedValue({
                ok: true,
                json: async () => mockSong,
            });

            const result = await libraryApi.getSong('test-id');

            expect(result).toEqual(mockSong);
            expect(mockFetch).toHaveBeenCalledWith(
                expect.stringContaining('http://localhost:8009/api/v1/library/songs/test-id')
            );
        });

        it('deleteSong > sends DELETE request', async () => {
            mockFetch.mockResolvedValue({
                ok: true,
                json: async () => ({}),
            });

            await libraryApi.deleteSong('test-id');

            expect(mockFetch).toHaveBeenCalledWith(
                'http://localhost:8009/api/v1/library/songs/test-id',
                expect.objectContaining({
                    method: 'DELETE',
                })
            );
        });
    });

    describe('transcriptionApi', () => {
        it('getStatus > fetches job status', async () => {
            const mockJob = { job_id: 'job-1', status: 'pending' };
            mockFetch.mockResolvedValue({
                ok: true,
                json: async () => mockJob,
            });

            const result = await transcriptionApi.getStatus('job-1');

            expect(result).toEqual(mockJob);
            expect(mockFetch).toHaveBeenCalledWith(
                expect.stringContaining('http://localhost:8009/api/v1/transcribe/job-1')
            );
        });
    });

    describe('notesApi', () => {
        it('getNotes > fetches notes for song', async () => {
            const mockNotes = [{ pitch: 60, startTime: 0, duration: 1 }];
            mockFetch.mockResolvedValue({
                ok: true,
                json: async () => mockNotes,
            });

            const result = await notesApi.getNotes('song-1');

            expect(result).toEqual(mockNotes);
            expect(mockFetch).toHaveBeenCalledWith(
                expect.stringContaining('http://localhost:8009/api/v1/library/songs/song-1/notes')
            );
        });
    });

    describe('analysisApi', () => {
        it('getChords > fetches chords for song', async () => {
            const mockChords = [{ root: 'C', quality: 'major' }];
            mockFetch.mockResolvedValue({
                ok: true,
                json: async () => mockChords,
            });

            const result = await analysisApi.getChords('song-1');

            expect(result).toEqual(mockChords);
            expect(mockFetch).toHaveBeenCalledWith(
                expect.stringContaining('http://localhost:8009/api/v1/analyze/song-1/chords')
            );
        });

        it('getPatterns > fetches patterns for song', async () => {
            const mockPatterns = [{ type: 'ii-V-I' }];
            mockFetch.mockResolvedValue({
                ok: true,
                json: async () => mockPatterns,
            });

            const result = await analysisApi.getPatterns('song-1');

            expect(result).toEqual(mockPatterns);
            expect(mockFetch).toHaveBeenCalledWith(
                expect.stringContaining('http://localhost:8009/api/v1/analyze/song-1/patterns')
            );
        });
    });
});
