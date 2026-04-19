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
          <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'} animate-pulse`} />
          <span className="text-sm text-gray-400">
            {isConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
        <div className="text-sm text-gray-400">
          Time elapsed: {formatTime(elapsed)}
        </div>
      </div>

      <div className="space-y-2">
        <div className="flex justify-between text-sm">
          <span className="text-gray-300">Overall Progress</span>
          <span className="text-accent-blue font-medium">{Math.round(progress)}%</span>
        </div>
        <div className="w-full h-3 bg-dark-card rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-accent-blue to-accent-purple transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {clipStatuses && clipStatuses.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-sm font-medium text-gray-300">Clip Status</h3>
          {clipStatuses.map((clip, index) => (
            <div key={index} className="bg-dark-card border border-dark-border rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium">Clip {index + 1}</span>
                <span className="text-sm text-gray-400">{clip.status}</span>
              </div>
              <div className="flex gap-2">
                {stages.map((stage) => (
                  <div
                    key={stage}
                    className={`flex-1 h-2 rounded-full ${
                      stages.indexOf(clip.status) >= stages.indexOf(stage)
                        ? 'bg-accent-blue'
                        : 'bg-gray-700'
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
