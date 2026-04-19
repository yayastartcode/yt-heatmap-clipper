import { useState, useEffect } from 'react';
import { getVideoInfo } from '../utils/api';

export default function VideoThumbnail({ url }) {
  const [info, setInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    const fetchInfo = async () => {
      setLoading(true);
      setError(false);
      const data = await getVideoInfo(url);
      if (data && data.title) {
        setInfo(data);
      } else {
        setError(true);
      }
      setLoading(false);
    };

    if (url) {
      fetchInfo();
    }
  }, [url]);

  if (loading) {
    return (
      <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-4 animate-pulse">
        <div className="flex gap-4">
          <div className="w-32 h-20 bg-slate-700 rounded-lg" />
          <div className="flex-1 space-y-2">
            <div className="h-4 bg-slate-700 rounded w-3/4" />
            <div className="h-3 bg-slate-700 rounded w-1/2" />
          </div>
        </div>
      </div>
    );
  }

  if (error || !info) {
    return (
      <div className="bg-red-500/10 border border-red-500/50 rounded-xl p-4">
        <p className="text-sm text-red-400">❌ Failed to load video info</p>
      </div>
    );
  }

  return (
    <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-4 hover:border-blue-500/50 transition-all">
      <div className="flex gap-4">
        {info.thumbnail_url && (
          <img
            src={info.thumbnail_url}
            alt={info.title}
            className="w-32 h-20 object-cover rounded-lg"
          />
        )}
        <div className="flex-1 min-w-0">
          <h3 className="font-medium text-white text-sm mb-1 truncate">{info.title}</h3>
          {info.author_name && (
            <p className="text-xs text-slate-400 truncate">{info.author_name}</p>
          )}
          {info.duration && (
            <p className="text-xs text-slate-500 mt-1">Duration: {Math.floor(info.duration / 60)}:{(info.duration % 60).toString().padStart(2, '0')}</p>
          )}
        </div>
      </div>
    </div>
  );
}
