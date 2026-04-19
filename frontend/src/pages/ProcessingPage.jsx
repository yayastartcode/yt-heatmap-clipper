import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import ProgressTracker from '../components/ProgressTracker';
import { useWebSocket } from '../hooks/useWebSocket';
import { getJobStatus, cancelJob } from '../utils/api';

export default function ProcessingPage() {
  const { jobId } = useParams();
  const navigate = useNavigate();
  const { progress, clipStatuses, isConnected, error } = useWebSocket(jobId);
  const [jobStatus, setJobStatus] = useState(null);
  const [showCancelConfirm, setShowCancelConfirm] = useState(false);
  const [cancelling, setCancelling] = useState(false);

  useEffect(() => {
    const checkStatus = async () => {
      try {
        const status = await getJobStatus(jobId);
        setJobStatus(status);

        if (status.status === 'completed') {
          toast.success('Processing completed!');
          setTimeout(() => {
            navigate(`/results/${jobId}`);
          }, 1000);
        } else if (status.status === 'failed') {
          toast.error('Processing failed');
        }
      } catch (err) {
        console.error('Failed to check status:', err);
      }
    };

    const interval = setInterval(checkStatus, 5000);
    checkStatus();

    return () => clearInterval(interval);
  }, [jobId, navigate]);

  const handleCancel = async () => {
    setCancelling(true);
    try {
      await cancelJob(jobId);
      toast.success('Job cancelled');
      navigate('/');
    } catch (err) {
      toast.error(err.message || 'Failed to cancel job');
      setCancelling(false);
      setShowCancelConfirm(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="text-center space-y-3">
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-500/20 border border-blue-500/50 rounded-full text-blue-400 font-medium mb-2">
          <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse" />
          Processing in progress
        </div>
        <h1 className="text-3xl font-bold text-white">Generating Your Clips</h1>
        <p className="text-slate-400">Job ID: <code className="px-2 py-1 bg-slate-800 rounded text-sm">{jobId}</code></p>
      </div>

      {/* Progress Card */}
      <div className="bg-slate-800/50 backdrop-blur border border-slate-700/50 rounded-2xl p-8 shadow-xl">
        <ProgressTracker
          progress={jobStatus?.progress ?? progress}
          clipStatuses={clipStatuses}
          isConnected={isConnected}
          jobStatus={jobStatus}
        />
      </div>

      {/* Error display */}
      {error && (
        <div className="bg-red-500/10 border border-red-500 rounded-2xl p-4 flex items-start gap-3">
          <svg className="w-6 h-6 text-red-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div className="flex-1">
            <h3 className="font-medium text-red-400 mb-1">Connection Error</h3>
            <p className="text-sm text-red-300">{error}</p>
          </div>
        </div>
      )}

      {/* Action buttons */}
      <div className="flex gap-4">
        <button
          onClick={() => setShowCancelConfirm(true)}
          disabled={cancelling}
          className="flex-1 px-6 py-3 bg-red-600 hover:bg-red-700 disabled:bg-red-800 disabled:cursor-not-allowed rounded-xl font-medium transition-all shadow-lg flex items-center justify-center gap-2"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
          {cancelling ? 'Cancelling...' : 'Cancel Job'}
        </button>
        
        <button
          onClick={() => navigate('/')}
          className="flex-1 px-6 py-3 bg-slate-800/50 border border-slate-700/50 hover:border-slate-600 rounded-xl font-medium transition-all backdrop-blur flex items-center justify-center gap-2"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
          </svg>
          Back to Home
        </button>
      </div>

      {/* What's happening info */}
      <div className="bg-slate-800/50 backdrop-blur border border-slate-700/50 rounded-2xl p-6">
        <h3 className="font-semibold mb-4 text-white flex items-center gap-2">
          <svg className="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          What's happening behind the scenes?
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm text-slate-400">
          <div className="flex items-start gap-2">
            <span className="text-blue-400">⬇️</span>
            <span>Downloading video from YouTube</span>
          </div>
          <div className="flex items-start gap-2">
            <span className="text-purple-400">🔍</span>
            <span>Extracting engagement heatmap</span>
          </div>
          <div className="flex items-start gap-2">
            <span className="text-emerald-400">🧠</span>
            <span>AI analyzing viral moments</span>
          </div>
          <div className="flex items-start gap-2">
            <span className="text-amber-400">✂️</span>
            <span>Cropping and processing clips</span>
          </div>
          <div className="flex items-start gap-2">
            <span className="text-pink-400">💬</span>
            <span>Generating AI subtitles</span>
          </div>
          <div className="flex items-start gap-2">
            <span className="text-cyan-400">🎨</span>
            <span>Creating thumbnails and titles</span>
          </div>
        </div>
      </div>

      {/* Cancel confirmation modal */}
      {showCancelConfirm && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-slate-800 border border-slate-700 rounded-2xl p-6 max-w-md w-full space-y-4 shadow-2xl">
            <div className="flex items-start gap-3">
              <div className="w-12 h-12 bg-red-500/20 rounded-full flex items-center justify-center flex-shrink-0">
                <svg className="w-6 h-6 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-white mb-2">Cancel Processing?</h3>
                <p className="text-sm text-slate-400">
                  This will stop the current job and you'll lose all progress. This action cannot be undone.
                </p>
              </div>
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => setShowCancelConfirm(false)}
                className="flex-1 px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-xl font-medium transition-all"
              >
                Keep Processing
              </button>
              <button
                onClick={handleCancel}
                disabled={cancelling}
                className="flex-1 px-4 py-2 bg-red-600 hover:bg-red-700 disabled:bg-red-800 rounded-xl font-medium transition-all"
              >
                {cancelling ? 'Cancelling...' : 'Yes, Cancel'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
