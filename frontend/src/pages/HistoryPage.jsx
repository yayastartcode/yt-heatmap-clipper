import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { deleteJob } from '../utils/api';

export default function HistoryPage() {
  const navigate = useNavigate();
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [deleteConfirm, setDeleteConfirm] = useState(null);

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
    try {
      await deleteJob(jobId);
      setJobs(jobs.filter(job => job.id !== jobId));
      toast.success('Job deleted');
      setDeleteConfirm(null);
    } catch (err) {
      toast.error(err.message || 'Failed to delete job');
    }
  };

  const handleClearAll = async () => {
    if (!confirm('Delete all jobs? This cannot be undone.')) return;

    try {
      await Promise.all(jobs.map(job => deleteJob(job.id)));
      setJobs([]);
      toast.success('All jobs deleted');
    } catch (err) {
      toast.error('Failed to delete all jobs');
    }
  };

  const getStatusBadge = (status) => {
    const styles = {
      completed: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/50',
      processing: 'bg-blue-500/20 text-blue-400 border-blue-500/50',
      failed: 'bg-red-500/20 text-red-400 border-red-500/50',
      queued: 'bg-amber-500/20 text-amber-400 border-amber-500/50',
    };

    const icons = {
      completed: '✓',
      processing: '⏳',
      failed: '✕',
      queued: '⏸',
    };

    return (
      <span className={`px-3 py-1 rounded-full text-xs font-medium border flex items-center gap-1 ${styles[status] || styles.queued}`}>
        <span>{icons[status] || '•'}</span>
        {status}
      </span>
    );
  };

  if (loading) {
    return (
      <div className="max-w-5xl mx-auto text-center py-20">
        <div className="animate-spin w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-4" />
        <p className="text-slate-400">Loading history...</p>
      </div>
    );
  }

  if (jobs.length === 0) {
    return (
      <div className="max-w-5xl mx-auto text-center py-20 space-y-6">
        <div className="text-8xl mb-4 animate-bounce">📋</div>
        <h2 className="text-3xl font-bold text-white">No History Yet</h2>
        <p className="text-slate-400 text-lg">Process your first video to see it here</p>
        <button
          onClick={() => navigate('/')}
          className="px-8 py-4 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 rounded-xl font-medium transition-all shadow-lg text-lg"
        >
          Get Started
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Processing History</h1>
          <p className="text-slate-400">{jobs.length} job{jobs.length !== 1 ? 's' : ''} total</p>
        </div>
        <div className="flex gap-3">
          {jobs.length > 0 && (
            <button
              onClick={handleClearAll}
              className="px-4 py-2 bg-red-600/20 border border-red-600/50 hover:bg-red-600/30 text-red-400 rounded-xl font-medium transition-all"
            >
              Clear All
            </button>
          )}
          <button
            onClick={() => navigate('/')}
            className="px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 rounded-xl font-medium transition-all shadow-lg"
          >
            New Job
          </button>
        </div>
      </div>

      {/* Jobs list */}
      <div className="space-y-4">
        {jobs.map((job) => (
          <div
            key={job.id}
            className="bg-slate-800/50 backdrop-blur border border-slate-700/50 rounded-2xl p-6 hover:border-slate-600 transition-all"
          >
            <div className="flex items-start justify-between gap-4 mb-4">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-3 mb-2 flex-wrap">
                  <h3 className="font-semibold text-lg text-white truncate">
                    {job.title || 'Untitled Job'}
                  </h3>
                  {getStatusBadge(job.status)}
                </div>
                <p className="text-sm text-slate-500 mb-1">
                  Job ID: <code className="px-2 py-0.5 bg-slate-900/50 rounded text-xs">{job.id}</code>
                </p>
                <p className="text-sm text-slate-400">
                  Created: {new Date(job.createdAt).toLocaleString()}
                </p>
              </div>
              
              <button
                onClick={() => setDeleteConfirm(job.id)}
                className="flex-shrink-0 w-10 h-10 flex items-center justify-center text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded-xl transition-all"
                title="Delete job"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>

            {job.urls && job.urls.length > 0 && (
              <div className="mb-4 p-3 bg-slate-900/30 rounded-xl">
                <p className="text-xs text-slate-500 mb-2 font-medium">URLs:</p>
                <div className="space-y-1">
                  {job.urls.map((url, i) => (
                    <p key={i} className="text-sm text-slate-400 truncate flex items-center gap-2">
                      <span className="text-red-500">▶</span>
                      {url}
                    </p>
                  ))}
                </div>
              </div>
            )}

            <div className="flex gap-3 flex-wrap">
              {job.status === 'completed' && (
                <button
                  onClick={() => navigate(`/results/${job.id}`)}
                  className="px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 rounded-xl text-sm font-medium transition-all shadow-lg flex items-center gap-2"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                  View Results
                </button>
              )}
              {job.status === 'processing' && (
                <button
                  onClick={() => navigate(`/processing/${job.id}`)}
                  className="px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 rounded-xl text-sm font-medium transition-all shadow-lg flex items-center gap-2"
                >
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  View Progress
                </button>
              )}
              {job.status === 'failed' && (
                <button
                  onClick={() => navigate('/')}
                  className="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-xl text-sm font-medium transition-all flex items-center gap-2"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  Try Again
                </button>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Delete confirmation modal */}
      {deleteConfirm && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-slate-800 border border-slate-700 rounded-2xl p-6 max-w-md w-full space-y-4 shadow-2xl">
            <div className="flex items-start gap-3">
              <div className="w-12 h-12 bg-red-500/20 rounded-full flex items-center justify-center flex-shrink-0">
                <svg className="w-6 h-6 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </div>
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-white mb-2">Delete Job?</h3>
                <p className="text-sm text-slate-400">
                  This will permanently delete this job and all its clips. This action cannot be undone.
                </p>
              </div>
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => setDeleteConfirm(null)}
                className="flex-1 px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-xl font-medium transition-all"
              >
                Cancel
              </button>
              <button
                onClick={() => handleDelete(deleteConfirm)}
                className="flex-1 px-4 py-2 bg-red-600 hover:bg-red-700 rounded-xl font-medium transition-all"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
