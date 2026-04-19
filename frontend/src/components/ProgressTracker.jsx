import { useEffect, useState } from 'react';

const stages = ['Downloading', 'Processing', 'Subtitling', 'Done'];

export default function ProgressTracker({ progress, clipStatuses, isConnected }) {
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

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'} animate-pulse shadow-lg ${isConnected ? 'shadow-green-500/50' : 'shadow-red-500/50'}`} />
          <span className="text-sm text-slate-400">
            {isConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
        <div className="text-sm text-slate-400">
          Time elapsed: {formatTime(elapsed)}
        </div>
      </div>

      <div className="space-y-2">
        <div className="flex justify-between text-sm">
          <span className="text-white">Overall Progress</span>
          <span className="text-blue-400 font-medium">{Math.round(progress)}%</span>
        </div>
        <div className="w-full h-3 bg-slate-800 rounded-full overflow-hidden border border-slate-700/50">
          <div
            className="h-full bg-gradient-to-r from-blue-500 to-purple-600 transition-all duration-300 shadow-lg"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {clipStatuses && clipStatuses.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-sm font-medium text-white">Clip Status</h3>
          {clipStatuses.map((clip, index) => (
            <div key={index} className="bg-slate-800/50 backdrop-blur border border-slate-700/50 rounded-2xl p-4">
              <div className="flex items-center justify-between mb-3">
                <span className="font-medium text-white">Clip {index + 1}</span>
                <span className="text-sm text-slate-400">{clip.status}</span>
              </div>
              <div className="flex gap-2">
                {stages.map((stage) => (
                  <div
                    key={stage}
                    className={`flex-1 h-2 rounded-full transition-all ${
                      stages.indexOf(clip.status) >= stages.indexOf(stage)
                        ? 'bg-gradient-to-r from-blue-500 to-purple-600'
                        : 'bg-slate-700'
                    }`}
                  />
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
