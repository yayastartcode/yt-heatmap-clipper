import { useState } from 'react';

export default function VideoPreview({ src, onClose }) {
  return (
    <div
      className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4"
      onClick={onClose}
    >
      <div
        className="relative max-w-4xl w-full bg-dark-card rounded-xl overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        <button
          onClick={onClose}
          className="absolute top-4 right-4 z-10 w-10 h-10 bg-black/50 hover:bg-black/70 rounded-full flex items-center justify-center transition"
        >
          ✕
        </button>
        <video
          src={src}
          controls
          autoPlay
          className="w-full"
        />
      </div>
    </div>
  );
}
