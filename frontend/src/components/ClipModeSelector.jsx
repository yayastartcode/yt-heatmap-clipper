const clipModes = [
  {
    id: 'heatmap',
    emoji: '🔥',
    label: 'Heatmap',
    description: 'Use YouTube engagement data (needs popular videos)'
  },
  {
    id: 'transcript',
    emoji: '🧠',
    label: 'AI Transcript',
    description: 'AI analyzes captions to find interesting moments'
  },
  {
    id: 'manual',
    emoji: '✂️',
    label: 'Manual',
    description: 'You choose the timestamps'
  },
  {
    id: 'even_split',
    emoji: '📐',
    label: 'Even Split',
    description: 'Split video into equal parts'
  }
];

export default function ClipModeSelector({ selected, onSelect }) {
  return (
    <div className="space-y-3">
      <label className="block text-sm font-medium text-white">Clip Detection Mode</label>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {clipModes.map((mode) => (
          <button
            key={mode.id}
            onClick={() => onSelect(mode.id)}
            className={`p-4 rounded-2xl border-2 transition-all text-left ${
              selected === mode.id
                ? 'border-blue-500 bg-blue-500/10 shadow-lg shadow-blue-500/20'
                : 'border-slate-700/50 bg-slate-800/50 hover:border-slate-600 backdrop-blur'
            }`}
          >
            <div className="flex items-center gap-3 mb-2">
              <span className="text-3xl">{mode.emoji}</span>
              <span className="font-medium text-white">{mode.label}</span>
            </div>
            <div className="text-xs text-slate-400">{mode.description}</div>
          </button>
        ))}
      </div>
    </div>
  );
}
