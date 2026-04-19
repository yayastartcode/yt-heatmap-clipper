import { useState } from 'react';
import VideoPreview from './VideoPreview';
import { getThumbnail } from '../utils/api';

export default function ClipCard({ clip, jobId }) {
  const [showPreview, setShowPreview] = useState(false);

  const downloadUrl = `/api/download/${jobId}/${clip.filename}`;
  const thumbnailUrl = clip.thumbnail || getThumbnail(jobId, clip.filename);

  // Parse duration if it's a string like "0:45"
  const formatDuration = (duration) => {
    if (!duration) return 'N/A';
    if (typeof duration === 'string') return duration;
    const mins = Math.floor(duration / 60);
    const secs = Math.floor(duration % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Get score color
  const getScoreColor = (score) => {
    if (!score) return 'bg-slate-500';
    if (score >= 0.8) return 'bg-emerald-500';
    if (score >= 0.6) return 'bg-blue-500';
    if (score >= 0.4) return 'bg-amber-500';
    return 'bg-red-500';
  };

  return (
    <>
      <div className="bg-slate-800/50 backdrop-blur border border-slate-700/50 rounded-2xl overflow-hidden hover:border-blue-500/50 hover:shadow-xl hover:shadow-blue-500/10 hover:scale-[1.02] transition-all duration-300 group">
        {/* Thumbnail with play overlay */}
        <div className="relative aspect-video bg-slate-900 overflow-hidden">
          <img
            src={thumbnailUrl}
            alt={clip.title || `Clip ${clip.index}`}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
            onError={(e) => {
              e.target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="225"%3E%3Crect fill="%230f172a" width="400" height="225"/%3E%3Ctext fill="%2394a3b8" font-size="20" x="50%25" y="50%25" text-anchor="middle" dominant-baseline="middle"%3E🎬%3C/text%3E%3C/svg%3E';
            }}
          />
          
          {/* Duration badge */}
          <div className="absolute bottom-2 right-2 px-2 py-1 bg-black/80 backdrop-blur rounded-lg text-xs font-medium text-white">
            {formatDuration(clip.duration)}
          </div>

          {/* Score indicator */}
          {clip.score !== undefined && (
            <div className="absolute top-2 right-2 px-2 py-1 bg-black/80 backdrop-blur rounded-lg text-xs font-bold text-white flex items-center gap-1">
              <div className={`w-2 h-2 rounded-full ${getScoreColor(clip.score)}`} />
              {Math.round(clip.score * 100)}
            </div>
          )}

          {/* Play button overlay */}
          <button
            onClick={() => setShowPreview(true)}
            className="absolute inset-0 flex items-center justify-center bg-black/60 opacity-0 group-hover:opacity-100 transition-all duration-300"
          >
            <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center shadow-2xl shadow-blue-500/50 group-hover:scale-110 transition-transform">
              <svg className="w-8 h-8 text-white ml-1" fill="currentColor" viewBox="0 0 20 20">
                <path d="M6.3 2.841A1.5 1.5 0 004 4.11V15.89a1.5 1.5 0 002.3 1.269l9.344-5.89a1.5 1.5 0 000-2.538L6.3 2.84z" />
              </svg>
            </div>
          </button>
        </div>

        {/* Card content */}
        <div className="p-4 space-y-3">
          <div>
            <h3 className="font-semibold text-white mb-1 line-clamp-2 leading-snug">
              {clip.title || `Clip ${clip.index}`}
            </h3>
            {clip.description && (
              <p className="text-sm text-slate-400 line-clamp-2">
                {clip.description}
              </p>
            )}
          </div>

          {/* Download button */}
          <a
            href={downloadUrl}
            download
            className="block w-full px-4 py-3 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 rounded-xl text-center font-medium transition-all shadow-lg hover:shadow-xl hover:shadow-blue-500/20 flex items-center justify-center gap-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            Download
          </a>
        </div>
      </div>

      {showPreview && (
        <VideoPreview
          src={downloadUrl}
          title={clip.title || `Clip ${clip.index}`}
          onClose={() => setShowPreview(false)}
        />
      )}
    </>
  );
}
