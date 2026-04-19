import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import ClipCard from '../components/ClipCard';
import { getClips, downloadAll } from '../utils/api';

export default function ResultsPage() {
  const { jobId } = useParams();
  const navigate = useNavigate();
  const [clips, setClips] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCelebration, setShowCelebration] = useState(true);

  useEffect(() => {
    const fetchClips = async () => {
      try {
        const data = await getClips(jobId);
        setClips(data.clips || []);
        
        // Hide celebration after 3 seconds
        setTimeout(() => setShowCelebration(false), 3000);
      } catch (err) {
        toast.error('Failed to load clips');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchClips();
  }, [jobId]);

  const handleDownloadAll = () => {
    window.location.href = downloadAll(jobId);
    toast.success('Downloading all clips...');
  };

  const handleShare = () => {
    const url = window.location.href;
    navigator.clipboard.writeText(url);
    toast.success('Link copied to clipboard!');
  };

  // Calculate stats
  const totalDuration = clips.reduce((acc, clip) => {
    if (typeof clip.duration === 'number') return acc + clip.duration;
    if (typeof clip.duration === 'string') {
      const [mins, secs] = clip.duration.split(':').map(Number);
      return acc + (mins * 60) + secs;
    }
    return acc;
  }, 0);

  const formatTotalDuration = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}m ${secs}s`;
  };

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto text-center py-20">
        <div className="animate-spin w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-4" />
        <p className="text-slate-400 text-lg">Loading your clips...</p>
      </div>
    );
  }

  if (clips.length === 0) {
    return (
      <div className="max-w-6xl mx-auto text-center py-20 space-y-6">
        <div className="text-8xl mb-4 animate-bounce">😕</div>
        <h2 className="text-3xl font-bold text-white">No clips found</h2>
        <p className="text-slate-400 text-lg">The video might not have enough engagement data or viral moments</p>
        <button
          onClick={() => navigate('/')}
          className="px-8 py-4 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 rounded-xl font-medium transition-all shadow-lg text-lg"
        >
          Try Another Video
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      {/* Success Celebration */}
      {showCelebration && (
        <div className="fixed inset-0 pointer-events-none z-50 flex items-center justify-center">
          <div className="text-9xl animate-bounce">
            ✅
          </div>
        </div>
      )}

      {/* Header with stats */}
      <div className="text-center space-y-4">
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-500/20 border border-emerald-500/50 rounded-full text-emerald-400 font-medium mb-4 animate-fadeIn">
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
          </svg>
          Processing Complete!
        </div>

        <h1 className="text-4xl font-bold text-white mb-4">Your Viral Clips Are Ready! 🎉</h1>
        
        {/* Summary stats */}
        <div className="flex items-center justify-center gap-8 text-slate-400">
          <div className="flex items-center gap-2">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 4v16M17 4v16M3 8h4m10 0h4M3 12h18M3 16h4m10 0h4M4 20h16a1 1 0 001-1V5a1 1 0 00-1-1H4a1 1 0 00-1 1v14a1 1 0 001 1z" />
            </svg>
            <span className="font-medium">{clips.length} clips generated</span>
          </div>
          <div className="flex items-center gap-2">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span className="font-medium">{formatTotalDuration(totalDuration)} total</span>
          </div>
        </div>
      </div>

      {/* Action buttons */}
      <div className="flex items-center justify-center gap-4 flex-wrap">
        <button
          onClick={handleShare}
          className="px-6 py-3 bg-slate-800/50 border border-slate-700/50 hover:border-slate-600 rounded-xl font-medium transition-all backdrop-blur flex items-center gap-2"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
          </svg>
          Share Link
        </button>
        
        <button
          onClick={handleDownloadAll}
          className="px-8 py-3 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 rounded-xl font-medium transition-all shadow-lg hover:shadow-xl hover:shadow-blue-500/20 flex items-center gap-2 text-lg"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          Download All (ZIP)
        </button>

        <button
          onClick={() => navigate('/')}
          className="px-6 py-3 bg-slate-800/50 border border-slate-700/50 hover:border-slate-600 rounded-xl font-medium transition-all backdrop-blur flex items-center gap-2"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          Process Another Video
        </button>
      </div>

      {/* Clips grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {clips.map((clip, index) => (
          <ClipCard
            key={index}
            clip={{ ...clip, index: index + 1 }}
            jobId={jobId}
          />
        ))}
      </div>

      {/* Bottom CTA */}
      <div className="text-center py-8">
        <p className="text-slate-400 mb-4">Ready to create more viral content?</p>
        <button
          onClick={() => navigate('/')}
          className="px-8 py-3 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 rounded-xl font-medium transition-all shadow-lg"
        >
          Process Another Video
        </button>
      </div>
    </div>
  );
}
