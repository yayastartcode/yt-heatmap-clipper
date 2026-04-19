# YT Heatmap Clipper - Frontend

Modern React web UI for the YT Heatmap Clipper application.

## Tech Stack

- **React 18** - UI framework
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Styling
- **React Router** - Client-side routing
- **React Hot Toast** - Toast notifications
- **WebSocket** - Real-time progress updates

## Features

- 🎬 YouTube URL input with validation
- 🎨 Visual crop mode selector (Center, Left, Right)
- 🎙️ Subtitle configuration with Whisper model selection
- ⚙️ Advanced settings panel
- 📊 Real-time processing progress via WebSocket
- 🎥 Video preview with modal player
- 📥 Individual and bulk clip downloads
- 📜 Processing history
- 🌙 Dark mode by default
- 📱 Fully responsive design

## Development

```bash
# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Project Structure

```
src/
├── App.jsx                 # Main app with routing
├── main.jsx               # Entry point
├── index.css              # Global styles
├── pages/
│   ├── HomePage.jsx       # Main landing page
│   ├── ProcessingPage.jsx # Real-time progress
│   ├── ResultsPage.jsx    # View generated clips
│   └── HistoryPage.jsx    # Past jobs
├── components/
│   ├── Layout.jsx         # App layout with nav
│   ├── URLInput.jsx       # URL input with chips
│   ├── CropModeSelector.jsx # Visual crop mode picker
│   ├── SubtitleConfig.jsx # Subtitle settings
│   ├── ProgressTracker.jsx # WebSocket progress
│   ├── VideoPreview.jsx   # Modal video player
│   ├── ClipCard.jsx       # Clip display card
│   └── SettingsPanel.jsx  # Advanced settings
├── hooks/
│   ├── useWebSocket.js    # WebSocket connection
│   └── useApi.js          # API call wrapper
└── utils/
    └── api.js             # API functions
```

## API Integration

The frontend connects to the FastAPI backend via:

- **REST API**: `/api/*` endpoints
- **WebSocket**: `/ws/progress/{jobId}` for real-time updates

Vite proxy configuration handles routing during development.

## Design System

- **Colors**:
  - Dark bg: `#0f172a`
  - Card bg: `#1e293b`
  - Border: `#334155`
  - Accent blue: `#3b82f6`
  - Accent purple: `#8b5cf6`

- **Typography**: System fonts with gradient text for headings
- **Spacing**: Consistent padding and gaps
- **Animations**: Smooth transitions and hover effects
- **Responsive**: Mobile-first with breakpoints at sm/md/lg

## Deployment

### Cloudflare Pages

```bash
# Build
npm run build

# Deploy (from project root)
wrangler pages deploy dist --project-name=yt-heatmap-clipper
```

### Environment Variables

No environment variables needed - API proxy is configured in `vite.config.js`.

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

## Notes

- WebSocket connection requires backend to be running
- Video preview uses native HTML5 player
- Toast notifications auto-dismiss after 3 seconds
- All API calls include error handling
