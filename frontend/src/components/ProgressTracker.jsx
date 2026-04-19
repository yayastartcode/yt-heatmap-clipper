import { useEffect, useState } from 'react';

export default function ProgressTracker({ progress, clipStatuses, isConnected, jobStatus }) {
  const [elapsed, setElapsed] = useState(0);
  const [showLogs, setShowLogs] = useState(false);

  useEffect(() => {
    const interval = setInterval(() => {
      setElapsed((prev) => prev + 1);
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getStageLabel = (stage) => {
    if (!stage) return 'Initializing...';
    const stageMap = {
      'extracting_heatmap': '🔍 Extracting heatmap data',
      'fetching_captions': '📝 Fetching captions',
      'analyzing_transcript': '🧠 AI analyzing transcript',
      'completed': '✅ Completed!'
    };
    
    if (stageMap[stage]) return stageMap[stage];
    if (stage.startsWith('downloading_clip_')) return `⬇️ Downloading clip ${stage.split('_').pop()}`;
    if (stage.startsWith('processing_clip_')) return `🎬 Processing clip ${stage.split('_').pop()}`;
    if (stage.startsWith('generating_subtitle_')) return `💬 Generating subtitle ${stage.split('_').pop()}`;
    return stage;
  };

  const getStageIcon = (stage) => {
    if (!stage) return '⏳';
    if (stage.includes('heatmap')) return '🔍';
    if (stage.includes('caption') || stage.includes('transcript')) return '📝';
    if (stage.includes('downloading')) return '⬇️';
    if (stage.includes('processing')) return '🎬';
    if (stage.includes('subtitle')) return '💬';
    if (stage === 'completed') return '✅';
    return '⚙️';
  };

  const clipsDone = jobStatus?.clips_done ?? 0;
  const totalClips = jobStatus?.total_clips ?? 0;
  const currentStage = jobStatus?.current_stage;
  const currentProgress = progress ?? 0;

  // Calculate ETA
  const eta = elapsed > 0 && currentProgress > 0 
    ? Math.round((elapsed / currentProgress) * (100 - currentProgress))
    : null;

  // Circular progress SVG
  const radius = 80;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (currentProgress / 100) * circumference;

  return (
    <div className="space-y-6">
      {/* Connection status */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-emerald-500' : 'bg-amber-500'} animate-pulse shadow-lg ${isConnected ? 'shadow-emerald-500/50' : 'shadow-amber-500/50'}`} />
          <span className="text-sm text-slate-400">
            {isConnected ? 'Live connected' : 'Polling updates...'}
          </span>
        </div>
        <div className="text-sm text-slate-400 flex items-center gap-2">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          {formatTime(elapsed)}
          {eta && <span className="text-slate-500">• ETA {formatTime(eta)}</span>}
        </div>
      </div>

      {/* Circular progress */}
      <div className="flex flex-col items-center justify-center py-8">
        <div className="relative">
          <svg className="transform -rotate-90" width="200" height="200">
            {/* Background circle */}
            <circle
              cx="100"
              cy="100"
              r={radius}
              stroke="#1e293b"
              strokeWidth="12"
              fill="none"
            />
            {/* Progress circle */}
            <circle
              cx="100"
              cy="100"
              r={radius}
              stroke="url(#gradient)"
              strokeWidth="12"
              fill="none"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              strokeLinecap="round"
              className="transition-all duration-500"
            />
            <defs>
              <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#3b82f6" />
                <stop offset="100%" stopColor="#8b5cf6" />
              </linearGradient>
            </defs>
          </svg>
          
          {/* Center content */}
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <div className="text-5xl mb-2 animate-pulse">{getStageIcon(currentStage)}</div>
            <div className="text-3xl font-bold bg-gradient-to-r from-blue-500 to-purple-600 bg-clip-text text-transparent">
              {Math.round(currentProgress)}%
            </div>
          </div>
        </div>

        {/* Current stage label */}
        <div className="mt-6 text-center">
          <p className="text-lg font-medium text-white mb-1">{getStageLabel(currentStage)}</p>
          {totalClips > 0 && (
            <p className="text-sm text-slate-400">
              {clipsDone} of {totalClips} clips completed
            </p>
          )}
        </div>
      </div>

      {/* Clip progress grid */}
      {totalClips > 0 && (
        <div className="space-y-3">
          <h3 className="text-sm font-medium text-slate-300">Clip Progress</h3>
          <div className="grid grid-cols-5 sm:grid-cols-10 gap-2">
            {Array.from({ length: totalClips }, (_, i) => {
              const clipNum = i + 1;
              const isDone = clipNum <= clipsDone;
              const isCurrent = currentStage?.includes(`_${clipNum}`);
              return (
                <div
                  key={i}
                  className={`aspect-square rounded-xl flex items-center justify-center text-sm font-bold transition-all ${
                    isDone
                      ? 'bg-emerald-500/20 border-2 border-emerald-500/50 text-emerald-400'
                      : isCurrent
                      ? 'bg-blue-500/20 border-2 border-blue-500/50 text-blue-400 animate-pulse'
                      : 'bg-slate-800/50 border-2 border-slate-700/50 text-slate-500'
                  }`}
                >
                  {isDone ? '✓' : clipNum}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Per-clip status cards */}
      {clipStatuses && clipStatuses.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-sm font-medium text-slate-300">Detailed Status</h3>
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {clipStatuses.map((clip, index) => (
              <div key={index} className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-3 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center text-sm font-bold">
                    {index + 1}
                  </span>
                  <span className="text-sm font-medium text-white">Clip {index + 1}</span>
                </div>
                <span className="text-xs text-slate-400 px-3 py-1 bg-slate-700/50 rounded-full">
                  {clip.status}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Collapsible logs section */}
      <div className="border-t border-slate-700/50 pt-4">
        <button
          onClick={() => setShowLogs(!showLogs)}
          className="w-full flex items-center justify-between text-sm text-slate-400 hover:text-slate-300 transition-colors"
        >
          <span>Live Logs</span>
          <svg 
            className={`w-5 h-5 transition-transform ${showLogs ? 'rotate-180' : ''}`}
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>
        
        {showLogs && (
          <div className="mt-3 bg-slate-900/50 border border-slate-700/30 rounded-xl p-4 max-h-48 overflow-y-auto font-mono text-xs text-slate-400">
            <p>⏳ {formatTime(elapsed)} - {getStageLabel(currentStage)}</p>
            <p>📊 Progress: {Math.round(currentProgress)}%</p>
            {totalClips > 0 && <p>🎬 Clips: {clipsDone}/{totalClips}</p>}
            {eta && <p>⏱️ ETA: {formatTime(eta)}</p>}
          </div>
        )}
      </div>
    </div>
  );
}
