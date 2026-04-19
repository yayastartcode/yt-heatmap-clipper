export default function VideoPreview({ src, onClose }) {
  return (
    <div
      className="fixed inset-0 bg-black/90 backdrop-blur-sm flex items-center justify-center z-50 p-4"
      onClick={onClose}
    >
      <div
        className="relative max-w-4xl w-full bg-slate-800 rounded-2xl overflow-hidden border border-slate-700 shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <button
          onClick={onClose}
          className="absolute top-4 right-4 z-10 w-10 h-10 bg-black/70 hover:bg-black/90 rounded-full flex items-center justify-center transition-all text-white shadow-lg"
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
