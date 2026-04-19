# SPEC.md - YT Heatmap Clipper Enhanced

## Overview
Enhance the existing yt-heatmap-clipper Python CLI tool into a full-featured web application with API backend, Telegram bot integration, and AI-powered enhancements.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Frontend (Web UI)                   │
│         Next.js / React + Tailwind CSS               │
│         Deploy: Cloudflare Pages                     │
└──────────────────────┬──────────────────────────────┘
                       │ REST API
┌──────────────────────▼──────────────────────────────┐
│                Backend (FastAPI)                      │
│         Python 3.11+ / FastAPI + Celery              │
│         Deploy: VPS (38.45.65.93)                    │
├─────────────────────────────────────────────────────┤
│  Core Engine (enhanced run.py)                       │
│  - Heatmap extraction                               │
│  - Video processing (FFmpeg)                        │
│  - AI Subtitle (Faster-Whisper)                     │
│  - AI Title/Description (LLM)                       │
│  - Thumbnail generation                             │
│  - Auto facecam detection                           │
├─────────────────────────────────────────────────────┤
│  Integrations                                        │
│  - Telegram Bot (send link → get clips)             │
│  - Background job queue (Celery + Redis)            │
│  - File storage (local + optional S3)               │
└─────────────────────────────────────────────────────┘
```

## Phase 1: Core Engine Enhancement (Python Backend)

### 1.1 Refactor to Modular Architecture
- Split monolithic `run.py` into modules:
  - `core/heatmap.py` - Heatmap extraction
  - `core/downloader.py` - Video download
  - `core/processor.py` - FFmpeg video processing
  - `core/subtitle.py` - Whisper subtitle generation
  - `core/detector.py` - Auto facecam detection
  - `core/ai.py` - LLM title/description generation
  - `core/thumbnail.py` - Thumbnail extraction
  - `api/` - FastAPI routes
  - `bot/` - Telegram bot
  - `config.py` - Centralized config

### 1.2 New Features
- **Batch processing**: Accept multiple URLs
- **Auto facecam detection**: Use frame analysis to detect facecam position
- **AI title/description**: Generate engaging titles using LLM
- **Smart thumbnail**: Extract best frame from clip as thumbnail
- **Progress tracking**: Real-time progress via WebSocket
- **Parallel processing**: Multiple clips simultaneously

### 1.3 Configuration
```python
# config.py
OUTPUT_DIR = "clips"
MAX_DURATION = 60
MIN_SCORE = 0.40
MAX_CLIPS = 10
PADDING = 10
WHISPER_MODEL = "small"
WHISPER_LANGUAGE = "id"
# New
PARALLEL_WORKERS = 4
THUMBNAIL_ENABLED = True
AI_TITLE_ENABLED = True
AUTO_DETECT_FACECAM = True
```

## Phase 2: Web UI (Frontend)

### 2.1 Features
- URL input (single + batch)
- Real-time processing progress (WebSocket)
- Preview generated clips in browser
- Download individual or all clips (zip)
- Configuration panel (crop mode, subtitle, model size)
- History of processed videos
- Responsive design (mobile-friendly)

### 2.2 Tech Stack
- React + Vite + Tailwind CSS
- WebSocket for real-time updates
- Video.js for preview player
- Deploy to Cloudflare Pages

## Phase 3: API Backend (FastAPI)

### 3.1 Endpoints
```
POST /api/process          - Submit URL(s) for processing
GET  /api/status/{job_id}  - Get job status
GET  /api/clips/{job_id}   - List generated clips
GET  /api/download/{clip}  - Download clip file
GET  /api/thumbnail/{clip} - Get clip thumbnail
WS   /ws/progress/{job_id} - Real-time progress
POST /api/batch            - Batch process multiple URLs
```

### 3.2 Job Queue
- Celery + Redis for background processing
- Job status: queued → processing → done/failed
- Webhook callback on completion

## Phase 4: Telegram Bot Integration

### 4.1 Flow
1. User sends YouTube link to bot
2. Bot acknowledges, starts processing
3. Progress updates sent as message edits
4. Completed clips sent as video messages
5. Thumbnail + title/description included

### 4.2 Commands
- `/clip <url>` - Process single video
- `/batch <url1> <url2>` - Process multiple
- `/settings` - Configure preferences
- `/status` - Check processing status

## Phase 5: AI Enhancements

### 5.1 Smart Segment Selection
- Combine heatmap data with transcript analysis
- Detect "hook" moments (questions, surprises, reveals)
- Score segments by engagement potential

### 5.2 Auto Facecam Detection
- Analyze first frame for facecam regions
- Use edge detection + face detection (OpenCV)
- Auto-select crop mode based on detection

### 5.3 AI Title & Description
- Transcribe clip content
- Generate catchy title (< 100 chars)
- Generate description with hashtags
- Multi-language support

### 5.4 Thumbnail Generation
- Extract highest-quality frame from clip
- Detect "interesting" frames (motion, expressions)
- Optional: Add text overlay

## Deployment

### Backend (VPS)
- Systemd service for FastAPI
- Redis for job queue
- Nginx reverse proxy
- Subdomain: `clipper.ahliwebmurah.space`

### Frontend (Cloudflare Pages)
- Auto-deploy from GitHub
- Custom domain: `clipper.ahliwebmurah.space` (or separate)

## File Structure (Target)
```
yt-heatmap-clipper/
├── core/
│   ├── __init__.py
│   ├── heatmap.py
│   ├── downloader.py
│   ├── processor.py
│   ├── subtitle.py
│   ├── detector.py
│   ├── ai.py
│   └── thumbnail.py
├── api/
│   ├── __init__.py
│   ├── main.py
│   ├── routes.py
│   ├── models.py
│   └── websocket.py
├── bot/
│   ├── __init__.py
│   └── telegram_bot.py
├── frontend/
│   ├── src/
│   ├── package.json
│   └── vite.config.js
├── config.py
├── worker.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```
