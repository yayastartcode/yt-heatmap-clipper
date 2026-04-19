import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import URLInput from '../components/URLInput';
import CropModeSelector from '../components/CropModeSelector';
import SubtitleConfig from '../components/SubtitleConfig';
import SettingsPanel from '../components/SettingsPanel';
import { processVideo, batchProcess } from '../utils/api';

export default function HomePage() {
  const navigate = useNavigate();
  const [urls, setUrls] = useState([]);
  const [cropMode, setCropMode] = useState('center');
  const [subtitlesEnabled, setSubtitlesEnabled] = useState(true);
  const [modelSize, setModelSize] = useState('small');
  const [settings, setSettings] = useState({
    maxClips: 10,
    minScore: 0.4,
    maxDuration: 60,
    autoDetectFacecam: true,
    aiTitles: true,
  });
  const [processing, setProcessing] = useState(false);

  const handleProcess = async () => {
    if (urls.length === 0) {
      toast.error('Please add at least one YouTube URL');
      return;
    }

    setProcessing(true);
    const options = {
      cropMode,
      subtitles: subtitlesEnabled,
      modelSize,
      ...settings,
    };

    try {
      let result;
      if (urls.length === 1) {
        result = await processVideo(urls[0], options);
      } else {
        result = await batchProcess(urls, options);
      }

      toast.success('Processing started!');
      navigate(`/processing/${result.jobId}`);
    } catch (error) {
      toast.error(error.message || 'Failed to start processing');
      setProcessing(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div className="text-center space-y-4">
        <h1 className="text-5xl font-bold bg-gradient-to-r from-accent-blue to-accent-purple bg-clip-text text-transparent">
          YT Heatmap Clipper
        </h1>
        <p className="text-xl text-gray-400">
          Extract viral moments from YouTube videos using heatmap data
        </p>
      </div>

      <div className="bg-dark-card border border-dark-border rounded-xl p-6 space-y-6">
        <URLInput urls={urls} onUrlsChange={setUrls} />

        <CropModeSelector selected={cropMode} onSelect={setCropMode} />

        <SubtitleConfig
          enabled={subtitlesEnabled}
          onEnabledChange={setSubtitlesEnabled}
          modelSize={modelSize}
          onModelSizeChange={setModelSize}
        />

        <button
          onClick={handleProcess}
          disabled={processing || urls.length === 0}
          className="w-full py-4 bg-gradient-to-r from-accent-blue to-accent-purple hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed rounded-xl text-lg font-semibold transition"
        >
          {processing ? 'Starting...' : `Process ${urls.length} Video${urls.length !== 1 ? 's' : ''}`}
        </button>
      </div>

      <SettingsPanel settings={settings} onSettingsChange={setSettings} />

      <div className="bg-dark-card border border-dark-border rounded-xl p-6">
        <h2 className="text-xl font-semibold mb-4">How It Works</h2>
        <ol className="space-y-3 text-gray-400">
          <li className="flex gap-3">
            <span className="flex-shrink-0 w-6 h-6 bg-accent-blue rounded-full flex items-center justify-center text-sm font-bold">1</span>
            <span>Paste YouTube video URL(s)</span>
          </li>
          <li className="flex gap-3">
            <span className="flex-shrink-0 w-6 h-6 bg-accent-blue rounded-full flex items-center justify-center text-sm font-bold">2</span>
            <span>Choose crop mode and subtitle settings</span>
          </li>
          <li className="flex gap-3">
            <span className="flex-shrink-0 w-6 h-6 bg-accent-blue rounded-full flex items-center justify-center text-sm font-bold">3</span>
            <span>Click Process and wait for AI to extract viral moments</span>
          </li>
          <li className="flex gap-3">
            <span className="flex-shrink-0 w-6 h-6 bg-accent-blue rounded-full flex items-center justify-center text-sm font-bold">4</span>
            <span>Download clips with AI-generated titles and subtitles</span>
          </li>
        </ol>
      </div>
    </div>
  );
}
