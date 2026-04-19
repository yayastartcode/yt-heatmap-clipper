import { useState } from 'react';
import VideoPreview from './VideoPreview';

export default function ClipCard({ clip, jobId }) {
  const [showPreview, setShowPreview] = useState(false);

  const downloadUrl = `/api/download/${jobId}/${clip.filename}`;
  const thumbnailUrl = clip.thumbnail || '/api/thumbnail/' + clip.filename;

  return (
    <>
      <div className="bg-dark-card border border-dark-border rounded-xl overflow-hidden hover:border-accent-blue transition group">
        <div className="relative aspect-video bg-gray-800">
          <img
            src={thumbnailUrl}
            alt={clip.title || `Clip ${clip.index}`}
            className="w-full h-full object-cover"
            onError={(e) => {
              e.target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="225"%3E%3Crect fill="%23334155" width="400" height="225"/%3E%3Ctext fill="%23fff" font-size="20" x="50%25" y="50%25" text-anchor="middle" dominant-baseline="middle"%3ENo Thumbnail%3C/text%3E%3C/svg%3E';
            }}
          />
          <button
            onClick={() => setShowPreview(true)}
            className="absolute inset-0 flex items-center justify-center bg-black/50 opacity-0 group-hover:opacity-100 transition"
          >
            <div className="w-16 h-16 bg-accent-blue rounded-full flex items-center justify-center">
              <svg className="w-8 h-8 text-white ml-1" fill="currentColor" viewBox="0 0 20 20">
                <path d="M6.3 2.841A1.5 1.5 0 004 4.11V15.89a1.5 1.5 0 002.3 1.269l9.344-5.89a1.5 1.5 0 000-2.538L6.3 2.84z" />
              </svg>
            </div>
          </button>
        </div>

        <div className="p-4 space-y-3">
          <div>
            <h3 className="font-medium text-white mb-1">
              {clip.title || `Clip ${clip.index}`}
            </h3>
            <p className="text-sm text-gray-400">
              Duration: {clip.duration || 'N/A'}
            </p>
          </div>

          {clip.description && (
            <p className="text-sm text-gray-500 line-clamp-2">
              {clip.description}
            </p>
          )}

          <a
            href={downloadUrl}
            download
            className="block w-full px-4 py-2 bg-accent-blue hover:bg-blue-600 rounded-lg text-center font-medium transition"
          >
            Download
          </a>
        </div>
      </div>

      {showPreview && (
        <VideoPreview
          src={downloadUrl}
          onClose={() => setShowPreview(false)}
        />
      )}
    </>
  );
}
