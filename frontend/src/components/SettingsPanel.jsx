import { useState } from 'react';

export default function SettingsPanel({ settings, onSettingsChange }) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="bg-slate-800/50 backdrop-blur border border-slate-700/50 rounded-2xl overflow-hidden">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-6 py-4 flex items-center justify-between hover:bg-slate-700/30 transition-colors"
      >
        <h3 className="text-lg font-semibold text-white">Advanced Settings</h3>
        <svg
          className={`w-5 h-5 text-slate-400 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isExpanded && (
        <div className="px-6 pb-6 space-y-4 border-t border-slate-700/50">
          <div className="space-y-2 pt-4">
            <label className="block text-sm font-medium text-white">Max Clips</label>
            <input
              type="number"
              min="1"
              max="20"
              value={settings.maxClips || 10}
              onChange={(e) => onSettingsChange({ ...settings, maxClips: parseInt(e.target.value) })}
              className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all text-white"
            />
          </div>

          <div className="space-y-2">
            <label className="block text-sm font-medium text-white">Min Score (0-1)</label>
            <input
              type="number"
              min="0"
              max="1"
              step="0.05"
              value={settings.minScore || 0.4}
              onChange={(e) => onSettingsChange({ ...settings, minScore: parseFloat(e.target.value) })}
              className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all text-white"
            />
          </div>

          <div className="space-y-2">
            <label className="block text-sm font-medium text-white">Max Duration (seconds)</label>
            <input
              type="number"
              min="10"
              max="300"
              value={settings.maxDuration || 60}
              onChange={(e) => onSettingsChange({ ...settings, maxDuration: parseInt(e.target.value) })}
              className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all text-white"
            />
          </div>

          <div className="flex items-center justify-between pt-2">
            <label className="text-sm font-medium text-white">Auto-detect Facecam</label>
            <button
              onClick={() => onSettingsChange({ ...settings, autoDetectFacecam: !settings.autoDetectFacecam })}
              className={`relative w-12 h-6 rounded-full transition-all ${
                settings.autoDetectFacecam ? 'bg-gradient-to-r from-blue-500 to-purple-600' : 'bg-slate-700'
              }`}
            >
              <div
                className={`absolute top-1 left-1 w-4 h-4 bg-white rounded-full transition-transform shadow-lg ${
                  settings.autoDetectFacecam ? 'translate-x-6' : ''
                }`}
              />
            </button>
          </div>

          <div className="flex items-center justify-between">
            <label className="text-sm font-medium text-white">Generate AI Titles</label>
            <button
              onClick={() => onSettingsChange({ ...settings, aiTitles: !settings.aiTitles })}
              className={`relative w-12 h-6 rounded-full transition-all ${
                settings.aiTitles ? 'bg-gradient-to-r from-blue-500 to-purple-600' : 'bg-slate-700'
              }`}
            >
              <div
                className={`absolute top-1 left-1 w-4 h-4 bg-white rounded-full transition-transform shadow-lg ${
                  settings.aiTitles ? 'translate-x-6' : ''
                }`}
              />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
