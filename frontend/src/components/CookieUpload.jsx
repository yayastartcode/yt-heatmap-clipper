import { useState, useRef } from 'react';
import { uploadCookies } from '../utils/api';
import toast from 'react-hot-toast';

export default function CookieUpload() {
  const [status, setStatus] = useState(null); // null, 'loaded', 'error'
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef(null);

  const handleFileSelect = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    try {
      await uploadCookies(file);
      setStatus('loaded');
      toast.success('Cookies uploaded successfully');
    } catch (err) {
      setStatus('error');
      toast.error(err.message || 'Failed to upload cookies');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <label className="text-sm font-medium text-white">YouTube Cookies (Optional)</label>
        {status === 'loaded' && (
          <span className="text-xs text-emerald-400 flex items-center gap-1">
            ✅ Cookies loaded
          </span>
        )}
        {status === 'error' && (
          <span className="text-xs text-red-400 flex items-center gap-1">
            ❌ Upload failed
          </span>
        )}
      </div>

      <input
        ref={fileInputRef}
        type="file"
        accept=".txt"
        onChange={handleFileSelect}
        className="hidden"
      />

      <button
        onClick={() => fileInputRef.current?.click()}
        disabled={uploading}
        className="w-full px-4 py-3 bg-slate-800 border border-slate-700 hover:border-slate-600 rounded-xl text-sm transition-all disabled:opacity-50 disabled:cursor-not-allowed text-left flex items-center justify-between"
      >
        <span className="text-slate-300">
          {uploading ? 'Uploading...' : 'Upload cookies.txt'}
        </span>
        <svg className="w-5 h-5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
        </svg>
      </button>

      <p className="text-xs text-slate-500">
        Upload YouTube cookies to access age-restricted or private videos. Export cookies using a browser extension.
      </p>
    </div>
  );
}
