/**
 * Upload Page - Transcribe new songs
 */

import { createFileRoute, useNavigate } from '@tanstack/react-router'
import { useState, useRef } from 'react'
import { useMutation } from '@tanstack/react-query'
import {
    Upload,
    Link as LinkIcon,
    FileAudio,
    X,
    Loader2,
    Music,
    CheckCircle2
} from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { transcriptionApi, TranscriptionOptions } from '../lib/api'
import { useJobsStore } from '../lib/jobsStore'

export const Route = createFileRoute('/upload')({ component: UploadPage })

function UploadPage() {
    const navigate = useNavigate()
    const fileInputRef = useRef<HTMLInputElement>(null)

    const [mode, setMode] = useState<'url' | 'file'>('url')
    const [url, setUrl] = useState('')
    const [file, setFile] = useState<File | null>(null)
    const [options, setOptions] = useState<TranscriptionOptions>({
        isolate_piano: true,
        detect_chords: true,
        detect_tempo: true,
        detect_key: true,
    })
    const [dragActive, setDragActive] = useState(false)

    // Get addJob from store
    const addJob = useJobsStore((state) => state.addJob)

    // Extract title from URL if possible
    const getUrlTitle = (inputUrl: string): string => {
        try {
            const urlObj = new URL(inputUrl)
            return urlObj.searchParams.get('v')
                ? `YouTube: ${urlObj.searchParams.get('v')?.slice(0, 8)}`
                : 'YouTube Video'
        } catch {
            return 'YouTube Video'
        }
    }

    // Mutations
    const urlMutation = useMutation({
        mutationFn: (inputUrl: string) => transcriptionApi.fromUrl(inputUrl, options),
        onSuccess: (data) => {
            addJob(data, getUrlTitle(url))
            navigate({ to: '/jobs', search: { highlight: data.job_id } })
        },
    })

    const fileMutation = useMutation({
        mutationFn: (inputFile: File) => transcriptionApi.fromUpload(inputFile, options),
        onSuccess: (data) => {
            addJob(data, file?.name || 'Uploaded File')
            navigate({ to: '/jobs', search: { highlight: data.job_id } })
        },
    })

    const isLoading = urlMutation.isPending || fileMutation.isPending
    const error = urlMutation.error || fileMutation.error

    const handleSubmit = () => {
        if (mode === 'url' && url) {
            urlMutation.mutate(url)
        } else if (mode === 'file' && file) {
            fileMutation.mutate(file)
        }
    }

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault()
        setDragActive(false)

        const droppedFile = e.dataTransfer.files[0]
        if (droppedFile && isAudioFile(droppedFile)) {
            setFile(droppedFile)
            setMode('file')
        }
    }

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        const selectedFile = e.target.files?.[0]
        if (selectedFile) {
            setFile(selectedFile)
            setMode('file')
        }
    }

    const isAudioFile = (file: File) => {
        return file.type.startsWith('audio/') || file.type.startsWith('video/')
    }

    const isYouTubeUrl = (url: string) => {
        return url.includes('youtube.com') || url.includes('youtu.be')
    }

    const canSubmit = (mode === 'url' && url && isYouTubeUrl(url)) || (mode === 'file' && file)

    return (
        <div className="min-h-screen p-8 max-w-3xl mx-auto">
            <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
            >
                <h1 className="text-3xl font-bold mb-2">Upload New Song</h1>
                <p className="text-slate-400 mb-8">
                    Transcribe piano music from YouTube or upload an audio file
                </p>
            </motion.div>

            {/* Mode Tabs */}
            <div className="flex gap-2 mb-6">
                <button
                    onClick={() => setMode('url')}
                    className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${mode === 'url'
                        ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                        : 'text-slate-400 hover:text-white hover:bg-slate-800'
                        }`}
                >
                    <LinkIcon className="w-4 h-4" />
                    YouTube URL
                </button>
                <button
                    onClick={() => setMode('file')}
                    className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${mode === 'file'
                        ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                        : 'text-slate-400 hover:text-white hover:bg-slate-800'
                        }`}
                >
                    <FileAudio className="w-4 h-4" />
                    Upload File
                </button>
            </div>

            {/* Input Area */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="glass-card rounded-xl p-6 mb-6"
            >
                <AnimatePresence mode="wait">
                    {mode === 'url' ? (
                        <motion.div
                            key="url"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                        >
                            <label className="block text-sm font-medium text-slate-300 mb-2">
                                YouTube URL
                            </label>
                            <div className="relative">
                                <LinkIcon className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
                                <input
                                    type="url"
                                    value={url}
                                    onChange={(e) => setUrl(e.target.value)}
                                    placeholder="https://www.youtube.com/watch?v=..."
                                    className="w-full pl-12 pr-4 py-3 bg-slate-800 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 outline-none transition-all"
                                />
                            </div>
                            {url && !isYouTubeUrl(url) && (
                                <p className="text-amber-400 text-sm mt-2">Please enter a valid YouTube URL</p>
                            )}
                        </motion.div>
                    ) : (
                        <motion.div
                            key="file"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                        >
                            <label className="block text-sm font-medium text-slate-300 mb-2">
                                Audio/Video File
                            </label>
                            <div
                                onDrop={handleDrop}
                                onDragOver={(e) => { e.preventDefault(); setDragActive(true) }}
                                onDragLeave={() => setDragActive(false)}
                                onClick={() => fileInputRef.current?.click()}
                                className={`
                  relative border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all
                  ${dragActive
                                        ? 'border-cyan-500 bg-cyan-500/10'
                                        : 'border-slate-700 hover:border-slate-600'
                                    }
                  ${file ? 'bg-slate-800/50' : ''}
                `}
                            >
                                <input
                                    ref={fileInputRef}
                                    type="file"
                                    accept="audio/*,video/*"
                                    onChange={handleFileSelect}
                                    className="hidden"
                                />

                                {file ? (
                                    <div className="flex items-center justify-center gap-3">
                                        <FileAudio className="w-8 h-8 text-cyan-400" />
                                        <div className="text-left">
                                            <p className="font-medium text-white">{file.name}</p>
                                            <p className="text-sm text-slate-500">
                                                {(file.size / 1024 / 1024).toFixed(2)} MB
                                            </p>
                                        </div>
                                        <button
                                            onClick={(e) => { e.stopPropagation(); setFile(null) }}
                                            className="p-1 hover:bg-slate-700 rounded"
                                        >
                                            <X className="w-5 h-5 text-slate-400" />
                                        </button>
                                    </div>
                                ) : (
                                    <>
                                        <Upload className="w-12 h-12 text-slate-500 mx-auto mb-3" />
                                        <p className="text-slate-400">
                                            Drop audio file here or <span className="text-cyan-400">browse</span>
                                        </p>
                                        <p className="text-sm text-slate-500 mt-1">
                                            MP3, WAV, MP4, etc.
                                        </p>
                                    </>
                                )}
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>
            </motion.div>

            {/* Options */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                className="glass-card rounded-xl p-6 mb-6"
            >
                <h3 className="font-medium text-white mb-4">Transcription Options</h3>
                <div className="grid grid-cols-2 gap-4">
                    {[
                        { key: 'isolate_piano', label: 'Isolate Piano', desc: 'Extract piano from mix' },
                        { key: 'detect_chords', label: 'Detect Chords', desc: 'Analyze chord progressions' },
                        { key: 'detect_tempo', label: 'Detect Tempo', desc: 'Find BPM automatically' },
                        { key: 'detect_key', label: 'Detect Key', desc: 'Identify key signature' },
                    ].map(({ key, label, desc }) => (
                        <label
                            key={key}
                            className="flex items-start gap-3 cursor-pointer group"
                        >
                            <div className="relative mt-1">
                                <input
                                    type="checkbox"
                                    checked={options[key as keyof TranscriptionOptions]}
                                    onChange={(e) => setOptions({ ...options, [key]: e.target.checked })}
                                    className="sr-only"
                                />
                                <div className={`w-5 h-5 rounded border-2 transition-all ${options[key as keyof TranscriptionOptions]
                                    ? 'bg-cyan-500 border-cyan-500'
                                    : 'border-slate-600 group-hover:border-slate-500'
                                    }`}>
                                    {options[key as keyof TranscriptionOptions] && (
                                        <CheckCircle2 className="w-4 h-4 text-white absolute top-0 left-0" />
                                    )}
                                </div>
                            </div>
                            <div>
                                <p className="font-medium text-slate-200">{label}</p>
                                <p className="text-sm text-slate-500">{desc}</p>
                            </div>
                        </label>
                    ))}
                </div>
            </motion.div>

            {/* Error */}
            {error && (
                <div className="bg-red-500/10 border border-red-500/30 text-red-400 rounded-lg p-4 mb-6">
                    {error instanceof Error ? error.message : 'An error occurred'}
                </div>
            )}

            {/* Submit */}
            <motion.button
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                onClick={handleSubmit}
                disabled={!canSubmit || isLoading}
                className={`
          w-full py-4 rounded-xl font-semibold text-lg flex items-center justify-center gap-3 transition-all
          ${canSubmit && !isLoading
                        ? 'bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-600 hover:to-blue-600 text-white shadow-lg shadow-cyan-500/25'
                        : 'bg-slate-800 text-slate-500 cursor-not-allowed'
                    }
        `}
            >
                {isLoading ? (
                    <>
                        <Loader2 className="w-5 h-5 animate-spin" />
                        Starting Transcription...
                    </>
                ) : (
                    <>
                        <Music className="w-5 h-5" />
                        Start Transcription
                    </>
                )}
            </motion.button>
        </div>
    )
}
