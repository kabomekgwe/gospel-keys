/**
 * Practice Components Tests
 */
import { describe, it, expect, beforeEach } from 'vitest';
import { screen } from '@testing-library/react';
import { render } from '../../test/utils';
import { StreakCounter } from './StreakCounter';
import { PracticeGoals } from './PracticeGoals';
import { PracticeStats } from './PracticeStats';
import { usePracticeStore } from '../../lib/practiceStore';

describe('Practice Components', () => {
    beforeEach(() => {
        // Reset practice store
        usePracticeStore.setState({
            currentStreak: 5,
            longestStreak: 10,
            xp: 500,
            level: 3,
            todayPracticeSeconds: 1200, // 20 minutes
            goal: {
                dailyMinutes: 30,
                daysPerWeek: 5,
            },
            sessions: [],
            dailyHistory: [],
        });
    });

    describe('StreakCounter', () => {
        it('renders current streak', () => {
            render(<StreakCounter />);
            expect(screen.getByText('5')).toBeInTheDocument();
        });

        it('shows day suffix', () => {
            render(<StreakCounter />);
            expect(screen.getByText(/day streak/i)).toBeInTheDocument();
        });

        it('shows longest streak when showDetails is true', () => {
            render(<StreakCounter showDetails />);
            expect(screen.getByText(/longest/i)).toBeInTheDocument();
            expect(screen.getByText('10')).toBeInTheDocument();
        });
    });

    describe('PracticeGoals', () => {
        it('renders progress ring', () => {
            render(<PracticeGoals />);
            // Component should render without errors
            expect(document.querySelector('svg')).toBeInTheDocument();
        });

        it('shows daily goal info', () => {
            render(<PracticeGoals />);
            expect(screen.getByText(/30/)).toBeInTheDocument(); // Goal minutes
        });
    });

    describe('PracticeStats', () => {
        it('renders level', () => {
            render(<PracticeStats />);
            expect(screen.getByText('Level')).toBeInTheDocument();
            expect(screen.getByText('3')).toBeInTheDocument();
        });

        it('renders practice time', () => {
            render(<PracticeStats />);
            expect(screen.getByText('Practice Time')).toBeInTheDocument();
        });

        it('renders sessions count', () => {
            render(<PracticeStats />);
            expect(screen.getByText('Sessions')).toBeInTheDocument();
        });

        it('renders songs practiced', () => {
            render(<PracticeStats />);
            expect(screen.getByText('Songs Practiced')).toBeInTheDocument();
        });

        it('supports grid layout', () => {
            const { container } = render(<PracticeStats layout="grid" />);
            expect(container.querySelector('.grid')).toBeInTheDocument();
        });

        it('supports horizontal layout', () => {
            const { container } = render(<PracticeStats layout="horizontal" />);
            expect(container.querySelector('.flex')).toBeInTheDocument();
        });
    });
});
