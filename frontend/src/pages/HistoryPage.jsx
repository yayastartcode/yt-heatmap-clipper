import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';

export default function HistoryPage() {
  const navigate = useNavigate();
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const response = await fetch('/api/history');
        const data = await response.json();
        setJobs(data.jobs || []);
      } catch (err) {
        toast.error('Failed to load history');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, []);

  const handleDelete = async (jobId) => {
    if (!confirm('Delete this job?')) return;

    try {
      await fetch(`/api/delete/${jobId}`, { method: 'DELETE' });
      setJobs(jobs.filter(job => job.id !== jobId));
      toast.success('Job deleted');
    } catch (err) {
      toast.error('Failed to delete job');
    }
  };

  const getStatusBadge = (status) => {
    const styles = {
      completed: 'bg-green-500/20 text-green-400 border-green-500',
      processing: 'bg-blue-500/20 text-blue-400 border-blue-500',
      failed: 'bg-red-500/20 text-red-400 border-red-500',
      queued: 'bg-yellow-500/20 text-yellow-400 border-yellow-500',
    };

    return (
      <span className={`px-3 py-1 rounded-full text-xs font-medium border ${styles[status] || styles.queued}`}>
        {status}
      </span>
    );
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto text-center py-20">
        <div className="animate-spin w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-4" />
        <p className="text-slate-400">Loading history...</p>
      </div>
    );
  }

  if (jobs.length === 0) {
    return (
      <div className="max-w-4xl mx-auto text-center py-20 space-y-4">
        <div className="text-6xl mb-4">📋</div>
        <h2 className="text-2xl font-bold text-white">No History Yet</h2>
        <p className="text-slate-400">Process your first video to see it here</p>
        <button
          onClick={() => navigate('/')}
          className="px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 rounded-xl font-medium transition-all shadow-lg"
        >
          Get Started
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-white">Processing History</h1>
        <button
          onClick={() => navigate('/')}
          className="px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 rounded-xl font-medium transition-all shadow-lg"
        >
          New Job
        </button>
      </div>

      <div className="space-y-4">
        {jobs.map((job) => (
          <div
            key={job.id}
            className="bg-slate-800/50 backdrop-blur border border-slate-700/50 rounded-2xl p-6 hover:border-slate-600 transition-all"
          >
            <div className="flex items-start justify-between mb-4">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <h3 className="font-semibold text-lg text-white">{job.title || 'Untitled Job'}</h3>
                  {getStatusBadge(job.status)}
                </div>
                <p className="text-sm text-slate-400 mb-1">Job ID: {job.id}</p>
                <p className="text-sm text-slate-400">
                  Created: {new Date(job.createdAt).toLocaleString()}
                </p>
              </div>
              <button
                onClick={() => handleDelete(job.id)}
                className="text-red-400 hover:text-red-300 transition-colors"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>

            {job.urls && job.urls.length > 0 && (
              <div className="mb-4">
                <p className="text-sm text-slate-500 mb-2">URLs:</p>
                <div className="space-y-1">
                  {job.urls.map((url, i) => (
                    <p key={i} className="text-sm text-slate-400 truncate">{url}</p>
                  ))}
                </div>
              </div>
            )}

            <div className="flex gap-3">
              {job.status === 'completed' && (
                <button
                  onClick={() => navigate(`/results/${job.id}`)}
                  className="px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 rounded-xl text-sm font-medium transition-all shadow-lg"
                >
                  View Results
                </button>
              )}
              {job.status === 'processing' && (
                <button
                  onClick={() => navigate(`/processing/${job.id}`)}
                  className="px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 rounded-xl text-sm font-medium transition-all shadow-lg"
                >
                  View Progress
                </button>
              )}
              {job.status === 'failed' && (
                <button
                  onClick={() => navigate('/')}
                  className="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-xl text-sm font-medium transition-all"
                >
                  Try Again
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
