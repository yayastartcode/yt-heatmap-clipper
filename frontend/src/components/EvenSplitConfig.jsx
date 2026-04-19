export default function EvenSplitConfig({ splitCount, onSplitCountChange, maxDuration, onMaxDurationChange }) {
  return (
    <div className="space-y-4">
      <label className="block text-sm font-medium text-white">Even Split Configuration</label>
      
      <div className="p-4 bg-slate-800/50 border border-slate-700/50 rounded-xl space-y-4">
        <div>
          <label className="block text-xs text-slate-400 mb-2">
            Number of clips: {splitCount}
          </label>
          <input
            type="range"
            min="2"
            max="20"
            value={splitCount}
            onChange={(e) => onSplitCountChange(parseInt(e.target.value, 10))}
            className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-blue-500"
          />
          <div className="flex justify-between text-xs text-slate-500 mt-1">
            <span>2</span>
            <span>20</span>
          </div>
        </div>
        
        <div>
          <label className="block text-xs text-slate-400 mb-2">
            Max duration per clip (seconds)
          </label>
          <input
            type="number"
            min="10"
            max="120"
            value={maxDuration}
            onChange={(e) => onMaxDurationChange(parseInt(e.target.value, 10) || 60)}
            className="w-full px-3 py-2 bg-slate-900/50 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:border-blue-500 focus:outline-none"
          />
          <div className="text-xs text-slate-500 mt-1">
            Recommended: 30-60 seconds for short-form content
          </div>
        </div>
      </div>
    </div>
  );
}
