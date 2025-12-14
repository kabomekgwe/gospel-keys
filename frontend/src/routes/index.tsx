/**
 * Home Page - Piano Keys Dashboard
 */

import { createFileRoute, Link } from '@tanstack/react-router'
import { useQuery } from '@tanstack/react-query'
import {
  Upload,
  Music2,
  TrendingUp,
  Clock,
  Star,
  ArrowRight
} from 'lucide-react'
import { motion } from 'framer-motion'
import { libraryApi, healthApi } from '../lib/api'
import { useUIStore } from '../lib/uiStore'

export const Route = createFileRoute('/')({ component: HomePage })

function HomePage() {
  const { openUploadModal } = useUIStore()

  // Check API health
  const { data: health } = useQuery({
    queryKey: ['health'],
    queryFn: healthApi.check,
    retry: false,
  })

  // Get recent songs
  const { data: recentSongs } = useQuery({
    queryKey: ['songs', 'recent'],
    queryFn: () => libraryApi.listSongs({ limit: 5 }),
  })

  // Note: 'Active Jobs' card removed as it's now integrated in Library
  const quickActions = [
    {
      title: 'Upload New Song',
      description: 'Transcribe from YouTube or file',
      icon: <Upload className="w-8 h-8" />,
      onClick: openUploadModal, // Use onClick instead of href
      color: 'from-cyan-500 to-blue-500',
    },
    {
      title: 'Browse Library',
      description: 'View your transcribed songs',
      icon: <Music2 className="w-8 h-8" />,
      href: '/library',
      color: 'from-violet-500 to-purple-500',
    },
  ]

  return (
    <div className="min-h-screen p-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-12"
      >
        <h1 className="text-4xl font-bold mb-2">
          Welcome to <span className="gradient-text">Piano Keys</span>
        </h1>
        <p className="text-slate-400 text-lg">
          AI-powered piano transcription, analysis, and learning
        </p>

        {/* API Status */}
        <div className="mt-4 flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${health ? 'bg-emerald-400' : 'bg-red-400'}`} />
          <span className="text-sm text-slate-500">
            {health ? `API Connected (v${health.version})` : 'API Disconnected'}
          </span>
        </div>
      </motion.div>

      {/* Quick Actions */}
      <section className="mb-12">
        <h2 className="text-xl font-semibold mb-6 text-slate-200">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6"> {/* Adjusted bandwidth */}
          {quickActions.map((action, index) => (
            <motion.div
              key={action.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              {action.href ? (
                <Link
                  to={action.href}
                  className="block group"
                >
                  <div className="glass-card rounded-xl p-6 hover:border-cyan-500/50 transition-all duration-300 hover:shadow-lg hover:shadow-cyan-500/10">
                    <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${action.color} flex items-center justify-center text-white mb-4`}>
                      {action.icon}
                    </div>
                    <h3 className="text-lg font-semibold text-white mb-1 group-hover:text-cyan-400 transition-colors">
                      {action.title}
                    </h3>
                    <p className="text-slate-400 text-sm">
                      {action.description}
                    </p>
                  </div>
                </Link>
              ) : (
                <button
                  onClick={action.onClick}
                  className="block w-full text-left group"
                >
                  <div className="glass-card rounded-xl p-6 hover:border-cyan-500/50 transition-all duration-300 hover:shadow-lg hover:shadow-cyan-500/10">
                    <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${action.color} flex items-center justify-center text-white mb-4`}>
                      {action.icon}
                    </div>
                    <h3 className="text-lg font-semibold text-white mb-1 group-hover:text-cyan-400 transition-colors">
                      {action.title}
                    </h3>
                    <p className="text-slate-400 text-sm">
                      {action.description}
                    </p>
                  </div>
                </button>
              )}
            </motion.div>
          ))}
        </div>
      </section>

      {/* Recent Songs */}
      <section className="mb-12">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-slate-200">
            <Clock className="w-5 h-5 inline-block mr-2 text-slate-400" />
            Recent Songs
          </h2>
          <Link
            to="/library"
            className="text-cyan-400 hover:text-cyan-300 text-sm flex items-center gap-1"
          >
            View all <ArrowRight className="w-4 h-4" />
          </Link>
        </div>

        {recentSongs && recentSongs.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
            {recentSongs.map((song, index) => (
              <motion.div
                key={song.id}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: index * 0.05 }}
              >
                <Link to={`/library/${song.id}`}>
                  <div className="glass-card rounded-lg p-4 hover:border-cyan-500/30 transition-all cursor-pointer group">
                    <div className="flex items-center gap-3 mb-3">
                      <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-slate-700 to-slate-800 flex items-center justify-center">
                        <Music2 className="w-5 h-5 text-cyan-400" />
                      </div>
                      {song.favorite && (
                        <Star className="w-4 h-4 text-yellow-400 fill-yellow-400" />
                      )}
                    </div>
                    <h3 className="font-medium text-white truncate group-hover:text-cyan-400 transition-colors">
                      {song.title}
                    </h3>
                    <p className="text-sm text-slate-500 truncate">
                      {song.artist || 'Unknown Artist'}
                    </p>
                    <div className="mt-2 flex items-center gap-3 text-xs text-slate-500">
                      <span>{Math.round(song.duration / 60)}:{String(Math.round(song.duration % 60)).padStart(2, '0')}</span>
                      {song.tempo && <span>{Math.round(song.tempo)} BPM</span>}
                    </div>
                  </div>
                </Link>
              </motion.div>
            ))}
          </div>
        ) : (
          <div className="glass-card rounded-xl p-12 text-center">
            <Music2 className="w-12 h-12 text-slate-600 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-slate-400 mb-2">No songs yet</h3>
            <p className="text-slate-500 mb-6">
              Upload your first song to get started
            </p>
            <button
              onClick={openUploadModal}
              className="inline-flex items-center gap-2 px-6 py-3 bg-cyan-500 hover:bg-cyan-600 text-white font-medium rounded-lg transition-colors"
            >
              <Upload className="w-5 h-5" />
              Upload Song
            </button>
          </div>
        )}
      </section>

      {/* Stats (placeholder) */}
      <section>
        <h2 className="text-xl font-semibold mb-6 text-slate-200">
          <TrendingUp className="w-5 h-5 inline-block mr-2 text-slate-400" />
          Your Stats
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { label: 'Songs Transcribed', value: recentSongs?.length || 0 },
            { label: 'Practice Sessions', value: 0 },
            { label: 'Hours Practiced', value: '0h' },
            { label: 'Favorite Songs', value: recentSongs?.filter(s => s.favorite).length || 0 },
          ].map((stat, index) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 + index * 0.1 }}
              className="glass-card rounded-lg p-4 text-center"
            >
              <div className="text-3xl font-bold text-white mb-1">{stat.value}</div>
              <div className="text-sm text-slate-500">{stat.label}</div>
            </motion.div>
          ))}
        </div>
      </section>
    </div>
  )
}
