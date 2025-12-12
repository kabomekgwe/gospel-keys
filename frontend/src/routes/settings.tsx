/**
 * Settings Page
 */

import { createFileRoute } from '@tanstack/react-router'
import { useState } from 'react'
import {
    Settings,
    Moon,
    Sun,
    Volume2,
    Globe,
    Save,
    Server
} from 'lucide-react'
import { motion } from 'framer-motion'

export const Route = createFileRoute('/settings')({ component: SettingsPage })

function SettingsPage() {
    const [settings, setSettings] = useState({
        theme: 'dark',
        autoPlay: true,
        defaultTempo: 1.0,
        showChords: true,
        apiUrl: 'http://localhost:8009',
    })

    const handleSave = () => {
        // Save to localStorage or API
        localStorage.setItem('pianokeys_settings', JSON.stringify(settings))
        alert('Settings saved!')
    }

    return (
        <div className="min-h-screen p-8 max-w-2xl mx-auto">
            <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                className="mb-8"
            >
                <h1 className="text-3xl font-bold mb-2">Settings</h1>
                <p className="text-slate-400">
                    Customize your Piano Keys experience
                </p>
            </motion.div>

            <div className="space-y-6">
                {/* Appearance */}
                <motion.section
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="glass-card rounded-xl p-6"
                >
                    <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                        <Moon className="w-5 h-5 text-slate-400" />
                        Appearance
                    </h2>

                    <div className="space-y-4">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="font-medium text-slate-200">Theme</p>
                                <p className="text-sm text-slate-500">Choose your preferred color scheme</p>
                            </div>
                            <div className="flex bg-slate-800 border border-slate-700 rounded-lg p-1">
                                <button
                                    onClick={() => setSettings({ ...settings, theme: 'dark' })}
                                    className={`flex items-center gap-2 px-3 py-1.5 rounded ${settings.theme === 'dark' ? 'bg-slate-700 text-white' : 'text-slate-400'
                                        }`}
                                >
                                    <Moon className="w-4 h-4" />
                                    Dark
                                </button>
                                <button
                                    onClick={() => setSettings({ ...settings, theme: 'light' })}
                                    className={`flex items-center gap-2 px-3 py-1.5 rounded ${settings.theme === 'light' ? 'bg-slate-700 text-white' : 'text-slate-400'
                                        }`}
                                >
                                    <Sun className="w-4 h-4" />
                                    Light
                                </button>
                            </div>
                        </div>
                    </div>
                </motion.section>

                {/* Playback */}
                <motion.section
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                    className="glass-card rounded-xl p-6"
                >
                    <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                        <Volume2 className="w-5 h-5 text-slate-400" />
                        Playback
                    </h2>

                    <div className="space-y-4">
                        <label className="flex items-center justify-between cursor-pointer">
                            <div>
                                <p className="font-medium text-slate-200">Auto-play on load</p>
                                <p className="text-sm text-slate-500">Start playback when opening a song</p>
                            </div>
                            <div
                                onClick={() => setSettings({ ...settings, autoPlay: !settings.autoPlay })}
                                className={`w-12 h-6 rounded-full transition-colors cursor-pointer ${settings.autoPlay ? 'bg-cyan-500' : 'bg-slate-700'
                                    }`}
                            >
                                <div className={`w-5 h-5 rounded-full bg-white shadow transform transition-transform mt-0.5 ${settings.autoPlay ? 'translate-x-6' : 'translate-x-0.5'
                                    }`} />
                            </div>
                        </label>

                        <div>
                            <div className="flex items-center justify-between mb-2">
                                <div>
                                    <p className="font-medium text-slate-200">Default Practice Tempo</p>
                                    <p className="text-sm text-slate-500">Starting speed for practice mode</p>
                                </div>
                                <span className="text-cyan-400 font-medium">{settings.defaultTempo}x</span>
                            </div>
                            <input
                                type="range"
                                min="0.5"
                                max="1.5"
                                step="0.1"
                                value={settings.defaultTempo}
                                onChange={(e) => setSettings({ ...settings, defaultTempo: parseFloat(e.target.value) })}
                                className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-cyan-500"
                            />
                        </div>

                        <label className="flex items-center justify-between cursor-pointer">
                            <div>
                                <p className="font-medium text-slate-200">Show chord symbols</p>
                                <p className="text-sm text-slate-500">Display chord names in piano roll</p>
                            </div>
                            <div
                                onClick={() => setSettings({ ...settings, showChords: !settings.showChords })}
                                className={`w-12 h-6 rounded-full transition-colors cursor-pointer ${settings.showChords ? 'bg-cyan-500' : 'bg-slate-700'
                                    }`}
                            >
                                <div className={`w-5 h-5 rounded-full bg-white shadow transform transition-transform mt-0.5 ${settings.showChords ? 'translate-x-6' : 'translate-x-0.5'
                                    }`} />
                            </div>
                        </label>
                    </div>
                </motion.section>

                {/* API Configuration */}
                <motion.section
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                    className="glass-card rounded-xl p-6"
                >
                    <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                        <Server className="w-5 h-5 text-slate-400" />
                        API Configuration
                    </h2>

                    <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">
                            Backend URL
                        </label>
                        <div className="relative">
                            <Globe className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
                            <input
                                type="url"
                                value={settings.apiUrl}
                                onChange={(e) => setSettings({ ...settings, apiUrl: e.target.value })}
                                className="w-full pl-12 pr-4 py-3 bg-slate-800 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 outline-none transition-all"
                            />
                        </div>
                        <p className="text-sm text-slate-500 mt-2">
                            For self-hosted Piano Keys deployments
                        </p>
                    </div>
                </motion.section>

                {/* Save Button */}
                <motion.button
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3 }}
                    onClick={handleSave}
                    className="w-full py-3 bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-600 hover:to-blue-600 text-white font-semibold rounded-xl flex items-center justify-center gap-2 transition-all shadow-lg shadow-cyan-500/25"
                >
                    <Save className="w-5 h-5" />
                    Save Settings
                </motion.button>
            </div>
        </div>
    )
}
