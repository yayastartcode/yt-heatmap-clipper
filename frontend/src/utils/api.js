const API_BASE = '/api';

export const processVideo = async (url, options) => {
  const response = await fetch(`${API_BASE}/process`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url, ...options })
  });
  if (!response.ok) throw new Error('Failed to process video');
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
  const response = await fetch(`${API_BASE}/batch`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ urls, ...options })
  });
  if (!response.ok) throw new Error('Failed to batch process');
  return response.json();
};
