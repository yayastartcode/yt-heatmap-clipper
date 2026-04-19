import { useEffect, useState } from 'react';

export default function ProgressTracker({ progress, clipStatuses, isConnected, jobStatus }) {
  const [elapsed, setElapsed] = useState(0);

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
    if (stage === 'extracting_heatmap') return '🔍 Extracting heatmap data...';
    if (stage === 'fetching_captions') return '📝 Fetching captions...';
    if (stage === 'analyzing_transcript') return '🧠 AI analyzing transcript...';
    if (stage.startsWith('downloading_clip_')) return `⬇️ Downloading clip ${stage.split('_').pop()}...`;
    if (stage.startsWith('processing_clip_')) return `🎬 Processing clip ${stage.split('_').pop()}...`;
    if (stage.startsWith('generating_subtitle_')) return `💬 Generating subtitle for clip ${stage.split('_').pop()}...`;
    if (stage === 'completed') return '✅ Completed!';
    return stage;
  };

  const clipsDone = jobStatus?.clips_done ?? 0;
  const totalClips = jobStatus?.total_clips ?? 0;
  const currentStage = jobStatus?.current_stage;
  const currentProgress = progress ?? 0;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-yellow-500'} animate-pulse shadow-lg ${isConnected ? 'shadow-green-500/50' : 'shadow-yellow-500/50'}`} />
          <span className="text-sm text-slate-400">
            {isConnected ? 'Live connected' : 'Polling updates...'}
          </span>
        </div>
        <div className="text-sm text-slate-400">
          ⏱️ {formatTime(elapsed)}
        </div>
      </div>

      {/* Current stage */}
      <div className="bg-slate-900/50 border border-slate-700/30 rounded-xl p-4 text-center">
        <p className="text-lg font-medium text-white">{getStageLabel(currentStage)}</p>
        {totalClips > 0 && (
          <p className="text-sm text-slate-400 mt-1">
            {clipsDone} of {totalClips} clips done
          </p>
        )}
      </div>

      {/* Progress bar */}
      <div className="space-y-2">
        <div className="flex justify-between text-sm">
          <span className="text-white">Overall Progress</span>
          <span className="text-blue-400 font-medium">{Math.round(currentProgress)}%</span>
        </div>
        <div className="w-full h-4 bg-slate-800 rounded-full overflow-hidden border border-slate-700/50">
          <div
            className="h-full bg-gradient-to-r from-blue-500 to-purple-600 transition-all duration-500 shadow-lg shadow-blue-500/20 rounded-full"
            style={{ width: `${Math.max(currentProgress, 2)}%` }}
          />
        </div>
      </div>

      {/* Clip progress indicators */}
      {totalClips > 0 && (
        <div className="space-y-2">
          <h3 className="text-sm font-medium text-slate-300">Clips</h3>
          <div className="flex gap-2 flex-wrap">
            {Array.from({ length: totalClips }, (_, i) => {
              const clipNum = i + 1;
              const isDone = clipNum <= clipsDone;
              const isCurrent = currentStage?.includes(`_${clipNum}`);
              return (
                <div
                  key={i}
                  className={`w-10 h-10 rounded-lg flex items-center justify-center text-sm font-bold transition-all ${
                    isDone
                      ? 'bg-green-500/20 border border-green-500/50 text-green-400'
                      : isCurrent
                      ? 'bg-blue-500/20 border border-blue-500/50 text-blue-400 animate-pulse'
                      : 'bg-slate-800/50 border border-slate-700/50 text-slate-500'
                  }`}
                >
                  {isDone ? '✓' : clipNum}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* WebSocket clip statuses (if available) */}
      {clipStatuses && clipStatuses.length > 0 && (
        <div className="space-y-2">
          {clipStatuses.map((clip, index) => (
            <div key={index} className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-3 flex items-center justify-between">
              <span className="text-sm font-medium text-white">Clip {index + 1}</span>
              <span className="text-xs text-slate-400">{clip.status}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
