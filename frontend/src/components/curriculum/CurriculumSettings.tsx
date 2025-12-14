import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { X, Save, Pause, Play, RotateCcw, Download, Trash2, AlertTriangle } from 'lucide-react';
import type { CurriculumResponse } from '../../lib/api';

interface CurriculumSettingsProps {
  curriculum: CurriculumResponse;
  onClose: () => void;
}

export function CurriculumSettings({ curriculum, onClose }: CurriculumSettingsProps) {
  const [title, setTitle] = useState(curriculum.title);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [showResetConfirm, setShowResetConfirm] = useState(false);
  const queryClient = useQueryClient();

  const { mutate: updateTitle, isPending: isUpdating } = useMutation({
    mutationFn: async (newTitle: string) => {
      const response = await fetch(`http://localhost:8000/api/v1/curriculum/${curriculum.id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: newTitle }),
      });
      if (!response.ok) throw new Error('Failed to update title');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['curriculum', 'active'] });
    },
  });

  const { mutate: togglePause, isPending: isTogglingPause } = useMutation({
    mutationFn: async () => {
      const newStatus = curriculum.status === 'active' ? 'paused' : 'active';
      const response = await fetch(`http://localhost:8000/api/v1/curriculum/${curriculum.id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus }),
      });
      if (!response.ok) throw new Error('Failed to toggle pause');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['curriculum', 'active'] });
    },
  });

  const { mutate: resetCurriculum, isPending: isResetting } = useMutation({
    mutationFn: async () => {
      const response = await fetch(`http://localhost:8000/api/v1/curriculum/${curriculum.id}/reset`, {
        method: 'POST',
      });
      if (!response.ok) throw new Error('Failed to reset curriculum');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['curriculum', 'active'] });
      setShowResetConfirm(false);
      onClose();
    },
  });

  const { mutate: deleteCurriculum, isPending: isDeleting } = useMutation({
    mutationFn: async () => {
      const response = await fetch(`http://localhost:8000/api/v1/curriculum/${curriculum.id}`, {
        method: 'DELETE',
      });
      if (!response.ok) throw new Error('Failed to delete curriculum');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['curriculum', 'active'] });
      setShowDeleteConfirm(false);
      onClose();
    },
  });

  const handleExport = () => {
    const exportData = {
      title: curriculum.title,
      description: curriculum.description,
      duration_weeks: curriculum.duration_weeks,
      current_week: curriculum.current_week,
      modules: curriculum.modules,
      exported_at: new Date().toISOString(),
    };

    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${curriculum.title.replace(/\s+/g, '_')}_curriculum.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleSaveTitle = () => {
    if (title.trim() && title !== curriculum.title) {
      updateTitle(title.trim());
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-800 rounded-xl border border-gray-700 shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-700">
          <h2 className="text-2xl font-bold text-white">Curriculum Settings</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition"
            aria-label="Close settings"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Title Edit */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Curriculum Title
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="flex-1 px-4 py-2 bg-gray-700 text-white rounded-lg border border-gray-600 focus:outline-none focus:ring-2 focus:ring-purple-500"
                placeholder="Enter curriculum title"
              />
              <button
                onClick={handleSaveTitle}
                disabled={isUpdating || title.trim() === curriculum.title}
                className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-500 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                <Save className="w-4 h-4" />
                Save
              </button>
            </div>
          </div>

          {/* Status */}
          <div>
            <h3 className="text-sm font-medium text-gray-300 mb-3">Status</h3>
            <div className="flex items-center justify-between p-4 bg-gray-700/50 rounded-lg">
              <div>
                <p className="text-white font-medium">
                  {curriculum.status === 'active' ? 'Active' : 'Paused'}
                </p>
                <p className="text-sm text-gray-400 mt-1">
                  {curriculum.status === 'active'
                    ? 'Curriculum is progressing normally'
                    : 'Curriculum is paused - no new exercises will be scheduled'}
                </p>
              </div>
              <button
                onClick={() => togglePause()}
                disabled={isTogglingPause}
                className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-500 transition flex items-center gap-2 disabled:opacity-50"
              >
                {curriculum.status === 'active' ? (
                  <>
                    <Pause className="w-4 h-4" />
                    Pause
                  </>
                ) : (
                  <>
                    <Play className="w-4 h-4" />
                    Resume
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Progress */}
          <div>
            <h3 className="text-sm font-medium text-gray-300 mb-3">Progress</h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="p-4 bg-gray-700/50 rounded-lg">
                <p className="text-sm text-gray-400">Current Week</p>
                <p className="text-2xl font-bold text-white mt-1">
                  {curriculum.current_week} / {curriculum.duration_weeks}
                </p>
              </div>
              <div className="p-4 bg-gray-700/50 rounded-lg">
                <p className="text-sm text-gray-400">Modules</p>
                <p className="text-2xl font-bold text-white mt-1">{curriculum.modules.length}</p>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div>
            <h3 className="text-sm font-medium text-gray-300 mb-3">Actions</h3>
            <div className="space-y-3">
              {/* Export */}
              <button
                onClick={handleExport}
                className="w-full p-4 bg-gray-700/50 rounded-lg hover:bg-gray-700 transition text-left flex items-center justify-between group"
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-blue-500/20 rounded-lg flex items-center justify-center group-hover:bg-blue-500/30 transition">
                    <Download className="w-5 h-5 text-blue-400" />
                  </div>
                  <div>
                    <p className="text-white font-medium">Export Curriculum</p>
                    <p className="text-sm text-gray-400">Download as JSON file</p>
                  </div>
                </div>
              </button>

              {/* Reset */}
              {!showResetConfirm ? (
                <button
                  onClick={() => setShowResetConfirm(true)}
                  className="w-full p-4 bg-gray-700/50 rounded-lg hover:bg-gray-700 transition text-left flex items-center justify-between group"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-orange-500/20 rounded-lg flex items-center justify-center group-hover:bg-orange-500/30 transition">
                      <RotateCcw className="w-5 h-5 text-orange-400" />
                    </div>
                    <div>
                      <p className="text-white font-medium">Reset Progress</p>
                      <p className="text-sm text-gray-400">Start curriculum over from week 1</p>
                    </div>
                  </div>
                </button>
              ) : (
                <div className="p-4 bg-orange-500/10 border border-orange-500/30 rounded-lg">
                  <div className="flex items-center gap-2 mb-3">
                    <AlertTriangle className="w-5 h-5 text-orange-400" />
                    <p className="text-white font-medium">Confirm Reset</p>
                  </div>
                  <p className="text-sm text-gray-300 mb-4">
                    This will reset your progress to week 1. All completed exercises will be marked as not completed. This action cannot be undone.
                  </p>
                  <div className="flex gap-2">
                    <button
                      onClick={() => resetCurriculum()}
                      disabled={isResetting}
                      className="flex-1 px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-500 transition disabled:opacity-50"
                    >
                      {isResetting ? 'Resetting...' : 'Yes, Reset Progress'}
                    </button>
                    <button
                      onClick={() => setShowResetConfirm(false)}
                      className="flex-1 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-500 transition"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              )}

              {/* Delete */}
              {!showDeleteConfirm ? (
                <button
                  onClick={() => setShowDeleteConfirm(true)}
                  className="w-full p-4 bg-gray-700/50 rounded-lg hover:bg-red-900/20 transition text-left flex items-center justify-between group"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-red-500/20 rounded-lg flex items-center justify-center group-hover:bg-red-500/30 transition">
                      <Trash2 className="w-5 h-5 text-red-400" />
                    </div>
                    <div>
                      <p className="text-white font-medium">Delete Curriculum</p>
                      <p className="text-sm text-gray-400">Permanently remove this curriculum</p>
                    </div>
                  </div>
                </button>
              ) : (
                <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
                  <div className="flex items-center gap-2 mb-3">
                    <AlertTriangle className="w-5 h-5 text-red-400" />
                    <p className="text-white font-medium">Confirm Deletion</p>
                  </div>
                  <p className="text-sm text-gray-300 mb-4">
                    This will permanently delete your curriculum and all associated data. This action cannot be undone.
                  </p>
                  <div className="flex gap-2">
                    <button
                      onClick={() => deleteCurriculum()}
                      disabled={isDeleting}
                      className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-500 transition disabled:opacity-50"
                    >
                      {isDeleting ? 'Deleting...' : 'Yes, Delete Forever'}
                    </button>
                    <button
                      onClick={() => setShowDeleteConfirm(false)}
                      className="flex-1 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-500 transition"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-gray-700 flex justify-end">
          <button
            onClick={onClose}
            className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-500 transition"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
