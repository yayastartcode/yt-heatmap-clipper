export default function SettingsPanel({ settings, onSettingsChange }) {
  return (
    <div className="bg-dark-card border border-dark-border rounded-xl p-6 space-y-4">
      <h3 className="text-lg font-semibold mb-4">Advanced Settings</h3>

      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-300">Max Clips</label>
        <input
          type="number"
          min="1"
          max="20"
          value={settings.maxClips || 10}
          onChange={(e) => onSettingsChange({ ...settings, maxClips: parseInt(e.target.value) })}
          className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg focus:outline-none focus:border-accent-blue transition"
        />
      </div>

      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-300">Min Score (0-1)</label>
        <input
          type="number"
          min="0"
          max="1"
          step="0.05"
          value={settings.minScore || 0.4}
          onChange={(e) => onSettingsChange({ ...settings, minScore: parseFloat(e.target.value) })}
          className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg focus:outline-none focus:border-accent-blue transition"
        />
      </div>

      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-300">Max Duration (seconds)</label>
        <input
          type="number"
          min="10"
          max="300"
          value={settings.maxDuration || 60}
          onChange={(e) => onSettingsChange({ ...settings, maxDuration: parseInt(e.target.value) })}
          className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg focus:outline-none focus:border-accent-blue transition"
        />
      </div>

      <div className="flex items-center justify-between">
        <label className="text-sm font-medium text-gray-300">Auto-detect Facecam</label>
        <button
          onClick={() => onSettingsChange({ ...settings, autoDetectFacecam: !settings.autoDetectFacecam })}
          className={`relative w-12 h-6 rounded-full transition ${
            settings.autoDetectFacecam ? 'bg-accent-blue' : 'bg-gray-600'
          }`}
        >
          <div
            className={`absolute top-1 left-1 w-4 h-4 bg-white rounded-full transition-transform ${
              settings.autoDetectFacecam ? 'translate-x-6' : ''
            }`}
          />
        </button>
      </div>

      <div className="flex items-center justify-between">
        <label className="text-sm font-medium text-gray-300">Generate AI Titles</label>
        <button
          onClick={() => onSettingsChange({ ...settings, aiTitles: !settings.aiTitles })}
          className={`relative w-12 h-6 rounded-full transition ${
            settings.aiTitles ? 'bg-accent-blue' : 'bg-gray-600'
          }`}
        >
          <div
            className={`absolute top-1 left-1 w-4 h-4 bg-white rounded-full transition-transform ${
              settings.aiTitles ? 'translate-x-6' : ''
            }`}
          />
        </button>
      </div>
    </div>
  );
}
