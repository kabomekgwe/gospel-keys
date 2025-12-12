/**
 * Practice Store
 * 
 * Zustand store for tracking practice sessions, streaks, and goals
 * with localStorage persistence
 */
import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

export interface PracticeSession {
    id: string;
    songId?: string;
    songTitle?: string;
    startTime: string;
    endTime?: string;
    durationSeconds: number;
    tempoMultiplier: number;
    notes?: string;
}

export interface DailyPractice {
    date: string; // YYYY-MM-DD
    totalSeconds: number;
    sessions: number;
    songsCount: number;
}

export interface PracticeGoal {
    dailyMinutes: number;
    weeklyDays: number;
}

interface PracticeState {
    // Streak data
    currentStreak: number;
    longestStreak: number;
    lastPracticeDate: string | null;

    // Goal settings
    goal: PracticeGoal;

    // Today's progress
    todayPracticeSeconds: number;
    todaySessionCount: number;

    // XP & Level
    xp: number;
    level: number;

    // Session history
    sessions: PracticeSession[];
    dailyHistory: DailyPractice[];

    // Actions
    startSession: (songId?: string, songTitle?: string) => string;
    endSession: (sessionId: string, durationSeconds: number) => void;
    addPracticeTime: (seconds: number) => void;
    setGoal: (goal: Partial<PracticeGoal>) => void;
    checkStreak: () => void;

    // Computed
    getTodayProgress: () => number; // 0-100%
    getWeeklyData: () => DailyPractice[];
    getMonthlyData: () => DailyPractice[];
}

// XP per minute of practice
const XP_PER_MINUTE = 10;
// XP required per level (exponential)
const XP_PER_LEVEL = (level: number) => Math.floor(100 * Math.pow(1.5, level - 1));

function getTodayDateString(): string {
    return new Date().toISOString().split('T')[0];
}

function getDaysBetween(date1: string, date2: string): number {
    const d1 = new Date(date1);
    const d2 = new Date(date2);
    const diffTime = Math.abs(d2.getTime() - d1.getTime());
    return Math.floor(diffTime / (1000 * 60 * 60 * 24));
}

export const usePracticeStore = create<PracticeState>()(
    persist(
        (set, get) => ({
            // Initial state
            currentStreak: 0,
            longestStreak: 0,
            lastPracticeDate: null,

            goal: {
                dailyMinutes: 30,
                weeklyDays: 5,
            },

            todayPracticeSeconds: 0,
            todaySessionCount: 0,

            xp: 0,
            level: 1,

            sessions: [],
            dailyHistory: [],

            // Actions
            startSession: (songId, songTitle) => {
                const sessionId = `session-${Date.now()}`;
                const session: PracticeSession = {
                    id: sessionId,
                    songId,
                    songTitle,
                    startTime: new Date().toISOString(),
                    durationSeconds: 0,
                    tempoMultiplier: 1.0,
                };

                set((state) => ({
                    sessions: [session, ...state.sessions].slice(0, 100), // Keep last 100
                }));

                return sessionId;
            },

            endSession: (sessionId, durationSeconds) => {
                set((state) => {
                    const sessions = state.sessions.map((s) =>
                        s.id === sessionId
                            ? { ...s, endTime: new Date().toISOString(), durationSeconds }
                            : s
                    );
                    return { sessions };
                });

                // Add practice time
                get().addPracticeTime(durationSeconds);
            },

            addPracticeTime: (seconds) => {
                const today = getTodayDateString();
                const earnedXp = Math.floor((seconds / 60) * XP_PER_MINUTE);

                set((state) => {
                    // Update today's stats
                    let newTodaySeconds = state.todayPracticeSeconds;
                    let newSessionCount = state.todaySessionCount;

                    // Check if we need to reset today's stats
                    if (state.lastPracticeDate !== today) {
                        newTodaySeconds = 0;
                        newSessionCount = 0;
                    }

                    newTodaySeconds += seconds;
                    newSessionCount += 1;

                    // Update daily history
                    const dailyHistory = [...state.dailyHistory];
                    const todayIndex = dailyHistory.findIndex((d) => d.date === today);

                    if (todayIndex >= 0) {
                        dailyHistory[todayIndex] = {
                            ...dailyHistory[todayIndex],
                            totalSeconds: dailyHistory[todayIndex].totalSeconds + seconds,
                            sessions: dailyHistory[todayIndex].sessions + 1,
                        };
                    } else {
                        dailyHistory.unshift({
                            date: today,
                            totalSeconds: seconds,
                            sessions: 1,
                            songsCount: 1,
                        });
                    }

                    // Calculate new XP and level
                    let newXp = state.xp + earnedXp;
                    let newLevel = state.level;

                    while (newXp >= XP_PER_LEVEL(newLevel)) {
                        newXp -= XP_PER_LEVEL(newLevel);
                        newLevel++;
                    }

                    // Update streak
                    let currentStreak = state.currentStreak;
                    let longestStreak = state.longestStreak;

                    if (state.lastPracticeDate === null) {
                        currentStreak = 1;
                    } else if (state.lastPracticeDate !== today) {
                        const daysSince = getDaysBetween(state.lastPracticeDate, today);
                        if (daysSince === 1) {
                            currentStreak = state.currentStreak + 1;
                        } else if (daysSince > 1) {
                            currentStreak = 1; // Streak broken
                        }
                    }

                    longestStreak = Math.max(longestStreak, currentStreak);

                    return {
                        todayPracticeSeconds: newTodaySeconds,
                        todaySessionCount: newSessionCount,
                        lastPracticeDate: today,
                        currentStreak,
                        longestStreak,
                        xp: newXp,
                        level: newLevel,
                        dailyHistory: dailyHistory.slice(0, 90), // Keep 90 days
                    };
                });
            },

            setGoal: (goal) => {
                set((state) => ({
                    goal: { ...state.goal, ...goal },
                }));
            },

            checkStreak: () => {
                const today = getTodayDateString();
                const { lastPracticeDate, currentStreak } = get();

                if (lastPracticeDate && lastPracticeDate !== today) {
                    const daysSince = getDaysBetween(lastPracticeDate, today);
                    if (daysSince > 1) {
                        // Streak broken
                        set({ currentStreak: 0 });
                    }
                }
            },

            // Computed getters
            getTodayProgress: () => {
                const { todayPracticeSeconds, goal } = get();
                const goalSeconds = goal.dailyMinutes * 60;
                return Math.min(100, Math.round((todayPracticeSeconds / goalSeconds) * 100));
            },

            getWeeklyData: () => {
                const { dailyHistory } = get();
                const today = new Date();
                const weekData: DailyPractice[] = [];

                for (let i = 6; i >= 0; i--) {
                    const date = new Date(today);
                    date.setDate(date.getDate() - i);
                    const dateStr = date.toISOString().split('T')[0];

                    const existing = dailyHistory.find((d) => d.date === dateStr);
                    weekData.push(existing || { date: dateStr, totalSeconds: 0, sessions: 0, songsCount: 0 });
                }

                return weekData;
            },

            getMonthlyData: () => {
                const { dailyHistory } = get();
                const today = new Date();
                const monthData: DailyPractice[] = [];

                for (let i = 29; i >= 0; i--) {
                    const date = new Date(today);
                    date.setDate(date.getDate() - i);
                    const dateStr = date.toISOString().split('T')[0];

                    const existing = dailyHistory.find((d) => d.date === dateStr);
                    monthData.push(existing || { date: dateStr, totalSeconds: 0, sessions: 0, songsCount: 0 });
                }

                return monthData;
            },
        }),
        {
            name: 'piano-keys-practice',
            storage: createJSONStorage(() => localStorage),
            partialize: (state) => ({
                currentStreak: state.currentStreak,
                longestStreak: state.longestStreak,
                lastPracticeDate: state.lastPracticeDate,
                goal: state.goal,
                todayPracticeSeconds: state.todayPracticeSeconds,
                todaySessionCount: state.todaySessionCount,
                xp: state.xp,
                level: state.level,
                sessions: state.sessions,
                dailyHistory: state.dailyHistory,
            }),
            onRehydrateStorage: () => (state) => {
                // Check streak on load
                if (state) {
                    state.checkStreak();
                }
            },
        }
    )
);

// Utility hooks
export function useTodayProgress() {
    return usePracticeStore((state) => state.getTodayProgress());
}

export function useWeeklyData() {
    return usePracticeStore((state) => state.getWeeklyData());
}
