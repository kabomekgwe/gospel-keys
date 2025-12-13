import {
    Radar,
    RadarChart,
    PolarGrid,
    PolarAngleAxis,
    PolarRadiusAxis,
    ResponsiveContainer,
    Tooltip
} from 'recharts';
import { motion } from 'framer-motion';
import type { GenreAnalysis } from '../../lib/api';

interface GenreRadarProps {
    analysis: GenreAnalysis;
}

export function GenreRadar({ analysis }: GenreRadarProps) {
    // Transform data for Recharts
    // If we have detailed probabilities, use them. Otherwise, synthesize a simple view.
    const data = analysis.all_probabilities
        ? Object.entries(analysis.all_probabilities).map(([genre, score]) => ({
            genre: genre.charAt(0).toUpperCase() + genre.slice(1),
            score: score * 100,
            fullMark: 100,
        }))
        : [
            { genre: analysis.primary_genre, score: 100, fullMark: 100 },
            // Add other dummy axes to make it look like a radar
            { genre: 'Other', score: 20, fullMark: 100 },
            { genre: 'Jazz', score: 0, fullMark: 100 },
            { genre: 'Classical', score: 0, fullMark: 100 },
            { genre: 'Pop', score: 0, fullMark: 100 },
        ];

    // Normalize keys if using synthesized data to avoid duplicates or verify logic
    // But simplified logic: if we have probabilities, we trust them (usually covers all 5 genres)

    return (
        <div className="w-full h-[300px] relative">
            <ResponsiveContainer width="100%" height="100%">
                <RadarChart cx="50%" cy="50%" outerRadius="80%" data={data}>
                    <PolarGrid stroke="#334155" />
                    <PolarAngleAxis
                        dataKey="genre"
                        tick={{ fill: '#94a3b8', fontSize: 12 }}
                    />
                    <PolarRadiusAxis
                        angle={30}
                        domain={[0, 100]}
                        tick={false}
                        axisLine={false}
                    />
                    <Radar
                        name="Genre Match"
                        dataKey="score"
                        stroke="#06b6d4" // cyan-500
                        strokeWidth={2}
                        fill="#06b6d4"
                        fillOpacity={0.3}
                    />
                    <Tooltip
                        contentStyle={{
                            backgroundColor: '#1e293b',
                            borderColor: '#334155',
                            color: '#f8fafc'
                        }}
                        itemStyle={{ color: '#06b6d4' }}
                        formatter={(value: number) => [`${value.toFixed(1)}%`, 'Match']}
                    />
                </RadarChart>
            </ResponsiveContainer>

            {/* Overlay stats */}
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="absolute top-0 right-0 p-4 text-right"
            >
                <div className="text-sm text-slate-400">Complexity</div>
                <div className="text-2xl font-bold text-white">
                    {analysis.harmonic_complexity_score?.toFixed(1) || 'N/A'}
                </div>
            </motion.div>
        </div>
    );
}
