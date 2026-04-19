# TASKS.md - YT Heatmap Clipper Enhanced

## Task Assignment Strategy
Split into 3 parallel sub-agents:
- **Agent 1**: Core Engine Refactor + Enhancement (Python backend)
- **Agent 2**: FastAPI Backend + WebSocket + Telegram Bot
- **Agent 3**: Web UI Frontend (React + Vite + Tailwind)

---

## Agent 1: Core Engine Refactor + AI Enhancement

### Task 1.1: Modular Refactor
- [x] Create `core/` package structure
- [x] Extract `core/heatmap.py` from run.py (heatmap extraction logic)
- [x] Extract `core/downloader.py` (yt-dlp download logic)
- [x] Extract `core/processor.py` (FFmpeg video processing)
- [x] Extract `core/subtitle.py` (Faster-Whisper subtitle)
- [x] Create `config.py` (centralized configuration)
- [x] Update `run.py` to use new modules (backward compatible CLI)
- [x] Test: CLI still works identically

### Task 1.2: New Core Features
- [x] Batch processing support (multiple URLs)
- [x] Parallel clip processing (concurrent FFmpeg)
- [x] Progress callback system (for WebSocket integration)
- [x] Smart thumbnail extraction (best frame from clip)
- [x] `core/thumbnail.py` - extract frame at peak engagement moment

### Task 1.3: AI Features
- [x] `core/detector.py` - Auto facecam detection using OpenCV
- [x] `core/ai.py` - AI title/description generation
- [x] Smart segment selection (heatmap + transcript analysis)
- [x] Watermark support (optional overlay)
- [x] Background music overlay (optional)

### Task 1.4: Requirements & Config
- [x] Update `requirements.txt` with all new deps
- [x] Create `config.py` with all settings
- [x] Update `.gitignore`

---

## Agent 2: FastAPI Backend + Telegram Bot

### Task 2.1: FastAPI Setup
- [x] Create `api/main.py` (FastAPI app)
- [x] Create `api/models.py` (Pydantic schemas)
- [x] Create `api/routes.py` (REST endpoints)
- [x] CORS configuration for frontend

### Task 2.2: API Endpoints
- [x] `POST /api/process` - Submit URL for processing
- [x] `GET /api/status/{job_id}` - Job status
- [x] `GET /api/clips/{job_id}` - List clips for job
- [x] `GET /api/download/{job_id}/{filename}` - Download clip
- [x] `GET /api/thumbnail/{job_id}/{filename}` - Get thumbnail
- [x] `POST /api/batch` - Batch process

### Task 2.3: WebSocket
- [x] `api/websocket.py` - Real-time progress
- [x] `WS /ws/progress/{job_id}` - Progress stream
- [x] Integration with core engine progress callbacks

### Task 2.4: Job Queue
- [x] Background task processing (asyncio-based, no Redis needed for MVP)
- [x] Job state management (in-memory + file-based)
- [x] Cleanup old jobs

### Task 2.5: Telegram Bot
- [x] `bot/telegram_bot.py`
- [x] `/clip <url>` command
- [x] `/batch <url1> <url2>` command
- [x] `/settings` command
- [x] Progress updates via message edits
- [x] Send completed clips as video messages

### Task 2.6: Deployment Config
- [x] `worker.py` - Entry point for backend
- [x] Systemd service file
- [x] Nginx config for reverse proxy

---

## Agent 3: Web UI Frontend

### Task 3.1: Project Setup
- [x] Initialize React + Vite + Tailwind in `frontend/`
- [x] Configure proxy to backend API
- [x] Setup routing (React Router)

### Task 3.2: Pages & Components
- [x] **Home Page**: URL input, crop mode selector, subtitle toggle
- [x] **Processing Page**: Real-time progress (WebSocket)
- [x] **Results Page**: Video previews, download buttons
- [x] **History Page**: Past processed videos
- [x] **Settings Page**: Default preferences

### Task 3.3: Core Components
- [x] `URLInput` - Single + batch URL input
- [x] `CropModeSelector` - Visual crop mode picker
- [x] `ProgressTracker` - Real-time progress bars
- [x] `VideoPreview` - Video player with controls
- [x] `ClipCard` - Clip info card (thumbnail, title, download)
- [x] `SettingsPanel` - Configuration panel

### Task 3.4: Features
- [x] WebSocket integration for live progress
- [x] Download individual clips
- [x] Download all as ZIP
- [x] Responsive design (mobile-first)
- [x] Dark mode
- [x] Toast notifications

### Task 3.5: Polish
- [x] Loading states & skeletons
- [x] Error handling & user feedback
- [x] SEO meta tags
- [x] PWA manifest (optional)

---

## Integration & Deployment (After all agents complete)
- [ ] Integration testing (frontend ↔ backend)
- [ ] Deploy backend to VPS
- [ ] Deploy frontend to Cloudflare Pages
- [ ] Setup subdomain `clipper.ahliwebmurah.space`
- [ ] End-to-end testing
- [ ] Update README.md
