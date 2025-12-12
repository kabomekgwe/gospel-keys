/**
 * Tension Curve Component
 * 
 * SVG line chart showing harmonic tension over time with:
 * - Tension level visualization
 * - Climax point markers
 * - Cadence annotations
 * - Interactive hover tooltips
 */
import { useMemo, useState } from 'react';
import { motion } from 'framer-motion';
import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    ReferenceLine,
    ReferenceDot,
    Area,
    ComposedChart,
} from 'recharts';

export interface TensionPoint {
    time: number;
    tension: number;  // 0-1 normalized
    chord?: string;
    event?: 'cadence' | 'climax' | 'resolution' | 'buildup';
    eventLabel?: string;
}

export interface TensionCurveProps {
    data: TensionPoint[];
    duration: number;
    currentTime?: number;
    onSeek?: (time: number) => void;
    showEvents?: boolean;
    arcType?: 'ascending' | 'descending' | 'arch' | 'wave' | 'plateau' | 'unknown';
}

// Custom tooltip component
function CustomTooltip({ active, payload, label }: any) {
    if (active && payload && payload.length) {
        const point = payload[0].payload as TensionPoint;
        return (
            <div className="bg-slate-800/95 backdrop-blur-sm border border-slate-700 rounded-lg p-3 shadow-xl">
                <p className="text-xs text-slate-400 mb-1">
                    {formatTime(point.time)}
                </p>
                <p className="text-sm font-medium text-white">
                    Tension: {Math.round(point.tension * 100)}%
                </p>
                {point.chord && (
                    <p className="text-sm text-cyan-400 mt-1">{point.chord}</p>
                )}
                {point.eventLabel && (
                    <p className="text-xs text-violet-400 mt-1">{point.eventLabel}</p>
                )}
            </div>
        );
    }
    return null;
}

function formatTime(seconds: number): string {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

// Event marker colors
const EVENT_COLORS = {
    cadence: '#10b981',     // Emerald
    climax: '#f97316',      // Orange
    resolution: '#06b6d4',  // Cyan
    buildup: '#8b5cf6',     // Violet
};

export function TensionCurve({
    data,
    duration,
    currentTime = 0,
    onSeek,
    showEvents = true,
    arcType = 'unknown',
}: TensionCurveProps) {
    const [hoveredPoint, setHoveredPoint] = useState<TensionPoint | null>(null);

    // Find events for markers
    const events = useMemo(() => {
        return data.filter(d => d.event);
    }, [data]);

    // Calculate arc description
    const arcDescription = useMemo(() => {
        switch (arcType) {
            case 'ascending':
                return 'Building tension throughout';
            case 'descending':
                return 'Tension release arc';
            case 'arch':
                return 'Classic tension-resolution arc';
            case 'wave':
                return 'Multiple tension peaks';
            case 'plateau':
                return 'Sustained tension level';
            default:
                return 'Complex tension pattern';
        }
    }, [arcType]);

    // Find current tension
    const currentTension = useMemo(() => {
        if (data.length === 0) return 0;

        // Find the nearest point
        let nearest = data[0];
        let minDiff = Math.abs(data[0].time - currentTime);

        for (const point of data) {
            const diff = Math.abs(point.time - currentTime);
            if (diff < minDiff) {
                minDiff = diff;
                nearest = point;
            }
        }

        return nearest.tension;
    }, [data, currentTime]);

    const handleChartClick = (e: any) => {
        if (e && e.activePayload && e.activePayload[0] && onSeek) {
            onSeek(e.activePayload[0].payload.time);
        }
    };

    return (
        <div className="space-y-4">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h3 className="text-lg font-semibold text-white">Tension Curve</h3>
                    <p className="text-sm text-slate-400">{arcDescription}</p>
                </div>

                {/* Current tension indicator */}
                <div className="flex items-center gap-3">
                    <span className="text-sm text-slate-400">Current:</span>
                    <div className="relative w-32 h-3 bg-slate-700 rounded-full overflow-hidden">
                        <motion.div
                            className="absolute inset-y-0 left-0 bg-gradient-to-r from-cyan-500 to-violet-500 rounded-full"
                            animate={{ width: `${currentTension * 100}%` }}
                            transition={{ type: 'spring', stiffness: 100 }}
                        />
                    </div>
                    <span className="text-sm font-mono text-white w-10 text-right">
                        {Math.round(currentTension * 100)}%
                    </span>
                </div>
            </div>

            {/* Chart */}
            <div className="h-48 bg-slate-800/30 rounded-xl p-4">
                <ResponsiveContainer width="100%" height="100%">
                    <ComposedChart
                        data={data}
                        onClick={handleChartClick}
                        margin={{ top: 10, right: 10, left: 0, bottom: 0 }}
                    >
                        <defs>
                            <linearGradient id="tensionGradient" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.4} />
                                <stop offset="95%" stopColor="#06b6d4" stopOpacity={0} />
                            </linearGradient>
                        </defs>

                        <CartesianGrid strokeDasharray="3 3" stroke="#334155" />

                        <XAxis
                            dataKey="time"
                            tickFormatter={formatTime}
                            stroke="#64748b"
                            fontSize={11}
                            tickLine={false}
                        />

                        <YAxis
                            domain={[0, 1]}
                            tickFormatter={(v) => `${Math.round(v * 100)}%`}
                            stroke="#64748b"
                            fontSize={11}
                            tickLine={false}
                            width={40}
                        />

                        <Tooltip content={<CustomTooltip />} />

                        {/* Tension area fill */}
                        <Area
                            type="monotone"
                            dataKey="tension"
                            stroke="none"
                            fill="url(#tensionGradient)"
                        />

                        {/* Main tension line */}
                        <Line
                            type="monotone"
                            dataKey="tension"
                            stroke="#06b6d4"
                            strokeWidth={2}
                            dot={false}
                            activeDot={{
                                r: 6,
                                fill: '#06b6d4',
                                stroke: '#0f172a',
                                strokeWidth: 2,
                            }}
                        />

                        {/* Current position line */}
                        <ReferenceLine
                            x={currentTime}
                            stroke="#f97316"
                            strokeWidth={2}
                            strokeDasharray="4 4"
                        />

                        {/* Event markers */}
                        {showEvents && events.map((event, i) => (
                            <ReferenceDot
                                key={i}
                                x={event.time}
                                y={event.tension}
                                r={6}
                                fill={EVENT_COLORS[event.event!]}
                                stroke="#0f172a"
                                strokeWidth={2}
                            />
                        ))}
                    </ComposedChart>
                </ResponsiveContainer>
            </div>

            {/* Event legend */}
            {showEvents && events.length > 0 && (
                <div className="flex flex-wrap items-center gap-4 text-xs">
                    {events.some(e => e.event === 'climax') && (
                        <span className="flex items-center gap-1.5">
                            <span className="w-3 h-3 rounded-full" style={{ backgroundColor: EVENT_COLORS.climax }} />
                            Climax
                        </span>
                    )}
                    {events.some(e => e.event === 'cadence') && (
                        <span className="flex items-center gap-1.5">
                            <span className="w-3 h-3 rounded-full" style={{ backgroundColor: EVENT_COLORS.cadence }} />
                            Cadence
                        </span>
                    )}
                    {events.some(e => e.event === 'resolution') && (
                        <span className="flex items-center gap-1.5">
                            <span className="w-3 h-3 rounded-full" style={{ backgroundColor: EVENT_COLORS.resolution }} />
                            Resolution
                        </span>
                    )}
                    {events.some(e => e.event === 'buildup') && (
                        <span className="flex items-center gap-1.5">
                            <span className="w-3 h-3 rounded-full" style={{ backgroundColor: EVENT_COLORS.buildup }} />
                            Buildup
                        </span>
                    )}
                </div>
            )}
        </div>
    );
}

// Mini tension indicator (for song cards, etc.)
export function TensionMini({ tension }: { tension: number }) {
    return (
        <div className="flex items-center gap-2">
            <div className="w-16 h-1.5 bg-slate-700 rounded-full overflow-hidden">
                <div
                    className="h-full bg-gradient-to-r from-cyan-500 to-violet-500 rounded-full"
                    style={{ width: `${tension * 100}%` }}
                />
            </div>
            <span className="text-xs text-slate-400">{Math.round(tension * 100)}%</span>
        </div>
    );
}
