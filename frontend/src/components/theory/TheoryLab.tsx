/**
 * Theory Lab Component
 *
 * Interactive exploration of advanced music theory concepts:
 * - Neo-Riemannian transformations (PLR)
 * - Negative harmony
 * - Chord substitutions
 * - Coltrane Changes
 * - Barry Harris diminished system
 */

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Atom, Sparkles, Shuffle, TrendingUp, Music, Bot } from 'lucide-react';
import { TonnetzLattice } from './TonnetzLattice';
import { NegativeHarmonyPanel } from './NegativeHarmonyPanel';
import { SubstitutionExplorer } from './SubstitutionExplorer';
import { ColtraneChangesVisualizer } from './ColtraneChangesVisualizer';
import { AITheoryCoach } from './AITheoryCoach';

type TabType = 'neo-riemannian' | 'negative-harmony' | 'substitutions' | 'coltrane' | 'barry-harris' | 'ai-coach';

interface TheoryLabProps {
    initialTab?: TabType;
}

const TABS = [
    {
        id: 'ai-coach' as const,
        name: 'AI Coach',
        icon: Bot,
        description: 'Ask theory questions, get instant answers',
        color: 'from-violet-500 to-purple-500'
    },
    {
        id: 'neo-riemannian' as const,
        name: 'Neo-Riemannian',
        icon: Atom,
        description: 'PLR transformations & Tonnetz lattice',
        color: 'from-blue-500 to-cyan-500'
    },
    {
        id: 'negative-harmony' as const,
        name: 'Negative Harmony',
        icon: Sparkles,
        description: 'Mirror-image harmonic relationships',
        color: 'from-purple-500 to-pink-500'
    },
    {
        id: 'substitutions' as const,
        name: 'Substitutions',
        icon: Shuffle,
        description: 'Explore chord substitution options',
        color: 'from-green-500 to-emerald-500'
    },
    {
        id: 'coltrane' as const,
        name: 'Coltrane Changes',
        icon: TrendingUp,
        description: 'Giant Steps harmonic patterns',
        color: 'from-orange-500 to-red-500'
    },
    {
        id: 'barry-harris' as const,
        name: 'Barry Harris',
        icon: Music,
        description: '6th-diminished scale system',
        color: 'from-indigo-500 to-purple-500'
    }
];

export function TheoryLab({ initialTab = 'neo-riemannian' }: TheoryLabProps) {
    const [activeTab, setActiveTab] = useState<TabType>(initialTab);

    const activeTabData = TABS.find(tab => tab.id === activeTab);

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
            {/* Header */}
            <div className="bg-gray-800/50 backdrop-blur-sm border-b border-gray-700">
                <div className="max-w-7xl mx-auto px-6 py-6">
                    <div className="flex items-center justify-between">
                        <div>
                            <h1 className="text-3xl font-bold text-white mb-2">
                                🧪 Theory Lab
                            </h1>
                            <p className="text-gray-400">
                                Explore advanced music theory concepts with interactive tools
                            </p>
                        </div>

                        {/* Status Badge */}
                        <div className="px-4 py-2 bg-green-500/10 border border-green-500/30 rounded-lg">
                            <div className="flex items-center gap-2">
                                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                                <span className="text-sm text-green-400">AI Powered</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Tab Navigation */}
            <div className="bg-gray-800/30 backdrop-blur-sm border-b border-gray-700">
                <div className="max-w-7xl mx-auto px-6">
                    <div className="flex gap-1 overflow-x-auto">
                        {TABS.map((tab) => {
                            const Icon = tab.icon;
                            const isActive = activeTab === tab.id;

                            return (
                                <button
                                    key={tab.id}
                                    onClick={() => setActiveTab(tab.id)}
                                    className={`
                                        relative px-6 py-4 whitespace-nowrap transition-all
                                        ${isActive
                                            ? 'text-white'
                                            : 'text-gray-400 hover:text-gray-300'
                                        }
                                    `}
                                >
                                    <div className="flex items-center gap-2">
                                        <Icon className="w-5 h-5" />
                                        <div className="text-left">
                                            <div className="font-medium">{tab.name}</div>
                                            <div className="text-xs text-gray-500">{tab.description}</div>
                                        </div>
                                    </div>

                                    {/* Active indicator */}
                                    {isActive && (
                                        <motion.div
                                            layoutId="activeTab"
                                            className={`
                                                absolute bottom-0 left-0 right-0 h-1
                                                bg-gradient-to-r ${tab.color}
                                            `}
                                            initial={false}
                                            transition={{ type: 'spring', stiffness: 500, damping: 30 }}
                                        />
                                    )}
                                </button>
                            );
                        })}
                    </div>
                </div>
            </div>

            {/* Tab Content */}
            <div className="max-w-7xl mx-auto px-6 py-8">
                <motion.div
                    key={activeTab}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    transition={{ duration: 0.3 }}
                >
                    {/* Header for current tab */}
                    {activeTabData && (
                        <div className="mb-8">
                            <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r ${activeTabData.color} bg-opacity-10`}>
                                <activeTabData.icon className="w-5 h-5" />
                                <h2 className="text-xl font-semibold text-white">
                                    {activeTabData.name}
                                </h2>
                            </div>
                            <p className="text-gray-400 mt-2">{activeTabData.description}</p>
                        </div>
                    )}

                    {/* Tab Panels */}
                    {activeTab === 'ai-coach' && (
                        <AITheoryCoach studentLevel="intermediate" />
                    )}

                    {activeTab === 'neo-riemannian' && (
                        <TonnetzLattice />
                    )}

                    {activeTab === 'negative-harmony' && (
                        <NegativeHarmonyPanel />
                    )}

                    {activeTab === 'substitutions' && (
                        <SubstitutionExplorer />
                    )}

                    {activeTab === 'coltrane' && (
                        <ColtraneChangesVisualizer />
                    )}

                    {activeTab === 'barry-harris' && (
                        <div className="bg-gray-800/50 rounded-xl border border-gray-700 p-8 text-center">
                            <Music className="w-16 h-16 mx-auto mb-4 text-indigo-400" />
                            <h3 className="text-xl font-semibold text-white mb-2">
                                Barry Harris Diminished System
                            </h3>
                            <p className="text-gray-400 mb-4">
                                Coming soon! Explore the 6th-diminished scale and four dominants from diminished 7th.
                            </p>
                            <div className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-500/10 border border-indigo-500/30 rounded-lg">
                                <div className="w-2 h-2 bg-indigo-500 rounded-full animate-pulse" />
                                <span className="text-sm text-indigo-400">In Development</span>
                            </div>
                        </div>
                    )}
                </motion.div>
            </div>

            {/* Info Footer */}
            <div className="max-w-7xl mx-auto px-6 py-8 border-t border-gray-700 mt-12">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="bg-gray-800/30 rounded-lg p-6">
                        <h4 className="text-white font-semibold mb-2">🎓 Learning Mode</h4>
                        <p className="text-gray-400 text-sm">
                            All explanations adapt to your skill level. Click on any transformation for detailed AI-generated explanations.
                        </p>
                    </div>
                    <div className="bg-gray-800/30 rounded-lg p-6">
                        <h4 className="text-white font-semibold mb-2">🎹 Audio Preview</h4>
                        <p className="text-gray-400 text-sm">
                            Hear each transformation with real-time MIDI synthesis. Compare voice leading and harmonic relationships.
                        </p>
                    </div>
                    <div className="bg-gray-800/30 rounded-lg p-6">
                        <h4 className="text-white font-semibold mb-2">💡 Practice Integration</h4>
                        <p className="text-gray-400 text-sm">
                            Export progressions to practice mode. Generate exercises based on theory concepts you're exploring.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}
