import { useState } from 'react';

export default function URLInput({ onUrlsChange, urls = [] }) {
  const [inputValue, setInputValue] = useState('');

  const isValidYouTubeUrl = (url) => {
    return url.includes('youtube.com') || url.includes('youtu.be');
  };

  const handleAdd = () => {
    const trimmed = inputValue.trim();
    if (trimmed && isValidYouTubeUrl(trimmed) && !urls.includes(trimmed)) {
      onUrlsChange([...urls, trimmed]);
      setInputValue('');
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
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleAdd();
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onPaste={handlePaste}
          onKeyPress={handleKeyPress}
          placeholder="Paste YouTube URL here..."
          className="flex-1 px-4 py-3 bg-dark-card border border-dark-border rounded-lg focus:outline-none focus:border-accent-blue transition"
        />
        <button
          onClick={handleAdd}
          disabled={!inputValue.trim() || !isValidYouTubeUrl(inputValue)}
          className="px-6 py-3 bg-accent-blue hover:bg-blue-600 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-lg font-medium transition"
        >
          Add URL
        </button>
      </div>

      {urls.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {urls.map((url, index) => (
            <div
              key={index}
              className="flex items-center gap-2 px-3 py-2 bg-dark-card border border-dark-border rounded-lg"
            >
              <span className="text-sm text-gray-300 truncate max-w-xs">{url}</span>
              <button
                onClick={() => handleRemove(url)}
                className="text-red-400 hover:text-red-300 transition"
              >
                ✕
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
