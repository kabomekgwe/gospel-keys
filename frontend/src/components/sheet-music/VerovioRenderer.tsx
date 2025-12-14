/**
 * Verovio Sheet Music Renderer
 * 
 * Displays server-rendered SVG notation using Verovio.
 * Provides higher quality engraving than client-side VexFlow for full scores.
 */
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { Music, ZoomIn, ZoomOut, RefreshCw, Loader2, AlertCircle } from 'lucide-react';

interface VerovioRendererProps {
    songId: string;
    height?: number;
    showControls?: boolean;
}

// Function to fetch SVG directly
async function fetchNotationSvg(songId: string): Promise<string> {
    const response = await fetch(`/api/v1/library/songs/${songId}/notation/svg`);
    if (!response.ok) {
        throw new Error('Failed to load notation');
    }
    const data = await response.json();
    return data.svg;
}

export function VerovioRenderer({
    songId,
    showControls = true,
}: VerovioRendererProps) {
    const [zoom, setZoom] = useState(100);

    const { data: svgContent, isLoading, error, refetch } = useQuery({
        queryKey: ['notation', 'svg', songId],
        queryFn: () => fetchNotationSvg(songId),
        retry: 1,
        staleTime: 1000 * 60 * 60, // 1 hour
    });

    // Auto-scroll logic could go here if we map timestamps to SVG elements
    // For now, it's a static view of the full score

    return (
        <div className="card bg-white text-slate-900 border-none overflow-hidden flex flex-col h-full">
            {/* Header / Controls */}
            <div className="flex items-center justify-between p-4 bg-slate-100 border-b border-slate-200">
                <h3 className="text-lg font-semibold text-slate-800 flex items-center gap-2">
                    <Music className="w-5 h-5 text-violet-600" />
                    Full Score
                </h3>

                {showControls && (
                    <div className="flex items-center gap-2">
                        <button
                            onClick={() => setZoom(z => Math.max(25, z - 10))}
                            className="p-2 rounded-lg bg-white border border-slate-200 text-slate-600 hover:text-violet-600 hover:border-violet-200 transition-colors"
                            title="Zoom Out"
                        >
                            <ZoomOut className="w-4 h-4" />
                        </button>
                        <span className="text-sm text-slate-600 min-w-[5ch] text-center font-medium">
                            {zoom}%
                        </span>
                        <button
                            onClick={() => setZoom(z => Math.min(200, z + 10))}
                            className="p-2 rounded-lg bg-white border border-slate-200 text-slate-600 hover:text-violet-600 hover:border-violet-200 transition-colors"
                            title="Zoom In"
                        >
                            <ZoomIn className="w-4 h-4" />
                        </button>

                        <div className="w-px h-6 bg-slate-300 mx-1" />

                        <button
                            onClick={() => refetch()}
                            className="p-2 rounded-lg bg-white border border-slate-200 text-slate-600 hover:text-violet-600 hover:border-violet-200 transition-colors"
                            title="Refresh"
                        >
                            <RefreshCw className="w-4 h-4" />
                        </button>
                    </div>
                )}
            </div>

            {/* Content Container */}
            <div className="flex-1 overflow-auto bg-slate-50 p-6 relative min-h-[400px]">
                {isLoading ? (
                    <div className="absolute inset-0 flex flex-col items-center justify-center text-slate-500">
                        <Loader2 className="w-8 h-8 animate-spin mb-3 text-violet-500" />
                        <p>Rendering notation...</p>
                    </div>
                ) : error ? (
                    <div className="absolute inset-0 flex flex-col items-center justify-center text-rose-500">
                        <AlertCircle className="w-10 h-10 mb-3" />
                        <p className="font-semibold">Unable to load notation</p>
                        <p className="text-sm text-slate-500 mt-1">
                            The server may not have Verovio installed.
                        </p>
                    </div>
                ) : svgContent ? (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="flex justify-center"
                        style={{
                            transform: `scale(${zoom / 100})`,
                            transformOrigin: 'top center',
                            transition: 'transform 0.2s ease-out'
                        }}
                        dangerouslySetInnerHTML={{ __html: svgContent }}
                    />
                ) : (
                    <div className="flex flex-col items-center justify-center h-full text-slate-400">
                        <Music className="w-12 h-12 mb-3 opacity-20" />
                        <p>No notation available</p>
                    </div>
                )}
            </div>

            {/* Footer */}
            <div className="p-3 bg-slate-100 border-t border-slate-200 text-xs text-slate-500 flex justify-between">
                <span>Engraved by Verovio</span>
                <span>Page 1 / 1</span>
            </div>
        </div>
    );
}
