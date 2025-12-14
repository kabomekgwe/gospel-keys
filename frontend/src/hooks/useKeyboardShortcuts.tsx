/**
 * Keyboard Shortcuts Hook
 * 
 * Provides global keyboard shortcut handling for practice and playback.
 * Features:
 * - Playback controls (space, arrows)
 * - Speed controls (1-5 keys)
 * - Loop toggle (L key)
 * - Mute toggle (M key)
 */
import { useEffect, useCallback, useRef } from 'react';

export interface KeyboardShortcutsConfig {
    /** Toggle play/pause */
    onPlayPause?: () => void;
    /** Seek forward (seconds) */
    onSeekForward?: (seconds: number) => void;
    /** Seek backward (seconds) */
    onSeekBackward?: (seconds: number) => void;
    /** Set playback speed */
    onSetSpeed?: (speed: number) => void;
    /** Toggle loop mode */
    onToggleLoop?: () => void;
    /** Toggle mute */
    onToggleMute?: () => void;
    /** Jump to start */
    onJumpToStart?: () => void;
    /** Jump to end */
    onJumpToEnd?: () => void;
    /** Whether shortcuts are enabled */
    enabled?: boolean;
}

const SPEED_MAP: Record<string, number> = {
    '1': 0.5,
    '2': 0.75,
    '3': 1.0,
    '4': 1.25,
    '5': 1.5,
};

export function useKeyboardShortcuts({
    onPlayPause,
    onSeekForward,
    onSeekBackward,
    onSetSpeed,
    onToggleLoop,
    onToggleMute,
    onJumpToStart,
    onJumpToEnd,
    enabled = true,
}: KeyboardShortcutsConfig) {
    // Use refs to avoid stale closures
    const callbacksRef = useRef({
        onPlayPause,
        onSeekForward,
        onSeekBackward,
        onSetSpeed,
        onToggleLoop,
        onToggleMute,
        onJumpToStart,
        onJumpToEnd,
    });

    // Update refs when callbacks change
    useEffect(() => {
        callbacksRef.current = {
            onPlayPause,
            onSeekForward,
            onSeekBackward,
            onSetSpeed,
            onToggleLoop,
            onToggleMute,
            onJumpToStart,
            onJumpToEnd,
        };
    }, [onPlayPause, onSeekForward, onSeekBackward, onSetSpeed, onToggleLoop, onToggleMute, onJumpToStart, onJumpToEnd]);

    const handleKeyDown = useCallback((event: KeyboardEvent) => {
        // Don't trigger if user is typing in an input
        const target = event.target as HTMLElement;
        if (
            target.tagName === 'INPUT' ||
            target.tagName === 'TEXTAREA' ||
            target.isContentEditable
        ) {
            return;
        }

        const { key, ctrlKey, metaKey, shiftKey } = event;
        const callbacks = callbacksRef.current;

        switch (key) {
            // Playback
            case ' ':
                event.preventDefault();
                callbacks.onPlayPause?.();
                break;

            // Seeking
            case 'ArrowLeft':
                event.preventDefault();
                callbacks.onSeekBackward?.(shiftKey ? 10 : 5);
                break;
            case 'ArrowRight':
                event.preventDefault();
                callbacks.onSeekForward?.(shiftKey ? 10 : 5);
                break;

            // Jump to start/end
            case 'Home':
                event.preventDefault();
                callbacks.onJumpToStart?.();
                break;
            case 'End':
                event.preventDefault();
                callbacks.onJumpToEnd?.();
                break;

            // Speed (1-5 keys)
            case '1':
            case '2':
            case '3':
            case '4':
            case '5':
                if (!ctrlKey && !metaKey) {
                    event.preventDefault();
                    callbacks.onSetSpeed?.(SPEED_MAP[key]);
                }
                break;

            // Toggles
            case 'l':
            case 'L':
                if (!ctrlKey && !metaKey) {
                    event.preventDefault();
                    callbacks.onToggleLoop?.();
                }
                break;
            case 'm':
            case 'M':
                if (!ctrlKey && !metaKey) {
                    event.preventDefault();
                    callbacks.onToggleMute?.();
                }
                break;
        }
    }, []);

    useEffect(() => {
        if (!enabled) return;

        document.addEventListener('keydown', handleKeyDown);
        return () => document.removeEventListener('keydown', handleKeyDown);
    }, [enabled, handleKeyDown]);
}

interface ShortcutItem {
    key: string;
    description: string;
}

// Keyboard shortcuts help overlay
export function KeyboardShortcutsHelp({ className = '' }: { className?: string }) {
    const shortcuts: ShortcutItem[] = [
        { key: 'Space', description: 'Play/Pause' },
        { key: '←', description: 'Seek backward 5s' },
        { key: '→', description: 'Seek forward 5s' },
        { key: 'Shift+←/→', description: 'Seek 10s' },
        { key: 'Home', description: 'Jump to start' },
        { key: 'End', description: 'Jump to end' },
        { key: '1-5', description: 'Set speed (0.5x-1.5x)' },
        { key: 'L', description: 'Toggle loop' },
        { key: 'M', description: 'Toggle mute' },
    ];

    return (
        <div className={`p-4 bg-slate-800/90 rounded-xl border border-slate-700 ${className}`}>
            <h3 className="text-sm font-semibold text-slate-200 mb-3">Keyboard Shortcuts</h3>
            <div className="grid grid-cols-2 gap-2 text-sm">
                {shortcuts.map((item) => (
                    <div key={item.key} className="flex items-center gap-2">
                        <kbd className="px-2 py-1 bg-slate-700 rounded text-xs font-mono text-slate-300">
                            {item.key}
                        </kbd>
                        <span className="text-slate-400">{item.description}</span>
                    </div>
                ))}
            </div>
        </div>
    );
}
