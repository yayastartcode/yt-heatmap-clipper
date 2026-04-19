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
import CookieUpload from '../components/CookieUpload';
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
  const [showAdvanced, setShowAdvanced] = useState(false);
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
    <div className="max-w-5xl mx-auto space-y-8">
      {/* Hero Section */}
      <div className="text-center space-y-6 py-12 relative">
        {/* Animated gradient background */}
        <div className="absolute inset-0 bg-gradient-to-r from-blue-500/10 via-purple-500/10 to-blue-500/10 rounded-3xl blur-3xl animate-pulse" />
        
        <div className="relative">
          <h1 className="text-6xl font-bold mb-4 animate-fadeIn">
            <span className="bg-gradient-to-r from-blue-500 via-purple-500 to-blue-500 bg-clip-text text-transparent animate-gradient">
              YT Heatmap Clipper
            </span>
          </h1>
          <p className="text-2xl text-slate-300 mb-6">
            Turn any YouTube video into viral short clips in minutes
          </p>
          
          {/* Trust badges */}
          <div className="flex items-center justify-center gap-6 text-sm text-slate-400">
            <div className="flex items-center gap-2">
              <span className="text-xl">🔥</span>
              <span>AI-Powered</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xl">⚡</span>
              <span>Fast Processing</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xl">🎯</span>
              <span>Smart Detection</span>
            </div>
          </div>
        </div>
      </div>

      {/* Main Form Card */}
      <div className="bg-slate-800/50 backdrop-blur border border-slate-700/50 rounded-2xl p-8 space-y-6 shadow-2xl">
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

        {/* Advanced Settings Collapsible */}
        <div className="border-t border-slate-700/50 pt-6">
          <button
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="w-full flex items-center justify-between text-white hover:text-blue-400 transition-colors"
          >
            <span className="flex items-center gap-2 font-medium">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              Advanced Settings
            </span>
            <svg 
              className={`w-5 h-5 transition-transform ${showAdvanced ? 'rotate-180' : ''}`}
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>

          {showAdvanced && (
            <div className="mt-6 space-y-6 animate-fadeIn">
              <SettingsPanel settings={settings} onSettingsChange={setSettings} />
              <CookieUpload />
            </div>
          )}
        </div>

        {/* Big Process Button */}
        <button
          onClick={handleProcess}
          disabled={processing || urls.length === 0}
          className="w-full py-5 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 disabled:from-slate-700 disabled:to-slate-700 disabled:cursor-not-allowed rounded-xl text-xl font-bold transition-all shadow-2xl hover:shadow-blue-500/50 hover:scale-[1.02] disabled:hover:scale-100 flex items-center justify-center gap-3"
        >
          {processing ? (
            <>
              <div className="w-6 h-6 border-3 border-white border-t-transparent rounded-full animate-spin" />
              Starting...
            </>
          ) : (
            <>
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Generate Clips {urls.length > 0 && `(${urls.length} video${urls.length !== 1 ? 's' : ''})`}
            </>
          )}
        </button>
      </div>

      {/* Features Section */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-slate-800/50 backdrop-blur border border-slate-700/50 rounded-2xl p-6 text-center hover:border-blue-500/50 transition-all">
          <div className="text-4xl mb-3">🧠</div>
          <h3 className="font-semibold text-white mb-2">AI-Powered Detection</h3>
          <p className="text-sm text-slate-400">
            Advanced AI analyzes engagement patterns and transcript to find the most viral moments
          </p>
        </div>

        <div className="bg-slate-800/50 backdrop-blur border border-slate-700/50 rounded-2xl p-6 text-center hover:border-purple-500/50 transition-all">
          <div className="text-4xl mb-3">📱</div>
          <h3 className="font-semibold text-white mb-2">Multiple Crop Modes</h3>
          <p className="text-sm text-slate-400">
            Center crop, facecam split, or custom layouts optimized for TikTok, Reels, and Shorts
          </p>
        </div>

        <div className="bg-slate-800/50 backdrop-blur border border-slate-700/50 rounded-2xl p-6 text-center hover:border-emerald-500/50 transition-all">
          <div className="text-4xl mb-3">💬</div>
          <h3 className="font-semibold text-white mb-2">Auto Subtitles</h3>
          <p className="text-sm text-slate-400">
            Whisper AI generates accurate subtitles in multiple languages with perfect timing
          </p>
        </div>
      </div>
    </div>
  );
}
