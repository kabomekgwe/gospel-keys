/**
 * Session History Chart Component
 * 
 * Displays practice history as bar/line charts and calendar heatmap
 */
// Chart component
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts';
import { Calendar, BarChart2, TrendingUp } from 'lucide-react';
import { useState } from 'react';
import { usePracticeStore } from '../../lib/practiceStore';

type ViewMode = 'bar' | 'line' | 'heatmap';
type TimeRange = 'week' | 'month';

interface SessionHistoryChartProps {
    defaultView?: ViewMode;
    defaultRange?: TimeRange;
}

export function SessionHistoryChart({
    defaultView = 'bar',
    defaultRange = 'week'
}: SessionHistoryChartProps) {
    const { getWeeklyData, getMonthlyData } = usePracticeStore();
    const [view, setView] = useState<ViewMode>(defaultView);
    const [range, setRange] = useState<TimeRange>(defaultRange);

    const data = range === 'week' ? getWeeklyData() : getMonthlyData();

    // Format data for charts
    const chartData = data.map((d) => ({
        date: d.date,
        day: new Date(d.date).toLocaleDateString('en-US', { weekday: 'short' }),
        dateLabel: new Date(d.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
        minutes: Math.round(d.totalSeconds / 60),
        sessions: d.sessions,
    }));

    const CustomTooltip = ({ active, payload }: any) => {
        if (active && payload && payload.length) {
            const data = payload[0].payload;
            return (
                <div className="bg-slate-800 border border-slate-700 rounded-lg p-3 shadow-xl">
                    <p className="text-white font-medium">{data.dateLabel}</p>
                    <p className="text-cyan-400">{data.minutes} minutes</p>
                    <p className="text-slate-400 text-sm">{data.sessions} sessions</p>
                </div>
            );
        }
        return null;
    };

    return (
        <div className="card p-6">
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                    <Calendar className="w-5 h-5 text-cyan-400" />
                    Practice History
                </h3>

                <div className="flex items-center gap-2">
                    {/* Time Range Toggle */}
                    <div className="flex bg-slate-800 rounded-lg p-1">
                        <button
                            onClick={() => setRange('week')}
                            className={`px-3 py-1 rounded text-sm font-medium transition-colors ${range === 'week' ? 'bg-slate-700 text-white' : 'text-slate-400'
                                }`}
                        >
                            Week
                        </button>
                        <button
                            onClick={() => setRange('month')}
                            className={`px-3 py-1 rounded text-sm font-medium transition-colors ${range === 'month' ? 'bg-slate-700 text-white' : 'text-slate-400'
                                }`}
                        >
                            Month
                        </button>
                    </div>

                    {/* View Toggle */}
                    <div className="flex bg-slate-800 rounded-lg p-1">
                        <button
                            onClick={() => setView('bar')}
                            className={`p-1.5 rounded transition-colors ${view === 'bar' ? 'bg-slate-700 text-white' : 'text-slate-400'
                                }`}
                        >
                            <BarChart2 className="w-4 h-4" />
                        </button>
                        <button
                            onClick={() => setView('line')}
                            className={`p-1.5 rounded transition-colors ${view === 'line' ? 'bg-slate-700 text-white' : 'text-slate-400'
                                }`}
                        >
                            <TrendingUp className="w-4 h-4" />
                        </button>
                    </div>
                </div>
            </div>

            {/* Chart */}
            <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                    {view === 'bar' ? (
                        <BarChart data={chartData}>
                            <XAxis
                                dataKey={range === 'week' ? 'day' : 'dateLabel'}
                                axisLine={false}
                                tickLine={false}
                                tick={{ fill: '#64748b', fontSize: 12 }}
                            />
                            <YAxis
                                axisLine={false}
                                tickLine={false}
                                tick={{ fill: '#64748b', fontSize: 12 }}
                                width={40}
                            />
                            <Tooltip content={<CustomTooltip />} />
                            <Bar
                                dataKey="minutes"
                                fill="url(#barGradient)"
                                radius={[4, 4, 0, 0]}
                            />
                            <defs>
                                <linearGradient id="barGradient" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="0%" stopColor="#06b6d4" />
                                    <stop offset="100%" stopColor="#0891b2" />
                                </linearGradient>
                            </defs>
                        </BarChart>
                    ) : (
                        <LineChart data={chartData}>
                            <XAxis
                                dataKey={range === 'week' ? 'day' : 'dateLabel'}
                                axisLine={false}
                                tickLine={false}
                                tick={{ fill: '#64748b', fontSize: 12 }}
                            />
                            <YAxis
                                axisLine={false}
                                tickLine={false}
                                tick={{ fill: '#64748b', fontSize: 12 }}
                                width={40}
                            />
                            <Tooltip content={<CustomTooltip />} />
                            <Line
                                type="monotone"
                                dataKey="minutes"
                                stroke="#06b6d4"
                                strokeWidth={2}
                                dot={{ fill: '#06b6d4', strokeWidth: 0, r: 4 }}
                                activeDot={{ r: 6, fill: '#06b6d4' }}
                            />
                        </LineChart>
                    )}
                </ResponsiveContainer>
            </div>

            {/* Summary */}
            <div className="mt-4 pt-4 border-t border-slate-700/50 flex items-center justify-between text-sm">
                <span className="text-slate-400">
                    Total: {chartData.reduce((acc, d) => acc + d.minutes, 0)} minutes
                </span>
                <span className="text-slate-400">
                    Avg: {Math.round(chartData.reduce((acc, d) => acc + d.minutes, 0) / chartData.length || 0)} min/day
                </span>
            </div>
        </div>
    );
}
