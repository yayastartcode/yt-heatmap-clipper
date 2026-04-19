import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import URLInput from '../components/URLInput';
import ClipModeSelector from '../components/ClipModeSelector';
import CropModeSelector from '../components/CropModeSelector';
import ManualSegments from '../components/ManualSegments';
import EvenSplitConfig from '../components/EvenSplitConfig';
import SubtitleConfig from '../components/SubtitleConfig';
import SettingsPanel from '../components/SettingsPanel';
import { processVideo, batchProcess } from '../utils/api';

export default function HomePage() {
  const navigate = useNavigate();
  const [urls, setUrls] = useState([]);
  const [clipMode, setClipMode] = useState('heatmap');
  const [cropMode, setCropMode] = useState('center');
  const [subtitlesEnabled, setSubtitlesEnabled] = useState(true);
  const [modelSize, setModelSize] = useState('small');
  const [manualSegments, setManualSegments] = useState([]);
  const [splitCount, setSplitCount] = useState(5);
  const [maxDuration, setMaxDuration] = useState(60);
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
    
    // Validate manual mode
    if (clipMode === 'manual' && manualSegments.length === 0) {
      toast.error('Please add at least one manual segment');
      return;
    }

    setProcessing(true);
    const options = {
      clipMode,
      cropMode,
      subtitles: subtitlesEnabled,
      modelSize,
      manualSegments: clipMode === 'manual' ? manualSegments : undefined,
      splitCount: clipMode === 'even_split' ? splitCount : undefined,
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
      const jobId = result.job_id || (Array.isArray(result) ? result[0]?.job_id : undefined);
      if (!jobId) throw new Error('No job ID returned');
      navigate(`/processing/${jobId}`);
    } catch (error) {
      toast.error(error.message || 'Failed to start processing');
      setProcessing(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div className="text-center space-y-4 py-8">
        <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-500 to-purple-500 bg-clip-text text-transparent">
          YT Heatmap Clipper
        </h1>
        <p className="text-xl text-slate-400">
          Extract viral moments from YouTube videos using heatmap data
        </p>
      </div>

      <div className="bg-slate-800/50 backdrop-blur border border-slate-700/50 rounded-2xl p-6 space-y-6">
        <URLInput urls={urls} onUrlsChange={setUrls} />

        <ClipModeSelector selected={clipMode} onSelect={setClipMode} />
        
        {clipMode === 'manual' && (
          <ManualSegments segments={manualSegments} onSegmentsChange={setManualSegments} />
        )}
        
        {clipMode === 'even_split' && (
          <EvenSplitConfig
            splitCount={splitCount}
            onSplitCountChange={setSplitCount}
            maxDuration={maxDuration}
            onMaxDurationChange={setMaxDuration}
          />
        )}

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
          className="w-full py-4 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 disabled:from-slate-700 disabled:to-slate-700 disabled:cursor-not-allowed rounded-xl text-lg font-semibold transition-all shadow-lg"
        >
          {processing ? 'Starting...' : `Process ${urls.length} Video${urls.length !== 1 ? 's' : ''}`}
        </button>
      </div>

      <SettingsPanel settings={settings} onSettingsChange={setSettings} />

      <div className="bg-slate-800/50 backdrop-blur border border-slate-700/50 rounded-2xl p-6">
        <h2 className="text-xl font-semibold mb-4 text-white">How It Works</h2>
        <ol className="space-y-3 text-slate-400">
          <li className="flex gap-3">
            <span className="flex-shrink-0 w-6 h-6 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-sm font-bold text-white">1</span>
            <span>Paste YouTube video URL(s)</span>
          </li>
          <li className="flex gap-3">
            <span className="flex-shrink-0 w-6 h-6 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-sm font-bold text-white">2</span>
            <span>Choose crop mode and subtitle settings</span>
          </li>
          <li className="flex gap-3">
            <span className="flex-shrink-0 w-6 h-6 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-sm font-bold text-white">3</span>
            <span>Click Process and wait for AI to extract viral moments</span>
          </li>
          <li className="flex gap-3">
            <span className="flex-shrink-0 w-6 h-6 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-sm font-bold text-white">4</span>
            <span>Download clips with AI-generated titles and subtitles</span>
          </li>
        </ol>
      </div>
    </div>
  );
}
