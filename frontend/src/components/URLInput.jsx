import { useState } from 'react';
import VideoThumbnail from './VideoThumbnail';

export default function URLInput({ onUrlsChange, urls = [] }) {
  const [inputValue, setInputValue] = useState('');
  const [showPreview, setShowPreview] = useState(false);

  const isValidYouTubeUrl = (url) => {
    return url.includes('youtube.com') || url.includes('youtu.be');
  };

  const handleAdd = () => {
    const trimmed = inputValue.trim();
    if (trimmed && isValidYouTubeUrl(trimmed) && !urls.includes(trimmed)) {
      onUrlsChange([...urls, trimmed]);
      setInputValue('');
      setShowPreview(false);
    }
  };

  const handleRemove = (urlToRemove) => {
    onUrlsChange(urls.filter(url => url !== urlToRemove));
  };

  const handlePaste = (e) => {
    const pastedText = e.clipboardData.getData('text');
    if (isValidYouTubeUrl(pastedText)) {
      e.preventDefault();
      setInputValue(pastedText);
      setShowPreview(true);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleAdd();
    }
  };

  const handleInputChange = (e) => {
    const value = e.target.value;
    setInputValue(value);
    setShowPreview(isValidYouTubeUrl(value));
  };

  return (
    <div className="space-y-4">
      <div className="space-y-3">
        <div className="flex gap-2">
          <div className="flex-1 relative">
            <div className="absolute left-4 top-1/2 -translate-y-1/2 text-red-500">
              <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
              </svg>
            </div>
            <input
              type="text"
              value={inputValue}
              onChange={handleInputChange}
              onPaste={handlePaste}
              onKeyPress={handleKeyPress}
              placeholder="Paste YouTube URL here..."
              className="w-full pl-14 pr-4 py-4 bg-slate-800 border-2 border-slate-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all text-white placeholder-slate-500 text-lg"
            />
          </div>
          <button
            onClick={handleAdd}
            disabled={!inputValue.trim() || !isValidYouTubeUrl(inputValue)}
            className="px-8 py-4 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 disabled:from-slate-700 disabled:to-slate-700 disabled:cursor-not-allowed rounded-xl font-medium transition-all shadow-lg"
          >
            Add
          </button>
        </div>

        {showPreview && inputValue && isValidYouTubeUrl(inputValue) && (
          <VideoThumbnail url={inputValue} />
        )}
      </div>

      {urls.length > 0 && (
        <div className="space-y-2">
          <p className="text-sm text-slate-400">{urls.length} video{urls.length !== 1 ? 's' : ''} added:</p>
          <div className="space-y-2">
            {urls.map((url, index) => (
              <div
                key={index}
                className="flex items-center gap-3 p-3 bg-slate-800/50 border border-slate-700/50 rounded-xl backdrop-blur hover:border-slate-600 transition-all"
              >
                <span className="flex-shrink-0 w-6 h-6 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-sm font-bold text-white">
                  {index + 1}
                </span>
                <span className="flex-1 text-sm text-slate-300 truncate">{url}</span>
                <button
                  onClick={() => handleRemove(url)}
                  className="flex-shrink-0 text-red-400 hover:text-red-300 transition-colors p-1"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
