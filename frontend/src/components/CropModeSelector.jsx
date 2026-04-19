const cropModes = [
  {
    id: 'center',
    label: 'Center Crop',
    description: 'Crop from center',
    svg: (
      <svg viewBox="0 0 160 90" className="w-full h-20">
        <rect x="0" y="0" width="160" height="90" fill="#1e293b" stroke="#475569" strokeWidth="2" rx="4"/>
        <rect x="55" y="15" width="50" height="60" fill="#3b82f6" fillOpacity="0.3" stroke="#3b82f6" strokeWidth="2" rx="2"/>
        <text x="80" y="50" fill="#94a3b8" fontSize="10" textAnchor="middle">9:16</text>
      </svg>
    )
  },
  {
    id: 'left',
    label: 'Split Left (Facecam)',
    description: 'Facecam on bottom-left',
    svg: (
      <svg viewBox="0 0 50 90" className="w-full h-20">
        <rect x="0" y="0" width="50" height="90" fill="#1e293b" stroke="#475569" strokeWidth="2" rx="4"/>
        <rect x="5" y="5" width="40" height="50" fill="#8b5cf6" fillOpacity="0.3" stroke="#8b5cf6" strokeWidth="2" rx="2"/>
        <text x="25" y="32" fill="#94a3b8" fontSize="8" textAnchor="middle">Content</text>
        <rect x="5" y="60" width="20" height="25" fill="#3b82f6" fillOpacity="0.3" stroke="#3b82f6" strokeWidth="2" rx="2"/>
        <text x="15" y="74" fill="#94a3b8" fontSize="6" textAnchor="middle">Cam</text>
      </svg>
    )
  },
  {
    id: 'right',
    label: 'Split Right (Facecam)',
    description: 'Facecam on bottom-right',
    svg: (
      <svg viewBox="0 0 50 90" className="w-full h-20">
        <rect x="0" y="0" width="50" height="90" fill="#1e293b" stroke="#475569" strokeWidth="2" rx="4"/>
        <rect x="5" y="5" width="40" height="50" fill="#8b5cf6" fillOpacity="0.3" stroke="#8b5cf6" strokeWidth="2" rx="2"/>
        <text x="25" y="32" fill="#94a3b8" fontSize="8" textAnchor="middle">Content</text>
        <rect x="25" y="60" width="20" height="25" fill="#3b82f6" fillOpacity="0.3" stroke="#3b82f6" strokeWidth="2" rx="2"/>
        <text x="35" y="74" fill="#94a3b8" fontSize="6" textAnchor="middle">Cam</text>
      </svg>
    )
  }
];

export default function CropModeSelector({ selected, onSelect }) {
  return (
    <div className="space-y-3">
      <label className="block text-sm font-medium text-white">Crop Mode</label>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {cropModes.map((mode) => (
          <button
            key={mode.id}
            onClick={() => onSelect(mode.id)}
            className={`p-4 rounded-2xl border-2 transition-all text-left ${
              selected === mode.id
                ? 'border-blue-500 bg-blue-500/10 shadow-lg shadow-blue-500/20'
                : 'border-slate-700/50 bg-slate-800/50 hover:border-slate-600 backdrop-blur'
            }`}
          >
            <div className="font-medium mb-3 text-white">{mode.label}</div>
            <div className="mb-3 flex justify-center">{mode.svg}</div>
            <div className="text-xs text-slate-400">{mode.description}</div>
          </button>
        ))}
      </div>
    </div>
  );
}
