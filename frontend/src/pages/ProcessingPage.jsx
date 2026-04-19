import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import ProgressTracker from '../components/ProgressTracker';
import { useWebSocket } from '../hooks/useWebSocket';
import { getJobStatus } from '../utils/api';

export default function ProcessingPage() {
  const { jobId } = useParams();
  const navigate = useNavigate();
  const { progress, clipStatuses, isConnected, error } = useWebSocket(jobId);
  const [jobStatus, setJobStatus] = useState(null);

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
    if (confirm('Are you sure you want to cancel this job?')) {
      try {
        await fetch(`/api/cancel/${jobId}`, { method: 'POST' });
        toast.success('Job cancelled');
        navigate('/');
      } catch (err) {
        toast.error('Failed to cancel job');
      }
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold text-white">Processing Video</h1>
        <p className="text-slate-400">Job ID: {jobId}</p>
      </div>

      <div className="bg-slate-800/50 backdrop-blur border border-slate-700/50 rounded-2xl p-6">
        <ProgressTracker
          progress={jobStatus?.progress ?? progress}
          clipStatuses={clipStatuses}
          isConnected={isConnected}
          jobStatus={jobStatus}
        />
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500 rounded-2xl p-4 text-red-400">
          {error}
        </div>
      )}

      <div className="flex gap-4">
        <button
          onClick={handleCancel}
          className="flex-1 px-6 py-3 bg-red-600 hover:bg-red-700 rounded-xl font-medium transition-all shadow-lg"
        >
          Cancel Job
        </button>
        <button
          onClick={() => navigate('/')}
          className="flex-1 px-6 py-3 bg-slate-800/50 border border-slate-700/50 hover:border-slate-600 rounded-xl font-medium transition-all backdrop-blur"
        >
          Back to Home
        </button>
      </div>

      <div className="bg-slate-800/50 backdrop-blur border border-slate-700/50 rounded-2xl p-6">
        <h3 className="font-semibold mb-3 text-white">What's happening?</h3>
        <ul className="space-y-2 text-sm text-slate-400">
          <li>• Downloading video from YouTube</li>
          <li>• Extracting heatmap data</li>
          <li>• Identifying viral moments</li>
          <li>• Cropping and processing clips</li>
          <li>• Generating subtitles with AI</li>
          <li>• Creating thumbnails and titles</li>
        </ul>
      </div>
    </div>
  );
}
