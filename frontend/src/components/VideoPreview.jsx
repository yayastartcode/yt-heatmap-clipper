import { useEffect, useRef } from 'react';

export default function VideoPreview({ src, title, onClose }) {
  const videoRef = useRef(null);

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') {
        onClose();
      } else if (e.key === ' ' && videoRef.current) {
        e.preventDefault();
        if (videoRef.current.paused) {
          videoRef.current.play();
        } else {
          videoRef.current.pause();
        }
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [onClose]);

  return (
    <div
      className="fixed inset-0 bg-black/95 backdrop-blur-sm flex items-center justify-center z-50 p-4 animate-fadeIn"
      onClick={onClose}
    >
      <div
        className="relative max-w-5xl w-full bg-slate-900 rounded-2xl overflow-hidden border border-slate-700 shadow-2xl animate-scaleIn"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="absolute top-0 left-0 right-0 z-10 bg-gradient-to-b from-black/80 to-transparent p-4 flex items-center justify-between">
          {title && (
            <h3 className="text-white font-medium truncate pr-12">{title}</h3>
          )}
          <button
            onClick={onClose}
            className="ml-auto w-10 h-10 bg-black/70 hover:bg-black/90 rounded-full flex items-center justify-center transition-all text-white shadow-lg hover:scale-110"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Video */}
        <video
          ref={videoRef}
          src={src}
          controls
          autoPlay
          className="w-full"
          controlsList="nodownload"
        />

        {/* Keyboard hints */}
        <div className="absolute bottom-4 left-4 bg-black/70 backdrop-blur rounded-lg px-3 py-2 text-xs text-slate-300 space-y-1">
          <p><kbd className="px-2 py-1 bg-slate-700 rounded">Space</kbd> Play/Pause</p>
          <p><kbd className="px-2 py-1 bg-slate-700 rounded">Esc</kbd> Close</p>
        </div>
      </div>
    </div>
  );
}
