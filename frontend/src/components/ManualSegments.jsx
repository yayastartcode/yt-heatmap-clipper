import { useState } from 'react';

function parseTimeToSeconds(timeStr) {
  const parts = timeStr.split(':').map(p => parseInt(p, 10) || 0);
  if (parts.length === 2) {
    return parts[0] * 60 + parts[1];
  }
  return parts[0] || 0;
}

function formatSecondsToTime(seconds) {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}

export default function ManualSegments({ segments, onSegmentsChange }) {
  const [errors, setErrors] = useState({});

  const addSegment = () => {
    onSegmentsChange([...segments, { start: 0, end: 30 }]);
  };

  const removeSegment = (index) => {
    onSegmentsChange(segments.filter((_, i) => i !== index));
  };

  const updateSegment = (index, field, value) => {
    const newSegments = [...segments];
    const seconds = parseTimeToSeconds(value);
    newSegments[index] = { ...newSegments[index], [field]: seconds };
    
    // Validate
    const newErrors = { ...errors };
    const seg = newSegments[index];
    
    if (seg.end <= seg.start) {
      newErrors[index] = 'End time must be after start time';
    } else if (seg.end - seg.start > 60) {
      newErrors[index] = 'Segment must be 60 seconds or less';
    } else {
      delete newErrors[index];
    }
    
    setErrors(newErrors);
    onSegmentsChange(newSegments);
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <label className="block text-sm font-medium text-white">Manual Timestamps</label>
        <button
          onClick={addSegment}
          className="px-3 py-1 bg-blue-500 hover:bg-blue-600 rounded-lg text-sm font-medium transition-colors"
        >
          + Add Segment
        </button>
      </div>
      
      {segments.length === 0 && (
        <div className="text-center py-8 text-slate-400 text-sm">
          No segments added. Click "Add Segment" to start.
        </div>
      )}
      
      <div className="space-y-3">
        {segments.map((seg, index) => (
          <div
            key={index}
            className="p-4 bg-slate-800/50 border border-slate-700/50 rounded-xl space-y-2"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-white">Segment {index + 1}</span>
              <button
                onClick={() => removeSegment(index)}
                className="text-red-400 hover:text-red-300 text-sm"
              >
                Remove
              </button>
            </div>
            
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs text-slate-400 mb-1">Start (MM:SS)</label>
                <input
                  type="text"
                  value={formatSecondsToTime(seg.start)}
                  onChange={(e) => updateSegment(index, 'start', e.target.value)}
                  placeholder="0:00"
                  className="w-full px-3 py-2 bg-slate-900/50 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:border-blue-500 focus:outline-none"
                />
              </div>
              
              <div>
                <label className="block text-xs text-slate-400 mb-1">End (MM:SS)</label>
                <input
                  type="text"
                  value={formatSecondsToTime(seg.end)}
                  onChange={(e) => updateSegment(index, 'end', e.target.value)}
                  placeholder="0:30"
                  className="w-full px-3 py-2 bg-slate-900/50 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:border-blue-500 focus:outline-none"
                />
              </div>
            </div>
            
            {errors[index] && (
              <div className="text-xs text-red-400 mt-1">{errors[index]}</div>
            )}
            
            <div className="text-xs text-slate-500">
              Duration: {seg.end - seg.start}s
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
