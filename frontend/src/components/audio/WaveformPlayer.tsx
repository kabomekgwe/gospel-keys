import { useRef, useEffect, useState } from 'react';
import WaveSurfer from 'wavesurfer.js';
import RegionsPlugin from 'wavesurfer.js/dist/plugins/regions.esm.js';
import { Play, Pause, Volume2, ZoomIn, ZoomOut, Repeat, FastForward } from 'lucide-react';

interface WaveformPlayerProps {
    audioUrl: string;
    height?: number;
    onRegionCreated?: (region: any) => void;
}

export function WaveformPlayer({ audioUrl, height = 128, onRegionCreated }: WaveformPlayerProps) {
    const containerRef = useRef<HTMLDivElement>(null);
    const wavesurferRef = useRef<WaveSurfer | null>(null);
    const regionsRef = useRef<any>(null);

    const [isPlaying, setIsPlaying] = useState(false);
    const [currentTime, setCurrentTime] = useState(0);
    const [duration, setDuration] = useState(0);
    const [playbackRate, setPlaybackRate] = useState(1.0);
    const [volume, setVolume] = useState(1.0);
    const [zoom, setZoom] = useState(0);
    const [isLooping, setIsLooping] = useState(false);

    useEffect(() => {
        if (!containerRef.current) return;

        const ws = WaveSurfer.create({
            container: containerRef.current,
            waveColor: '#4b5563', // slate-600
            progressColor: '#06b6d4', // cyan-500
            cursorColor: '#22d3ee', // cyan-400
            height,
            barWidth: 2,
            barGap: 3,
            normalize: true,
            minPxPerSec: 50,
        });

        // Initialize Regions Plugin
        const wsRegions = RegionsPlugin.create();
        ws.registerPlugin(wsRegions);
        regionsRef.current = wsRegions;

        wsRegions.on('region-created', (region) => {
            console.log('Region created', region);
            if (onRegionCreated) onRegionCreated(region);
        });

        wsRegions.on('region-clicked', (region, e) => {
            e.stopPropagation();
            region.play();
            setIsLooping(true); // Auto-loop when clicking a region?
        });

        wsRegions.on('region-out', (region) => {
            if (isLooping) {
                region.play();
            }
        });

        wavesurferRef.current = ws;

        ws.on('ready', () => {
            setDuration(ws.getDuration());
        });

        ws.on('play', () => setIsPlaying(true));
        ws.on('pause', () => setIsPlaying(false));
        ws.on('timeupdate', (time) => setCurrentTime(time));

        ws.load(audioUrl);

        return () => {
            ws.destroy();
        };
    }, [audioUrl, height]);

    // Cleanup on unmount
    useEffect(() => {
        return () => {
            if (wavesurferRef.current) {
                wavesurferRef.current.destroy();
            }
        };
    }, []);

    // Effect to handle looping state logic if needed externally
    useEffect(() => {
        if (!regionsRef.current) return;
        // Logic to toggle looping behavior on regions could go here
    }, [isLooping]);


    const togglePlay = () => {
        wavesurferRef.current?.playPause();
    };

    const handleSpeedChange = (rate: number) => {
        setPlaybackRate(rate);
        wavesurferRef.current?.setPlaybackRate(rate);
    };

    const handleVolumeChange = (vol: number) => {
        setVolume(vol);
        wavesurferRef.current?.setVolume(vol);
    };

    const handleZoom = (delta: number) => {
        const newZoom = Math.max(0, zoom + delta);
        setZoom(newZoom);
        wavesurferRef.current?.zoom(newZoom);
    };

    const formatTime = (seconds: number) => {
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    };

    return (
        <div className="bg-slate-800/50 rounded-xl p-4 border border-slate-700">
            {/* Waveform Container */}
            <div ref={containerRef} className="mb-4" />

            {/* Controls */}
            <div className="flex flex-wrap items-center justify-between gap-4">
                <div className="flex items-center gap-2">
                    <button
                        onClick={togglePlay}
                        className="p-3 bg-cyan-500 rounded-full text-white hover:bg-cyan-400 transition-colors shadow-lg shadow-cyan-500/20"
                    >
                        {isPlaying ? <Pause className="w-5 h-5 fill-current" /> : <Play className="w-5 h-5 fill-current pl-0.5" />}
                    </button>

                    <div className="flex flex-col ml-2">
                        <span className="text-white font-mono text-sm">{formatTime(currentTime)}</span>
                        <span className="text-slate-500 text-xs">{formatTime(duration)}</span>
                    </div>

                    <button
                        onClick={() => setIsLooping(!isLooping)}
                        className={`p-2 rounded-lg ml-2 transition-colors ${isLooping ? 'bg-indigo-500/20 text-indigo-400' : 'text-slate-400 hover:text-white'}`}
                        title="Toggle Loop"
                    >
                        <Repeat className="w-5 h-5" />
                    </button>
                </div>

                {/* Speed & Zoom Controls */}
                <div className="flex items-center gap-4">
                    {/* Speed */}
                    <div className="flex items-center gap-2 bg-slate-800 rounded-lg p-1.5 border border-slate-700">
                        <FastForward className="w-4 h-4 text-slate-400" />
                        <select
                            value={playbackRate}
                            onChange={(e) => handleSpeedChange(parseFloat(e.target.value))}
                            className="bg-transparent text-sm text-white focus:outline-none cursor-pointer"
                        >
                            <option value="0.5">0.5x</option>
                            <option value="0.75">0.75x</option>
                            <option value="1.0">1.0x</option>
                            <option value="1.25">1.25x</option>
                            <option value="1.5">1.5x</option>
                        </select>
                    </div>

                    {/* Zoom */}
                    <div className="flex items-center gap-1 bg-slate-800 rounded-lg p-1 border border-slate-700">
                        <button onClick={() => handleZoom(-10)} className="p-1 text-slate-400 hover:text-white">
                            <ZoomOut className="w-4 h-4" />
                        </button>
                        <button onClick={() => handleZoom(10)} className="p-1 text-slate-400 hover:text-white">
                            <ZoomIn className="w-4 h-4" />
                        </button>
                    </div>

                    {/* Volume */}
                    <div className="flex items-center gap-2 group">
                        <Volume2 className="w-5 h-5 text-slate-400" />
                        <input
                            type="range"
                            min="0"
                            max="1"
                            step="0.05"
                            value={volume}
                            onChange={(e) => handleVolumeChange(parseFloat(e.target.value))}
                            className="w-20 h-1.5 bg-slate-700 rounded-lg appearance-none cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-3 [&::-webkit-slider-thumb]:h-3 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-cyan-400"
                        />
                    </div>
                </div>
            </div>

            <div className="mt-2 text-xs text-slate-500 text-center">
                drag on waveform to create loop
            </div>
        </div>
    );
}
