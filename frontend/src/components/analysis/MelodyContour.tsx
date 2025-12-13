import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    ReferenceArea
} from 'recharts';
import type { PitchAnalysisResult } from '../../lib/api';

interface MelodyContourProps {
    analysis: PitchAnalysisResult;
}

export function MelodyContour({ analysis }: MelodyContourProps) {
    // Transform data: Sample down if too many points to improve performance
    const step = Math.max(1, Math.floor(analysis.pitch_contour.time.length / 500)); // Max ~500 points

    const data = analysis.pitch_contour.time
        .map((time, i) => ({
            time: parseFloat(time.toFixed(2)),
            frequency: analysis.pitch_contour.frequency[i],
            confidence: analysis.pitch_contour.confidence[i],
            note: analysis.pitch_contour.notes[i]
        }))
        .filter((_, i) => i % step === 0 && _.confidence > 0.6); // Filter low confidence

    return (
        <div className="w-full h-[300px] relative">
            <ResponsiveContainer width="100%" height="100%">
                <LineChart data={data} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis
                        dataKey="time"
                        stroke="#94a3b8"
                        tickFormatter={(val) => `${val}s`}
                    />
                    <YAxis
                        stroke="#94a3b8"
                        label={{ value: 'Hz', angle: -90, position: 'insideLeft', fill: '#94a3b8' }}
                        domain={['auto', 'auto']}
                    />
                    <Tooltip
                        contentStyle={{
                            backgroundColor: '#1e293b',
                            borderColor: '#334155',
                            color: '#f8fafc'
                        }}
                        labelFormatter={(label) => `Time: ${label}s`}
                    />

                    {/* Highlight Vibrato Regions if available */}
                    {analysis.vibrato_regions?.map((region: any, i: number) => (
                        <ReferenceArea
                            key={`vibrato-${i}`}
                            x1={region.start}
                            x2={region.end}
                            fill="#8b5cf6"
                            fillOpacity={0.1}
                        />
                    ))}

                    <Line
                        type="monotone"
                        dataKey="frequency"
                        stroke="#10b981"
                        strokeWidth={2}
                        dot={false}
                        activeDot={{ r: 4 }}
                    />
                </LineChart>
            </ResponsiveContainer>

            {data.length === 0 && (
                <div className="absolute inset-0 flex items-center justify-center text-slate-500">
                    No clear melody detected (low confidence)
                </div>
            )}
        </div>
    );
}
