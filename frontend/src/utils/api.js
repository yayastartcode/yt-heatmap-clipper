const API_BASE = '/api';

// Map frontend crop mode names to API enum values
const CROP_MODE_MAP = {
  'center': 'none',
  'left': 'facecam_left',
  'right': 'facecam_right',
};

function buildApiPayload(url, options) {
  const payload = {
    url,
    clip_mode: options.clipMode || 'heatmap',
    crop_mode: CROP_MODE_MAP[options.cropMode] || 'none',
    use_subtitle: options.subtitles ?? true,
    whisper_model: options.modelSize || 'small',
    whisper_language: 'id',
    max_clips: options.maxClips || 10,
    min_score: options.minScore || 0.4,
  };
  
  // Add optional fields
  if (options.manualSegments) {
    payload.manual_segments = options.manualSegments;
  }
  
  if (options.splitCount) {
    payload.split_count = options.splitCount;
  }
  
  return payload;
}

export const processVideo = async (url, options) => {
  const payload = buildApiPayload(url, options);
  const response = await fetch(`${API_BASE}/process`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to process video');
  }
  return response.json();
};

export const getJobStatus = async (jobId) => {
  const response = await fetch(`${API_BASE}/status/${jobId}`);
  if (!response.ok) throw new Error('Failed to get job status');
  return response.json();
};

export const getClips = async (jobId) => {
  const response = await fetch(`${API_BASE}/clips/${jobId}`);
  if (!response.ok) throw new Error('Failed to get clips');
  return response.json();
};

export const downloadClip = (jobId, filename) => {
  return `${API_BASE}/download/${jobId}/${filename}`;
};

export const batchProcess = async (urls, options) => {
  const payload = {
    urls,
    clip_mode: options.clipMode || 'heatmap',
    crop_mode: CROP_MODE_MAP[options.cropMode] || 'none',
    use_subtitle: options.subtitles ?? true,
    whisper_model: options.modelSize || 'small',
    whisper_language: 'id',
    max_clips: options.maxClips || 10,
    min_score: options.minScore || 0.4,
  };
  
  // Add optional fields
  if (options.manualSegments) {
    payload.manual_segments = options.manualSegments;
  }
  
  if (options.splitCount) {
    payload.split_count = options.splitCount;
  }
  
  const response = await fetch(`${API_BASE}/batch`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to batch process');
  }
  return response.json();
};
