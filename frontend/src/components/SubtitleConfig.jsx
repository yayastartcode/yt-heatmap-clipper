export default function SubtitleConfig({ enabled, onEnabledChange, modelSize, onModelSizeChange }) {
  const modelSizes = ['tiny', 'base', 'small', 'medium', 'large'];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <label className="text-sm font-medium text-white">Enable Subtitles</label>
        <button
          onClick={() => onEnabledChange(!enabled)}
          className={`relative w-12 h-6 rounded-full transition-all ${
            enabled ? 'bg-gradient-to-r from-blue-500 to-purple-600' : 'bg-slate-700'
          }`}
        >
          <div
            className={`absolute top-1 left-1 w-4 h-4 bg-white rounded-full transition-transform shadow-lg ${
              enabled ? 'translate-x-6' : ''
            }`}
          />
        </button>
      </div>

      {enabled && (
        <div className="space-y-2">
          <label className="block text-sm font-medium text-white">Whisper Model Size</label>
          <select
            value={modelSize}
            onChange={(e) => onModelSizeChange(e.target.value)}
            className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all text-white"
          >
            {modelSizes.map((size) => (
              <option key={size} value={size} className="bg-slate-800">
                {size.charAt(0).toUpperCase() + size.slice(1)}
              </option>
            ))}
          </select>
          <p className="text-xs text-slate-400">
            Larger models are more accurate but slower
          </p>
        </div>
      )}
    </div>
  );
}
