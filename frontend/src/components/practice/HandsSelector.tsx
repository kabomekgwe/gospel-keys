/**
 * Hands Selector Component
 * 
 * UI for selecting and controlling left/right hand practice options.
 * Features:
 * - Hand mode toggle (left/right/both)
 * - Pattern selection per hand
 * - Style selection (neosoul, gospel, jazz)
 */
import { useState, useMemo } from 'react';
import { motion } from 'framer-motion';

export type HandMode = 'left' | 'right' | 'both';
export type Style = 'neosoul' | 'gospel' | 'jazz';

export interface HandsSelectorProps {
    /** Currently selected hand mode */
    mode: HandMode;
    /** Callback when mode changes */
    onModeChange: (mode: HandMode) => void;
    /** Selected left hand pattern */
    leftPattern: string;
    /** Selected right hand pattern */
    rightPattern: string;
    /** Available left hand patterns */
    leftPatterns: string[];
    /** Available right hand patterns */
    rightPatterns: string[];
    /** Callback when pattern changes */
    onPatternChange: (hand: 'left' | 'right', pattern: string) => void;
    /** Selected style */
    style: Style;
    /** Callback when style changes */
    onStyleChange: (style: Style) => void;
    /** Whether generation is loading */
    isLoading?: boolean;
    /** Additional CSS classes */
    className?: string;
}

const HAND_MODES: { value: HandMode; label: string; icon: string }[] = [
    { value: 'left', label: 'Left Hand', icon: '🫲' },
    { value: 'both', label: 'Both Hands', icon: '🙌' },
    { value: 'right', label: 'Right Hand', icon: '🫱' },
];

const STYLES: { value: Style; label: string; description: string }[] = [
    { value: 'neosoul', label: 'Neo-Soul', description: 'D\'Angelo, Erykah Badu style' },
    { value: 'gospel', label: 'Gospel', description: 'Church style runs & shouts' },
    { value: 'jazz', label: 'Jazz', description: 'ii-V-I, comping patterns' },
];

function formatPatternName(pattern: string): string {
    return pattern
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}

export function HandsSelector({
    mode,
    onModeChange,
    leftPattern,
    rightPattern,
    leftPatterns,
    rightPatterns,
    onPatternChange,
    style,
    onStyleChange,
    isLoading = false,
    className = '',
}: HandsSelectorProps) {
    return (
        <div className={`flex flex-col gap-6 ${className}`}>
            {/* Hand Mode Toggle */}
            <div className="flex flex-col gap-2">
                <label className="text-sm font-medium text-slate-400">Practice Mode</label>
                <div className="flex gap-2 p-1 bg-slate-800/50 rounded-xl">
                    {HAND_MODES.map(({ value, label, icon }) => (
                        <motion.button
                            key={value}
                            onClick={() => onModeChange(value)}
                            className={`
                flex-1 flex items-center justify-center gap-2 py-3 px-4 rounded-lg
                text-sm font-medium transition-colors
                ${mode === value
                                    ? 'bg-gradient-to-r from-violet-600 to-indigo-600 text-white shadow-lg shadow-violet-500/25'
                                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-700/50'
                                }
              `}
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                            disabled={isLoading}
                        >
                            <span className="text-xl">{icon}</span>
                            <span className="hidden sm:inline">{label}</span>
                        </motion.button>
                    ))}
                </div>
            </div>

            {/* Style Selection */}
            <div className="flex flex-col gap-2">
                <label className="text-sm font-medium text-slate-400">Style</label>
                <div className="grid grid-cols-3 gap-2">
                    {STYLES.map(({ value, label, description }) => (
                        <motion.button
                            key={value}
                            onClick={() => onStyleChange(value)}
                            className={`
                flex flex-col items-start p-3 rounded-lg border
                text-left transition-colors
                ${style === value
                                    ? 'bg-slate-700/50 border-violet-500/50 ring-1 ring-violet-500/30'
                                    : 'bg-slate-800/30 border-slate-700/50 hover:bg-slate-700/30'
                                }
              `}
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                            disabled={isLoading}
                        >
                            <span className={`font-medium ${style === value ? 'text-violet-300' : 'text-slate-200'}`}>
                                {label}
                            </span>
                            <span className="text-xs text-slate-500 mt-0.5 line-clamp-1">
                                {description}
                            </span>
                        </motion.button>
                    ))}
                </div>
            </div>

            {/* Pattern Selection */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Left Hand Pattern */}
                {(mode === 'left' || mode === 'both') && (
                    <div className="flex flex-col gap-2">
                        <label className="flex items-center gap-2 text-sm font-medium text-blue-400">
                            <div className="w-3 h-3 rounded bg-blue-500" />
                            Left Hand Pattern
                        </label>
                        <select
                            value={leftPattern}
                            onChange={(e) => onPatternChange('left', e.target.value)}
                            className="
                w-full px-3 py-2.5 rounded-lg
                bg-slate-800 border border-slate-700
                text-slate-200 text-sm
                focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500
              "
                            disabled={isLoading}
                        >
                            {leftPatterns.map(pattern => (
                                <option key={pattern} value={pattern}>
                                    {formatPatternName(pattern)}
                                </option>
                            ))}
                        </select>
                    </div>
                )}

                {/* Right Hand Pattern */}
                {(mode === 'right' || mode === 'both') && (
                    <div className="flex flex-col gap-2">
                        <label className="flex items-center gap-2 text-sm font-medium text-green-400">
                            <div className="w-3 h-3 rounded bg-green-500" />
                            Right Hand Pattern
                        </label>
                        <select
                            value={rightPattern}
                            onChange={(e) => onPatternChange('right', e.target.value)}
                            className="
                w-full px-3 py-2.5 rounded-lg
                bg-slate-800 border border-slate-700
                text-slate-200 text-sm
                focus:outline-none focus:ring-2 focus:ring-green-500/50 focus:border-green-500
              "
                            disabled={isLoading}
                        >
                            {rightPatterns.map(pattern => (
                                <option key={pattern} value={pattern}>
                                    {formatPatternName(pattern)}
                                </option>
                            ))}
                        </select>
                    </div>
                )}
            </div>
        </div>
    );
}

// Compact inline version for toolbar
export function HandsModeToggle({
    mode,
    onModeChange,
    className = '',
}: Pick<HandsSelectorProps, 'mode' | 'onModeChange' | 'className'>) {
    return (
        <div className={`inline-flex gap-1 p-0.5 bg-slate-800/50 rounded-lg ${className}`}>
            {HAND_MODES.map(({ value, icon }) => (
                <button
                    key={value}
                    onClick={() => onModeChange(value)}
                    className={`
            p-2 rounded-md text-lg transition-colors
            ${mode === value
                            ? 'bg-slate-700 shadow'
                            : 'hover:bg-slate-700/50'
                        }
          `}
                    title={HAND_MODES.find(m => m.value === value)?.label}
                >
                    {icon}
                </button>
            ))}
        </div>
    );
}
