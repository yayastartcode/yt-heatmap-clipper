import { useState, useEffect, useRef } from 'react';

export const useWebSocket = (jobId) => {
  const [progress, setProgress] = useState(0);
  const [clipStatuses, setClipStatuses] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState(null);
  const ws = useRef(null);

  useEffect(() => {
    if (!jobId) return;

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/progress/${jobId}`;
    
    ws.current = new WebSocket(wsUrl);

    ws.current.onopen = () => {
      setIsConnected(true);
      setError(null);
    };

    ws.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.progress !== undefined) setProgress(data.progress);
        if (data.clips) setClipStatuses(data.clips);
      } catch (err) {
        console.error('WebSocket message error:', err);
      }
    };

    ws.current.onerror = (err) => {
      setError('WebSocket connection error');
      console.error('WebSocket error:', err);
    };

    ws.current.onclose = () => {
      setIsConnected(false);
    };

    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  }, [jobId]);

  return { progress, clipStatuses, isConnected, error };
};
