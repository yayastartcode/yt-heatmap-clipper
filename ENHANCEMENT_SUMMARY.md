# YT Heatmap Clipper Enhancement Summary

## Completed Tasks

### ✅ Task 1: Cookie Support for yt-dlp

**Files Modified:**
- `config.py` - Added `COOKIES_FILE = "cookies.txt"` setting
- `core/downloader.py` - Added cookie file support and `--remote-components ejs:github` flag

**Changes:**
- yt-dlp now checks for `cookies.txt` in project root
- If found, passes `--cookies cookies.txt` to yt-dlp
- Added `--remote-components ejs:github` for JS challenge solving
- Helps bypass YouTube bot detection

### ✅ Task 2: LLM Transcript Analysis

**New File Created:**
- `core/transcript.py` (11KB, 350+ lines)

**Features:**
1. **Caption Fetching** (`fetch_captions`)
   - Downloads YouTube auto-generated or manual subtitles using yt-dlp
   - Supports multiple languages (id, en)
   - Parses JSON3 subtitle format into timestamped segments
   - Cookie support for subtitle download

2. **LLM Analysis** (`analyze_transcript_for_clips`)
   - Primary: Uses OpenAI-compatible LLM API to find interesting moments
   - Fallback: Keyword-based heuristic analysis
   - Detects: questions, exclamations, laughter, topic transitions
   - Returns scored clips with reasons and text previews

3. **Heuristic Fallback**
   - Indonesian & English language support
   - Scores segments by marker density
   - Groups nearby segments into 30-60s clips
   - No external API required

**Configuration Added to `config.py`:**
```python
LLM_API_URL = os.environ.get("LLM_API_URL", "")
LLM_API_KEY = os.environ.get("LLM_API_KEY", "")
LLM_MODEL = os.environ.get("LLM_MODEL", "gpt-4o-mini")
TRANSCRIPT_LANGUAGES = ["id", "en"]
```

### ✅ Task 3: API Updates

**Files Modified:**
- `api/models.py`
  - Added `ClipMode` enum: `heatmap`, `transcript`, `manual`, `even_split`
  - Added `ManualSegment` model for manual timestamps
  - Updated `JobRequest` with new fields:
    - `clip_mode` (default: "heatmap")
    - `manual_segments` (optional)
    - `split_count` (optional, default: 5)
  - Updated `BatchJobRequest` with same fields

- `api/processor.py`
  - Refactored `process_video()` to support all 4 clip modes
  - **Heatmap mode**: Original behavior (YouTube engagement data)
  - **Transcript mode**: Uses AI/heuristic transcript analysis
  - **Manual mode**: Uses user-provided timestamps
  - **Even split mode**: Divides video evenly into N clips
  - Added import for `fetch_captions` and `analyze_transcript_for_clips`

- `api/routes.py`
  - Updated batch endpoint to pass new fields

### ✅ Task 4: Frontend Updates

**New Components Created:**

1. **`ClipModeSelector.jsx`** (1.6KB)
   - 4 cards in 2x2 grid (responsive)
   - Emoji icons: 🔥 Heatmap, 🧠 AI Transcript, ✂️ Manual, 📐 Even Split
   - Blue border + glow for selected state
   - Matches dark theme style

2. **`ManualSegments.jsx`** (4.1KB)
   - Add/remove segments dynamically
   - Time inputs in MM:SS format
   - Validation: end > start, max 60s per segment
   - Shows duration for each segment
   - Error messages for invalid inputs

3. **`EvenSplitConfig.jsx`** (1.7KB)
   - Slider for number of clips (2-20)
   - Input for max duration per clip
   - Shows recommended values

**Files Modified:**

- `frontend/src/pages/HomePage.jsx`
  - Added state for: `clipMode`, `manualSegments`, `splitCount`, `maxDuration`
  - Added `ClipModeSelector` above `CropModeSelector`
  - Conditionally renders `ManualSegments` or `EvenSplitConfig`
  - Validation for manual mode (requires at least 1 segment)
  - Passes all new data to API

- `frontend/src/utils/api.js`
  - Updated `buildApiPayload()` to include `clip_mode`, `manual_segments`, `split_count`
  - Updated `batchProcess()` with same fields

### ✅ Task 5: Configuration Updates

**`config.py` additions:**
```python
# Cookie support
COOKIES_FILE = "cookies.txt"

# LLM settings for transcript analysis
LLM_API_URL = os.environ.get("LLM_API_URL", "")
LLM_API_KEY = os.environ.get("LLM_API_KEY", "")
LLM_MODEL = os.environ.get("LLM_MODEL", "gpt-4o-mini")

# Transcript settings
TRANSCRIPT_LANGUAGES = ["id", "en"]
```

## Verification Results

✅ **Frontend Build:** Success (279KB JS, 29KB CSS)
✅ **Python Imports:** All modules import correctly
✅ **Models:** ClipMode enum has all 4 values
✅ **Backward Compatibility:** Heatmap mode still works as default

## Files Created/Modified

### Created (3 files):
1. `core/transcript.py` - Transcript extraction and analysis
2. `frontend/src/components/ClipModeSelector.jsx` - Clip mode selector UI
3. `frontend/src/components/ManualSegments.jsx` - Manual timestamp input
4. `frontend/src/components/EvenSplitConfig.jsx` - Even split configuration

### Modified (7 files):
1. `config.py` - Added LLM and cookie settings
2. `core/downloader.py` - Added cookie support
3. `api/models.py` - Added ClipMode enum and new fields
4. `api/processor.py` - Refactored to support all clip modes
5. `api/routes.py` - Updated batch endpoint
6. `frontend/src/pages/HomePage.jsx` - Integrated new components
7. `frontend/src/utils/api.js` - Updated API payload builder

## Usage Instructions

### 1. Cookie Setup (Optional)
To bypass YouTube bot detection, create `cookies.txt` in project root:
```bash
# Export cookies from browser using extension like "Get cookies.txt"
# Place in: /root/.openclaw/workspace/projects/yt-heatmap-clipper/cookies.txt
```

### 2. LLM Setup (Optional)
For AI transcript analysis, set environment variables:
```bash
export LLM_API_URL="https://api.openai.com/v1/chat/completions"
export LLM_API_KEY="sk-..."
export LLM_MODEL="gpt-4o-mini"
```

Or use any OpenAI-compatible API (Anthropic, local models, etc.)

### 3. Using Clip Modes

**Heatmap Mode (Default):**
- Uses YouTube "Most Replayed" data
- Best for popular videos with engagement data
- No additional setup required

**AI Transcript Mode:**
- Analyzes video captions to find interesting moments
- Works with LLM API or heuristic fallback
- Good for videos with captions/subtitles

**Manual Mode:**
- User specifies exact timestamps
- Full control over clip selection
- Useful for specific segments

**Even Split Mode:**
- Divides video into equal parts
- Good for creating series or highlights
- Configurable clip count and duration

## Technical Notes

- **Python 3.8+ compatible** - Type hints and modern syntax
- **Tailwind v4** - Uses @theme in index.css
- **Dark theme** - All components match existing style (bg-slate-800/50, etc.)
- **Error handling** - Comprehensive try/catch blocks
- **Validation** - Frontend and backend validation for all inputs
- **Backward compatible** - Existing heatmap mode unchanged

## Next Steps

1. Test with real YouTube videos
2. Add cookies.txt if needed for bot detection
3. Configure LLM API for transcript analysis
4. Monitor performance and adjust settings
5. Consider adding more language support for heuristics
