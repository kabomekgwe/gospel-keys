/**
 * Practice Store Tests
 */
import { describe, it, expect, beforeEach } from 'vitest';
import { usePracticeStore } from './practiceStore';

describe('practiceStore', () => {
    beforeEach(() => {
        // Clear localStorage to avoid persistence issues
        localStorage.clear();

        // Reset store before each test
        usePracticeStore.setState({
            currentStreak: 0,
            longestStreak: 0,
            xp: 0,
            level: 1,
            todayPracticeSeconds: 0,
            lastPracticeDate: null,
            goal: {
                dailyMinutes: 30,
                weeklyDays: 5,
            },
            sessions: [],
            dailyHistory: [],
        });
    });

    describe('streak management', () => {
        it('starts with zero streak', () => {
            const state = usePracticeStore.getState();
            expect(state.currentStreak).toBe(0);
            expect(state.longestStreak).toBe(0);
        });
    });

    describe('XP and leveling', () => {
        it('starts at level 1 with 0 XP', () => {
            const state = usePracticeStore.getState();
            expect(state.level).toBe(1);
            expect(state.xp).toBe(0);
        });

        it('adds XP correctly via addPracticeTime', () => {
            const { addPracticeTime } = usePracticeStore.getState();
            // 5 minutes = 50 XP (10 per minute) - not enough to level up
            addPracticeTime(300);

            const state = usePracticeStore.getState();
            expect(state.xp).toBe(50);
        });

        it('levels up when XP threshold reached', () => {
            const { addPracticeTime } = usePracticeStore.getState();
            // 10 minutes = 100 XP, which is enough for level 1 -> 2
            addPracticeTime(600);

            const state = usePracticeStore.getState();
            expect(state.level).toBeGreaterThan(1);
        });
    });

    describe('goal management', () => {
        it('has default goal values', () => {
            const state = usePracticeStore.getState();
            expect(state.goal.dailyMinutes).toBe(30);
            expect(state.goal.weeklyDays).toBe(5);
        });

        it('updates goal correctly', () => {
            const { setGoal } = usePracticeStore.getState();
            setGoal({ dailyMinutes: 60, weeklyDays: 7 });

            const state = usePracticeStore.getState();
            expect(state.goal.dailyMinutes).toBe(60);
            expect(state.goal.weeklyDays).toBe(7);
        });
    });

    describe('session tracking', () => {
        it('starts with empty sessions', () => {
            const state = usePracticeStore.getState();
            expect(state.sessions).toHaveLength(0);
        });

        it('logs practice time correctly', () => {
            const { addPracticeTime } = usePracticeStore.getState();
            addPracticeTime(600); // 10 minutes in seconds

            const state = usePracticeStore.getState();
            expect(state.todayPracticeSeconds).toBe(600);
        });
    });

    describe('progress calculations', () => {
        it('calculates today progress correctly', () => {
            const store = usePracticeStore.getState();
            // Log 15 minutes (half of 30 minute goal)
            store.addPracticeTime(900);

            const progress = usePracticeStore.getState().getTodayProgress();
            expect(progress).toBe(50); // 50%
        });

        it('caps progress at 100%', () => {
            const store = usePracticeStore.getState();
            // Log 60 minutes (double the 30 minute goal)
            store.addPracticeTime(3600);

            const progress = usePracticeStore.getState().getTodayProgress();
            expect(progress).toBe(100);
        });
    });
});
