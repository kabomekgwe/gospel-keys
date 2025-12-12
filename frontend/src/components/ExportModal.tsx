/**
 * Export Modal Component
 * 
 * Modal dialog for exporting songs in various formats:
 * - MIDI file export
 * - MusicXML export
 * - Audio export (original/isolated)
 * - Sheet music PDF generation (future)
 */
import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    X,
    Download,
    FileMusic,
    FileText,
    Music2,
    Check,
    Loader2,
    Settings2,
} from 'lucide-react';

export interface ExportModalProps {
    isOpen: boolean;
    onClose: () => void;
    songId: string;
    songTitle: string;
    onExport: (format: ExportFormat, options: ExportOptions) => Promise<void>;
}

export type ExportFormat = 'midi' | 'musicxml' | 'audio_original' | 'audio_isolated' | 'pdf';

export interface ExportOptions {
    format: ExportFormat;
    includeChords?: boolean;
    includeDynamics?: boolean;
    separateHands?: boolean;
    audioFormat?: 'mp3' | 'wav' | 'flac';
    quality?: 'standard' | 'high';
}

const EXPORT_FORMATS = [
    {
        id: 'midi' as const,
        name: 'MIDI',
        description: 'Standard MIDI file for DAWs and notation software',
        icon: FileMusic,
        extension: '.mid',
        color: 'cyan',
    },
    {
        id: 'musicxml' as const,
        name: 'MusicXML',
        description: 'Sheet music format for Finale, Sibelius, MuseScore',
        icon: FileText,
        extension: '.musicxml',
        color: 'violet',
    },
    {
        id: 'audio_original' as const,
        name: 'Original Audio',
        description: 'Download the original audio file',
        icon: Music2,
        extension: '.mp3',
        color: 'amber',
    },
    {
        id: 'audio_isolated' as const,
        name: 'Isolated Piano',
        description: 'Piano track isolated from the mix',
        icon: Music2,
        extension: '.wav',
        color: 'emerald',
    },
];

export function ExportModal({
    isOpen,
    onClose,
    songId,
    songTitle,
    onExport,
}: ExportModalProps) {
    const [selectedFormat, setSelectedFormat] = useState<ExportFormat>('midi');
    const [showOptions, setShowOptions] = useState(false);
    const [isExporting, setIsExporting] = useState(false);
    const [exportComplete, setExportComplete] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Options state
    const [includeChords, setIncludeChords] = useState(true);
    const [includeDynamics, setIncludeDynamics] = useState(true);
    const [separateHands, setSeparateHands] = useState(true);
    const [audioFormat, setAudioFormat] = useState<'mp3' | 'wav' | 'flac'>('mp3');
    const [quality, setQuality] = useState<'standard' | 'high'>('high');

    const handleExport = async () => {
        setIsExporting(true);
        setError(null);
        setExportComplete(false);

        try {
            await onExport(selectedFormat, {
                format: selectedFormat,
                includeChords,
                includeDynamics,
                separateHands,
                audioFormat,
                quality,
            });
            setExportComplete(true);

            // Auto-close after success
            setTimeout(() => {
                onClose();
                setExportComplete(false);
            }, 2000);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Export failed');
        } finally {
            setIsExporting(false);
        }
    };

    const selectedFormatInfo = EXPORT_FORMATS.find(f => f.id === selectedFormat);

    return (
        <AnimatePresence>
            {isOpen && (
                <>
                    {/* Backdrop */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={onClose}
                        className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50"
                    />

                    {/* Modal */}
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95, y: 20 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95, y: 20 }}
                        className="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-lg z-50"
                    >
                        <div className="bg-slate-800 border border-slate-700 rounded-2xl shadow-2xl overflow-hidden">
                            {/* Header */}
                            <div className="flex items-center justify-between p-6 border-b border-slate-700">
                                <div>
                                    <h2 className="text-xl font-semibold text-white flex items-center gap-2">
                                        <Download className="w-5 h-5 text-cyan-400" />
                                        Export
                                    </h2>
                                    <p className="text-sm text-slate-400 mt-1 truncate max-w-sm">
                                        {songTitle}
                                    </p>
                                </div>

                                <button
                                    onClick={onClose}
                                    className="p-2 text-slate-400 hover:text-white hover:bg-slate-700 rounded-lg transition-colors"
                                >
                                    <X className="w-5 h-5" />
                                </button>
                            </div>

                            {/* Format selection */}
                            <div className="p-6 space-y-4">
                                <label className="text-sm font-medium text-slate-300">
                                    Export Format
                                </label>

                                <div className="grid grid-cols-2 gap-3">
                                    {EXPORT_FORMATS.map((format) => {
                                        const isSelected = selectedFormat === format.id;

                                        return (
                                            <motion.button
                                                key={format.id}
                                                whileHover={{ scale: 1.02 }}
                                                whileTap={{ scale: 0.98 }}
                                                onClick={() => setSelectedFormat(format.id)}
                                                className={`
                          p-4 rounded-xl border text-left transition-all
                          ${isSelected
                                                        ? `bg-${format.color}-500/10 border-${format.color}-500/50 ring-2 ring-${format.color}-500/30`
                                                        : 'bg-slate-700/30 border-slate-600/50 hover:bg-slate-700/50'
                                                    }
                        `}
                                            >
                                                <div className="flex items-start gap-3">
                                                    <div className={`
                            p-2 rounded-lg
                            ${isSelected ? `bg-${format.color}-500/20` : 'bg-slate-600/30'}
                          `}>
                                                        <format.icon className={`w-5 h-5 ${isSelected ? `text-${format.color}-400` : 'text-slate-400'}`} />
                                                    </div>

                                                    <div className="flex-1 min-w-0">
                                                        <div className="flex items-center gap-2">
                                                            <span className={`font-medium ${isSelected ? 'text-white' : 'text-slate-300'}`}>
                                                                {format.name}
                                                            </span>
                                                            <span className="text-xs text-slate-500">{format.extension}</span>
                                                        </div>
                                                        <p className="text-xs text-slate-400 mt-0.5 line-clamp-2">
                                                            {format.description}
                                                        </p>
                                                    </div>

                                                    {isSelected && (
                                                        <Check className="w-4 h-4 text-cyan-400 flex-shrink-0" />
                                                    )}
                                                </div>
                                            </motion.button>
                                        );
                                    })}
                                </div>
                            </div>

                            {/* Options toggle */}
                            <div className="px-6">
                                <button
                                    onClick={() => setShowOptions(!showOptions)}
                                    className="flex items-center gap-2 text-sm text-slate-400 hover:text-white transition-colors"
                                >
                                    <Settings2 className="w-4 h-4" />
                                    {showOptions ? 'Hide' : 'Show'} export options
                                </button>
                            </div>

                            {/* Options panel */}
                            <AnimatePresence>
                                {showOptions && (
                                    <motion.div
                                        initial={{ height: 0, opacity: 0 }}
                                        animate={{ height: 'auto', opacity: 1 }}
                                        exit={{ height: 0, opacity: 0 }}
                                        className="overflow-hidden"
                                    >
                                        <div className="p-6 pt-4 space-y-4">
                                            {(selectedFormat === 'midi' || selectedFormat === 'musicxml') && (
                                                <>
                                                    <label className="flex items-center gap-3 cursor-pointer">
                                                        <input
                                                            type="checkbox"
                                                            checked={includeChords}
                                                            onChange={(e) => setIncludeChords(e.target.checked)}
                                                            className="w-4 h-4 rounded bg-slate-700 border-slate-600 text-cyan-500 focus:ring-cyan-500"
                                                        />
                                                        <span className="text-sm text-slate-300">Include chord symbols</span>
                                                    </label>

                                                    <label className="flex items-center gap-3 cursor-pointer">
                                                        <input
                                                            type="checkbox"
                                                            checked={includeDynamics}
                                                            onChange={(e) => setIncludeDynamics(e.target.checked)}
                                                            className="w-4 h-4 rounded bg-slate-700 border-slate-600 text-cyan-500 focus:ring-cyan-500"
                                                        />
                                                        <span className="text-sm text-slate-300">Include dynamics (velocity)</span>
                                                    </label>

                                                    <label className="flex items-center gap-3 cursor-pointer">
                                                        <input
                                                            type="checkbox"
                                                            checked={separateHands}
                                                            onChange={(e) => setSeparateHands(e.target.checked)}
                                                            className="w-4 h-4 rounded bg-slate-700 border-slate-600 text-cyan-500 focus:ring-cyan-500"
                                                        />
                                                        <span className="text-sm text-slate-300">Separate left/right hands</span>
                                                    </label>
                                                </>
                                            )}

                                            {(selectedFormat === 'audio_original' || selectedFormat === 'audio_isolated') && (
                                                <>
                                                    <div>
                                                        <label className="text-sm text-slate-400 mb-2 block">Audio format</label>
                                                        <div className="flex gap-2">
                                                            {(['mp3', 'wav', 'flac'] as const).map((fmt) => (
                                                                <button
                                                                    key={fmt}
                                                                    onClick={() => setAudioFormat(fmt)}
                                                                    className={`
                                    px-4 py-2 rounded-lg text-sm font-medium transition-colors
                                    ${audioFormat === fmt
                                                                            ? 'bg-cyan-500 text-white'
                                                                            : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                                                                        }
                                  `}
                                                                >
                                                                    {fmt.toUpperCase()}
                                                                </button>
                                                            ))}
                                                        </div>
                                                    </div>

                                                    <div>
                                                        <label className="text-sm text-slate-400 mb-2 block">Quality</label>
                                                        <div className="flex gap-2">
                                                            {(['standard', 'high'] as const).map((q) => (
                                                                <button
                                                                    key={q}
                                                                    onClick={() => setQuality(q)}
                                                                    className={`
                                    px-4 py-2 rounded-lg text-sm font-medium capitalize transition-colors
                                    ${quality === q
                                                                            ? 'bg-cyan-500 text-white'
                                                                            : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                                                                        }
                                  `}
                                                                >
                                                                    {q}
                                                                </button>
                                                            ))}
                                                        </div>
                                                    </div>
                                                </>
                                            )}
                                        </div>
                                    </motion.div>
                                )}
                            </AnimatePresence>

                            {/* Error message */}
                            {error && (
                                <div className="mx-6 p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-sm">
                                    {error}
                                </div>
                            )}

                            {/* Actions */}
                            <div className="p-6 flex items-center justify-end gap-3 border-t border-slate-700">
                                <button
                                    onClick={onClose}
                                    disabled={isExporting}
                                    className="px-4 py-2 text-slate-300 hover:text-white transition-colors"
                                >
                                    Cancel
                                </button>

                                <motion.button
                                    whileHover={{ scale: 1.02 }}
                                    whileTap={{ scale: 0.98 }}
                                    onClick={handleExport}
                                    disabled={isExporting || exportComplete}
                                    className={`
                    flex items-center gap-2 px-6 py-2.5 rounded-xl font-medium transition-all
                    ${exportComplete
                                            ? 'bg-emerald-500 text-white'
                                            : 'bg-gradient-to-r from-cyan-500 to-cyan-400 text-white hover:shadow-lg hover:shadow-cyan-500/30'
                                        }
                    disabled:opacity-50
                  `}
                                >
                                    {isExporting ? (
                                        <>
                                            <Loader2 className="w-4 h-4 animate-spin" />
                                            Exporting...
                                        </>
                                    ) : exportComplete ? (
                                        <>
                                            <Check className="w-4 h-4" />
                                            Downloaded!
                                        </>
                                    ) : (
                                        <>
                                            <Download className="w-4 h-4" />
                                            Export {selectedFormatInfo?.name}
                                        </>
                                    )}
                                </motion.button>
                            </div>
                        </div>
                    </motion.div>
                </>
            )}
        </AnimatePresence>
    );
}
