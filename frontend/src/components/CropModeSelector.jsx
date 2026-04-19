import { useState } from 'react';

const cropModes = [
  {
    id: 'center',
    label: 'Center Crop',
    description: 'Crop from center',
    diagram: `
┌─────────────┐
│             │
│   ┌─────┐   │
│   │     │   │
│   └─────┘   │
│             │
└─────────────┘
    `
  },
  {
    id: 'left',
    label: 'Split Left (Facecam)',
    description: 'Facecam on left',
    diagram: `
┌─────────────┐
│ ┌───┐       │
│ │   │       │
│ │   │       │
│ └───┘       │
│             │
└─────────────┘
    `
  },
  {
    id: 'right',
    label: 'Split Right (Facecam)',
    description: 'Facecam on right',
    diagram: `
┌─────────────┐
│       ┌───┐ │
│       │   │ │
│       │   │ │
│       └───┘ │
│             │
└─────────────┘
    `
  }
];

export default function CropModeSelector({ selected, onSelect }) {
  return (
    <div className="space-y-3">
      <label className="block text-sm font-medium text-gray-300">Crop Mode</label>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {cropModes.map((mode) => (
          <button
            key={mode.id}
            onClick={() => onSelect(mode.id)}
            className={`p-4 rounded-xl border-2 transition text-left ${
              selected === mode.id
                ? 'border-accent-blue bg-accent-blue/10'
                : 'border-dark-border bg-dark-card hover:border-gray-500'
            }`}
          >
            <div className="font-medium mb-2">{mode.label}</div>
            <pre className="text-xs text-gray-400 mb-2 font-mono">{mode.diagram}</pre>
            <div className="text-xs text-gray-500">{mode.description}</div>
          </button>
        ))}
      </div>
    </div>
  );
}
