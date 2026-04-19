import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import ClipCard from '../components/ClipCard';
import { getClips } from '../utils/api';

export default function ResultsPage() {
  const { jobId } = useParams();
  const navigate = useNavigate();
  const [clips, setClips] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchClips = async () => {
      try {
        const data = await getClips(jobId);
        setClips(data.clips || []);
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
    window.location.href = `/api/download-all/${jobId}`;
    toast.success('Downloading all clips...');
  };

  const handleShare = () => {
    const url = window.location.href;
    navigator.clipboard.writeText(url);
    toast.success('Link copied to clipboard!');
  };

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto text-center py-20">
        <div className="animate-spin w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-4" />
        <p className="text-slate-400">Loading clips...</p>
      </div>
    );
  }

  if (clips.length === 0) {
    return (
      <div className="max-w-6xl mx-auto text-center py-20 space-y-4">
        <div className="text-6xl mb-4">😕</div>
        <h2 className="text-2xl font-bold text-white">No clips found</h2>
        <p className="text-slate-400">The video might not have enough engagement data</p>
        <button
          onClick={() => navigate('/')}
          className="px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 rounded-xl font-medium transition-all shadow-lg"
        >
          Try Another Video
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-3xl font-bold mb-2 text-white">Generated Clips</h1>
          <p className="text-slate-400">{clips.length} viral moments extracted</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={handleShare}
            className="px-6 py-3 bg-slate-800/50 border border-slate-700/50 hover:border-slate-600 rounded-xl font-medium transition-all backdrop-blur"
          >
            Share
          </button>
          <button
            onClick={handleDownloadAll}
            className="px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 rounded-xl font-medium transition-all shadow-lg"
          >
            Download All (ZIP)
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {clips.map((clip, index) => (
          <ClipCard
            key={index}
            clip={{ ...clip, index: index + 1 }}
            jobId={jobId}
          />
        ))}
      </div>

      <div className="flex justify-center">
        <button
          onClick={() => navigate('/')}
          className="px-8 py-3 bg-slate-800/50 border border-slate-700/50 hover:border-slate-600 rounded-xl font-medium transition-all backdrop-blur"
        >
          Process Another Video
        </button>
      </div>
    </div>
  );
}
