export default function SubtitleConfig({ enabled, onEnabledChange, modelSize, onModelSizeChange }) {
  const modelSizes = ['tiny', 'base', 'small', 'medium', 'large'];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <label className="text-sm font-medium text-gray-300">Enable Subtitles</label>
        <button
          onClick={() => onEnabledChange(!enabled)}
          className={`relative w-12 h-6 rounded-full transition ${
            enabled ? 'bg-accent-blue' : 'bg-gray-600'
          }`}
        >
          <div
            className={`absolute top-1 left-1 w-4 h-4 bg-white rounded-full transition-transform ${
              enabled ? 'translate-x-6' : ''
            }`}
          />
        </button>
      </div>

      {enabled && (
        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-300">Whisper Model Size</label>
          <select
            value={modelSize}
            onChange={(e) => onModelSizeChange(e.target.value)}
            className="w-full px-4 py-2 bg-dark-card border border-dark-border rounded-lg focus:outline-none focus:border-accent-blue transition"
          >
            {modelSizes.map((size) => (
              <option key={size} value={size}>
                {size.charAt(0).toUpperCase() + size.slice(1)}
              </option>
            ))}
          </select>
          <p className="text-xs text-gray-500">
            Larger models are more accurate but slower
          </p>
        </div>
      )}
    </div>
  );
}
