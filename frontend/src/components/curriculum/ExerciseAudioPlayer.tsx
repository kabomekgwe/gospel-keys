/**
 * Exercise Audio Player Component
 *
 * Plays MIDI and audio files for curriculum exercises with playback controls
 */

import { useState, useRef, useEffect } from 'react';
import { api } from '@/lib/api';

interface ExerciseAudioPlayerProps {
  exerciseId: string;
  exerciseTitle: string;
}

type AudioMethod = 'fluidsynth' | 'stable_audio';

export function ExerciseAudioPlayer({ exerciseId, exerciseTitle }: ExerciseAudioPlayerProps) {
  const [audioMethod, setAudioMethod] = useState<AudioMethod>('fluidsynth');
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [playbackRate, setPlaybackRate] = useState(1.0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [audioStatus, setAudioStatus] = useState<any>(null);

  const audioRef = useRef<HTMLAudioElement>(null);
  const audioUrlRef = useRef<string | null>(null);

  // Check audio status on mount
  useEffect(() => {
    checkAudioStatus();
  }, [exerciseId]);

  // Cleanup audio URL on unmount
  useEffect(() => {
    return () => {
      if (audioUrlRef.current) {
        URL.revokeObjectURL(audioUrlRef.current);
      }
    };
  }, []);

  const checkAudioStatus = async () => {
    try {
      const status = await api.getAudioStatus(exerciseId);
      setAudioStatus(status);
    } catch (err) {
      console.error('Failed to check audio status:', err);
    }
  };

  const loadAudio = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const blob = await api.getExerciseAudio(exerciseId, audioMethod);

      // Revoke old URL if exists
      if (audioUrlRef.current) {
        URL.revokeObjectURL(audioUrlRef.current);
      }

      // Create new URL
      const url = URL.createObjectURL(blob);
      audioUrlRef.current = url;

      if (audioRef.current) {
        audioRef.current.src = url;
        audioRef.current.playbackRate = playbackRate;
      }

      setIsLoading(false);
    } catch (err) {
      setError('Failed to load audio');
      setIsLoading(false);
    }
  };

  const togglePlay = async () => {
    if (!audioRef.current) return;

    // Load audio if not loaded
    if (!audioRef.current.src || audioRef.current.src === '') {
      await loadAudio();
    }

    if (isPlaying) {
      audioRef.current.pause();
    } else {
      audioRef.current.play();
    }
    setIsPlaying(!isPlaying);
  };

  const handleTimeUpdate = () => {
    if (audioRef.current) {
      setCurrentTime(audioRef.current.currentTime);
    }
  };

  const handleLoadedMetadata = () => {
    if (audioRef.current) {
      setDuration(audioRef.current.duration);
    }
  };

  const handleEnded = () => {
    setIsPlaying(false);
    setCurrentTime(0);
  };

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const time = parseFloat(e.target.value);
    setCurrentTime(time);
    if (audioRef.current) {
      audioRef.current.currentTime = time;
    }
  };

  const changePlaybackRate = (rate: number) => {
    setPlaybackRate(rate);
    if (audioRef.current) {
      audioRef.current.playbackRate = rate;
    }
  };

  const switchAudioMethod = (method: AudioMethod) => {
    setAudioMethod(method);
    setIsPlaying(false);
    setCurrentTime(0);
    if (audioRef.current) {
      audioRef.current.src = '';
    }
    if (audioUrlRef.current) {
      URL.revokeObjectURL(audioUrlRef.current);
      audioUrlRef.current = null;
    }
  };

  const downloadAudio = async () => {
    try {
      const blob = await api.getExerciseAudio(exerciseId, audioMethod);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${exerciseTitle.replace(/\s+/g, '_')}_${audioMethod}.wav`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Failed to download audio:', err);
    }
  };

  const downloadMIDI = async () => {
    try {
      const blob = await api.getExerciseMIDI(exerciseId);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${exerciseTitle.replace(/\s+/g, '_')}.mid`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Failed to download MIDI:', err);
    }
  };

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Check if audio is available
  const isAudioAvailable = audioStatus?.status === 'complete';

  return (
    <div className="bg-white rounded-lg shadow p-4 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-gray-900">Exercise Audio</h3>

        {/* Audio Method Toggle */}
        <div className="flex gap-2">
          <button
            onClick={() => switchAudioMethod('fluidsynth')}
            className={`px-3 py-1 text-sm rounded ${
              audioMethod === 'fluidsynth'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700'
            }`}
          >
            Piano
          </button>
          <button
            onClick={() => switchAudioMethod('stable_audio')}
            className={`px-3 py-1 text-sm rounded ${
              audioMethod === 'stable_audio'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700'
            }`}
          >
            AI Audio
          </button>
        </div>
      </div>

      {/* Status Message */}
      {!isAudioAvailable && (
        <div className="bg-yellow-50 border border-yellow-200 rounded p-3 text-sm text-yellow-800">
          {audioStatus?.status === 'generating' ? (
            '🎵 Audio is being generated... Check back soon!'
          ) : audioStatus?.status === 'failed' ? (
            '❌ Audio generation failed. Please try regenerating.'
          ) : (
            '⏳ Audio not yet generated for this exercise.'
          )}
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 rounded p-3 text-sm text-red-800">
          {error}
        </div>
      )}

      {isAudioAvailable && (
        <>
          {/* Hidden audio element */}
          <audio
            ref={audioRef}
            onTimeUpdate={handleTimeUpdate}
            onLoadedMetadata={handleLoadedMetadata}
            onEnded={handleEnded}
          />

          {/* Playback Controls */}
          <div className="space-y-3">
            {/* Play/Pause Button */}
            <button
              onClick={togglePlay}
              disabled={isLoading}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 rounded-lg disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <span>Loading...</span>
              ) : isPlaying ? (
                <>⏸ Pause</>
              ) : (
                <>▶️ Play</>
              )}
            </button>

            {/* Progress Bar */}
            <div className="space-y-1">
              <input
                type="range"
                min="0"
                max={duration || 0}
                value={currentTime}
                onChange={handleSeek}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-gray-600">
                <span>{formatTime(currentTime)}</span>
                <span>{formatTime(duration)}</span>
              </div>
            </div>

            {/* Speed Control */}
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-700">Speed:</span>
              {[0.5, 0.75, 1, 1.25, 1.5, 2].map((rate) => (
                <button
                  key={rate}
                  onClick={() => changePlaybackRate(rate)}
                  className={`px-2 py-1 text-xs rounded ${
                    playbackRate === rate
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 text-gray-700'
                  }`}
                >
                  {rate}x
                </button>
              ))}
            </div>

            {/* Download Buttons */}
            <div className="flex gap-2">
              <button
                onClick={downloadAudio}
                className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-800 py-2 rounded text-sm"
              >
                📥 Download Audio
              </button>
              <button
                onClick={downloadMIDI}
                className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-800 py-2 rounded text-sm"
              >
                🎹 Download MIDI
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
