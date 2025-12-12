/**
 * Circle of Fifths Interactive Component
 * 
 * SVG-based interactive circle of fifths visualization
 */
import { useState } from 'react';
import { motion } from 'framer-motion';

interface CircleOfFifthsProps {
    onSelectKey?: (key: string, isMinor: boolean) => void;
    selectedKey?: string;
    showMinors?: boolean;
}

const MAJOR_KEYS = ['C', 'G', 'D', 'A', 'E', 'B', 'F#', 'Db', 'Ab', 'Eb', 'Bb', 'F'];
const MINOR_KEYS = ['Am', 'Em', 'Bm', 'F#m', 'C#m', 'G#m', 'D#m', 'Bbm', 'Fm', 'Cm', 'Gm', 'Dm'];

export function CircleOfFifths({
    onSelectKey,
    selectedKey = 'C',
    showMinors = true
}: CircleOfFifthsProps) {
    const [hoveredKey, setHoveredKey] = useState<string | null>(null);

    const size = 400;
    const center = size / 2;
    const outerRadius = 180;
    const innerRadius = 120;
    const minorRadius = 80;

    // Calculate position for each key
    const getPosition = (index: number, radius: number) => {
        const angle = (index * 30 - 90) * (Math.PI / 180); // Start from top (12 o'clock)
        return {
            x: center + Math.cos(angle) * radius,
            y: center + Math.sin(angle) * radius,
        };
    };

    const getArcPath = (startAngle: number, endAngle: number, innerR: number, outerR: number) => {
        const startOuter = {
            x: center + Math.cos(startAngle) * outerR,
            y: center + Math.sin(startAngle) * outerR,
        };
        const endOuter = {
            x: center + Math.cos(endAngle) * outerR,
            y: center + Math.sin(endAngle) * outerR,
        };
        const startInner = {
            x: center + Math.cos(endAngle) * innerR,
            y: center + Math.sin(endAngle) * innerR,
        };
        const endInner = {
            x: center + Math.cos(startAngle) * innerR,
            y: center + Math.sin(startAngle) * innerR,
        };

        return `
      M ${startOuter.x} ${startOuter.y}
      A ${outerR} ${outerR} 0 0 1 ${endOuter.x} ${endOuter.y}
      L ${startInner.x} ${startInner.y}
      A ${innerR} ${innerR} 0 0 0 ${endInner.x} ${endInner.y}
      Z
    `;
    };

    return (
        <div className="flex flex-col items-center">
            <svg width={size} height={size} className="overflow-visible">
                {/* Outer ring - Major keys */}
                {MAJOR_KEYS.map((key, i) => {
                    const startAngle = ((i * 30 - 15 - 90) * Math.PI) / 180;
                    const endAngle = ((i * 30 + 15 - 90) * Math.PI) / 180;
                    const isSelected = selectedKey === key;
                    const isHovered = hoveredKey === key;
                    const labelPos = getPosition(i, (outerRadius + innerRadius) / 2);

                    return (
                        <g key={key}>
                            <motion.path
                                d={getArcPath(startAngle, endAngle, innerRadius, outerRadius)}
                                fill={isSelected ? '#06b6d4' : isHovered ? '#334155' : '#1e293b'}
                                stroke="#475569"
                                strokeWidth={1}
                                onClick={() => onSelectKey?.(key, false)}
                                onMouseEnter={() => setHoveredKey(key)}
                                onMouseLeave={() => setHoveredKey(null)}
                                style={{ cursor: 'pointer' }}
                                whileHover={{ scale: 1.02 }}
                                transition={{ duration: 0.1 }}
                            />
                            <text
                                x={labelPos.x}
                                y={labelPos.y}
                                textAnchor="middle"
                                dominantBaseline="central"
                                fill={isSelected ? 'white' : '#94a3b8'}
                                fontSize={16}
                                fontWeight={isSelected ? 'bold' : 'normal'}
                                style={{ pointerEvents: 'none' }}
                            >
                                {key}
                            </text>
                        </g>
                    );
                })}

                {/* Inner ring - Minor keys */}
                {showMinors && MINOR_KEYS.map((key, i) => {
                    const startAngle = ((i * 30 - 15 - 90) * Math.PI) / 180;
                    const endAngle = ((i * 30 + 15 - 90) * Math.PI) / 180;
                    const isSelected = selectedKey === key;
                    const isHovered = hoveredKey === key;
                    const labelPos = getPosition(i, (innerRadius + minorRadius) / 2);

                    return (
                        <g key={key}>
                            <motion.path
                                d={getArcPath(startAngle, endAngle, minorRadius, innerRadius)}
                                fill={isSelected ? '#8b5cf6' : isHovered ? '#334155' : '#0f172a'}
                                stroke="#334155"
                                strokeWidth={1}
                                onClick={() => onSelectKey?.(key.replace('m', ''), true)}
                                onMouseEnter={() => setHoveredKey(key)}
                                onMouseLeave={() => setHoveredKey(null)}
                                style={{ cursor: 'pointer' }}
                                whileHover={{ scale: 1.02 }}
                                transition={{ duration: 0.1 }}
                            />
                            <text
                                x={labelPos.x}
                                y={labelPos.y}
                                textAnchor="middle"
                                dominantBaseline="central"
                                fill={isSelected ? 'white' : '#64748b'}
                                fontSize={12}
                                fontWeight={isSelected ? 'bold' : 'normal'}
                                style={{ pointerEvents: 'none' }}
                            >
                                {key}
                            </text>
                        </g>
                    );
                })}

                {/* Center circle */}
                <circle
                    cx={center}
                    cy={center}
                    r={minorRadius}
                    fill="#0f172a"
                    stroke="#334155"
                    strokeWidth={1}
                />
                <text
                    x={center}
                    y={center - 10}
                    textAnchor="middle"
                    fill="#94a3b8"
                    fontSize={14}
                    fontWeight="bold"
                >
                    Circle of
                </text>
                <text
                    x={center}
                    y={center + 10}
                    textAnchor="middle"
                    fill="#94a3b8"
                    fontSize={14}
                    fontWeight="bold"
                >
                    Fifths
                </text>
            </svg>

            {/* Legend */}
            <div className="flex items-center gap-6 mt-4">
                <div className="flex items-center gap-2">
                    <div className="w-4 h-4 rounded bg-cyan-500" />
                    <span className="text-sm text-slate-400">Major</span>
                </div>
                {showMinors && (
                    <div className="flex items-center gap-2">
                        <div className="w-4 h-4 rounded bg-violet-500" />
                        <span className="text-sm text-slate-400">Minor</span>
                    </div>
                )}
            </div>
        </div>
    );
}
