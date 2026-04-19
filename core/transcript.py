"""
Transcript extraction and analysis module
Fetches YouTube captions/subtitles with fallback to Whisper transcription
"""
import os
import sys
import json
import subprocess
import re
import time
from typing import List, Dict, Optional
from pathlib import Path

import config
from core.downloader import download_audio_only


def fetch_captions(video_id: str, output_dir: str = "temp") -> Optional[List[Dict]]:
    """
    Fetch YouTube captions/subtitles with fallback chain:
    1. Auto-generated subtitles
    2. Manual subtitles
    3. Whisper transcription of downloaded audio
    
    Args:
        video_id: YouTube video ID
        output_dir: Directory to save subtitle files
        
    Returns:
        List of timestamped segments: [{start, end, text}, ...]
        None if all methods fail
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Try YouTube captions first (auto and manual)
    segments = _fetch_youtube_captions(video_id, output_dir)
    if segments:
        return _merge_short_segments(segments)
    
    print(f"YouTube captions not available for {video_id}, trying Whisper transcription...")
    
    # Fallback to Whisper transcription
    segments = _transcribe_with_whisper(video_id, output_dir)
    if segments:
        return _merge_short_segments(segments)
    
    return None


def _fetch_youtube_captions(video_id: str, output_dir: str) -> Optional[List[Dict]]:
    """
    Fetch YouTube captions using yt-dlp.
    Tries both auto-generated and manual subtitles.
    """
    # Try multiple subtitle formats
    for sub_format in ["json3", "vtt", "srt"]:
        for attempt in range(config.MAX_RETRIES):
            try:
                cmd = [
                    sys.executable, "-m", "yt_dlp",
                    "--write-auto-sub",
                    "--write-sub",  # Also try manual subs
                    "--sub-lang", ",".join(config.TRANSCRIPT_LANGUAGES),
                    "--skip-download",
                    "--sub-format", sub_format,
                    "--remote-components", "ejs:github",
                ]
                
                # Add cookies if available
                cookies_path = Path(config.COOKIES_FILE)
                if cookies_path.exists():
                    cmd.extend(["--cookies", str(cookies_path)])
                
                cmd.extend([
                    "-o", f"{output_dir}/{video_id}",
                    f"https://youtu.be/{video_id}"
                ])
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                # Find downloaded subtitle file
                subtitle_file = _find_subtitle_file(output_dir, video_id, sub_format)
                
                if subtitle_file:
                    # Parse based on format
                    if sub_format == "json3":
                        segments = _parse_json3(subtitle_file)
                    elif sub_format == "vtt":
                        segments = _parse_vtt(subtitle_file)
                    elif sub_format == "srt":
                        segments = _parse_srt(subtitle_file)
                    else:
                        segments = None
                    
                    # Clean up subtitle file
                    subtitle_file.unlink()
                    
                    if segments:
                        return segments
            
            except subprocess.TimeoutExpired:
                if attempt < config.MAX_RETRIES - 1:
                    time.sleep(config.RETRY_DELAY)
                continue
            except Exception as e:
                print(f"Error fetching captions (format={sub_format}, attempt={attempt+1}): {e}")
                if attempt < config.MAX_RETRIES - 1:
                    time.sleep(config.RETRY_DELAY)
                continue
    
    return None


def _find_subtitle_file(output_dir: str, video_id: str, sub_format: str) -> Optional[Path]:
    """Find the downloaded subtitle file."""
    output_path = Path(output_dir)
    
    # Try different language codes
    for lang in config.TRANSCRIPT_LANGUAGES + ["en-orig", "en-US", "id-ID"]:
        # Try auto-generated
        potential_file = output_path / f"{video_id}.{lang}.{sub_format}"
        if potential_file.exists():
            return potential_file
        
        # Try manual
        potential_file = output_path / f"{video_id}.{lang}.{sub_format}"
        if potential_file.exists():
            return potential_file
    
    # Try without language code
    potential_file = output_path / f"{video_id}.{sub_format}"
    if potential_file.exists():
        return potential_file
    
    return None


def _parse_json3(subtitle_file: Path) -> List[Dict]:
    """Parse JSON3 subtitle format."""
    try:
        with open(subtitle_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        segments = []
        events = data.get("events", [])
        
        for event in events:
            if "segs" not in event:
                continue
            
            start_time = event.get("tStartMs", 0) / 1000.0
            duration = event.get("dDurationMs", 0) / 1000.0
            
            # Combine all text segments
            text = "".join(seg.get("utf8", "") for seg in event["segs"])
            text = text.strip()
            
            if text:
                segments.append({
                    "start": start_time,
                    "end": start_time + duration,
                    "text": text
                })
        
        return segments
    except Exception as e:
        print(f"Error parsing JSON3: {e}")
        return []


def _parse_vtt(subtitle_file: Path) -> List[Dict]:
    """Parse VTT subtitle format."""
    try:
        with open(subtitle_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        segments = []
        
        # VTT format: timestamp --> timestamp\ntext
        pattern = r'(\d{2}:\d{2}:\d{2}\.\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}\.\d{3})\s*\n(.*?)(?=\n\n|\Z)'
        matches = re.findall(pattern, content, re.DOTALL)
        
        for start_str, end_str, text in matches:
            start = _parse_timestamp(start_str)
            end = _parse_timestamp(end_str)
            text = re.sub(r'<[^>]+>', '', text).strip()  # Remove HTML tags
            
            if text:
                segments.append({
                    "start": start,
                    "end": end,
                    "text": text
                })
        
        return segments
    except Exception as e:
        print(f"Error parsing VTT: {e}")
        return []


def _parse_srt(subtitle_file: Path) -> List[Dict]:
    """Parse SRT subtitle format."""
    try:
        with open(subtitle_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        segments = []
        
        # SRT format: number\ntimestamp --> timestamp\ntext
        pattern = r'\d+\s*\n(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})\s*\n(.*?)(?=\n\n|\Z)'
        matches = re.findall(pattern, content, re.DOTALL)
        
        for start_str, end_str, text in matches:
            start = _parse_timestamp(start_str.replace(',', '.'))
            end = _parse_timestamp(end_str.replace(',', '.'))
            text = text.strip()
            
            if text:
                segments.append({
                    "start": start,
                    "end": end,
                    "text": text
                })
        
        return segments
    except Exception as e:
        print(f"Error parsing SRT: {e}")
        return []


def _parse_timestamp(timestamp: str) -> float:
    """Parse timestamp string to seconds."""
    # Format: HH:MM:SS.mmm
    parts = timestamp.split(':')
    hours = int(parts[0])
    minutes = int(parts[1])
    seconds = float(parts[2])
    
    return hours * 3600 + minutes * 60 + seconds


def _transcribe_with_whisper(video_id: str, output_dir: str) -> Optional[List[Dict]]:
    """
    Transcribe video using Whisper after downloading audio.
    """
    try:
        from faster_whisper import WhisperModel
        
        # Download audio
        audio_file = Path(output_dir) / f"{video_id}_audio.m4a"
        
        print(f"Downloading audio for transcription...")
        if not download_audio_only(video_id, str(audio_file)):
            print("Failed to download audio")
            return None
        
        print(f"Transcribing with Whisper ({config.WHISPER_MODEL})...")
        
        # Load Whisper model
        model = WhisperModel(
            config.WHISPER_MODEL,
            device=config.WHISPER_DEVICE,
            compute_type=config.WHISPER_COMPUTE_TYPE
        )
        
        # Transcribe
        segments_iter, info = model.transcribe(
            str(audio_file),
            language=config.WHISPER_LANGUAGE,
            beam_size=5
        )
        
        segments = []
        for segment in segments_iter:
            segments.append({
                "start": segment.start,
                "end": segment.end,
                "text": segment.text.strip()
            })
        
        # Clean up audio file
        audio_file.unlink()
        
        print(f"Transcription complete: {len(segments)} segments")
        return segments
    
    except ImportError:
        print("faster-whisper not installed, cannot transcribe")
        return None
    except Exception as e:
        print(f"Whisper transcription failed: {e}")
        return None


def _merge_short_segments(segments: List[Dict], min_duration: float = 5.0) -> List[Dict]:
    """
    Merge very short segments into meaningful chunks.
    
    Args:
        segments: List of segments
        min_duration: Minimum duration for merged segments
        
    Returns:
        List of merged segments
    """
    if not segments:
        return []
    
    merged = []
    current = segments[0].copy()
    
    for i in range(1, len(segments)):
        seg = segments[i]
        current_duration = current["end"] - current["start"]
        
        # If current segment is too short, merge with next
        if current_duration < min_duration:
            # Extend current segment
            current["end"] = seg["end"]
            current["text"] = current["text"] + " " + seg["text"]
        else:
            # Current segment is long enough, save it
            merged.append(current)
            current = seg.copy()
    
    # Add last segment
    merged.append(current)
    
    return merged


def analyze_transcript_for_clips(
    segments: List[Dict],
    max_clips: int = 5,
    language: str = "id"
) -> List[Dict]:
    """
    Analyze transcript to find interesting moments for clips.
    Uses LLM if configured, otherwise falls back to heuristic analysis.
    
    Args:
        segments: List of transcript segments from fetch_captions
        max_clips: Maximum number of clips to return
        language: Language code for analysis
        
    Returns:
        List of clip suggestions: [{start, end, duration, score, reason, text_preview}, ...]
    """
    if not segments:
        return []
    
    # Try LLM analysis first if configured
    if config.LLM_API_URL and config.LLM_API_KEY:
        try:
            return _analyze_with_llm(segments, max_clips, language)
        except Exception as e:
            print(f"LLM analysis failed, using fallback: {e}")
    
    # Fallback to heuristic analysis
    return _analyze_with_heuristics(segments, max_clips, language)


def _analyze_with_llm(
    segments: List[Dict],
    max_clips: int,
    language: str
) -> List[Dict]:
    """
    Analyze transcript using LLM API (enowxai proxy).
    """
    import requests
    
    # Build full transcript (limit to avoid token limits)
    transcript_lines = []
    total_chars = 0
    max_chars = 8000  # Leave room for prompt and response
    
    for seg in segments:
        line = f"[{seg['start']:.1f}s - {seg['end']:.1f}s] {seg['text']}"
        if total_chars + len(line) > max_chars:
            break
        transcript_lines.append(line)
        total_chars += len(line)
    
    full_transcript = "\n".join(transcript_lines)
    
    # Build prompt
    lang_name = "Indonesian" if language == "id" else "English"
    prompt = f"""Analyze this video transcript and identify the {max_clips} most interesting/viral moments suitable for short clips (30-60 seconds each).

Transcript:
{full_transcript}

For each moment, provide:
1. Start time (in seconds)
2. End time (in seconds)  
3. A brief reason why it's interesting
4. A score from 0.0 to 1.0

Focus on:
- Hook moments (first 3 seconds that grab attention)
- Funny or surprising moments
- Emotional peaks (laughter, surprise, anger)
- Key insights or revelations
- Controversial or debate-worthy statements
- Questions and answers

Respond ONLY with valid JSON array (no markdown, no explanation):
[
  {{"start": 120.5, "end": 175.0, "reason": "Funny reaction to unexpected question", "score": 0.95}},
  {{"start": 300.2, "end": 355.8, "reason": "Emotional story about childhood", "score": 0.88}}
]
"""
    
    # Call LLM API
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {config.LLM_API_KEY}"
    }
    
    payload = {
        "model": config.LLM_MODEL,
        "messages": [
            {"role": "system", "content": f"You are a video content analyst. Respond only with valid JSON. Analyze content in {lang_name}."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 2000
    }
    
    response = requests.post(
        config.LLM_API_URL,
        headers=headers,
        json=payload,
        timeout=60
    )
    
    response.raise_for_status()
    result = response.json()
    
    # Extract content
    content = result["choices"][0]["message"]["content"]
    
    # Parse JSON response (remove markdown if present)
    content = re.sub(r'```json\s*', '', content)
    content = re.sub(r'```\s*', '', content)
    content = content.strip()
    
    clips = json.loads(content)
    
    # Enhance with text preview and duration
    for clip in clips:
        clip["duration"] = clip["end"] - clip["start"]
        clip["text_preview"] = _get_text_preview(segments, clip["start"], clip["end"])
    
    return clips[:max_clips]


def _analyze_with_heuristics(
    segments: List[Dict],
    max_clips: int,
    language: str
) -> List[Dict]:
    """
    Analyze transcript using improved keyword-based heuristics.
    """
    # Enhanced markers for different languages
    markers = {
        "id": {
            "questions": ["?", "kenapa", "gimana", "bagaimana", "mengapa", "apa", "siapa", "dimana", "kapan"],
            "exclamations": ["!", "wow", "gila", "serius", "nggak percaya", "luar biasa", "mantap", "keren", "hebat"],
            "laughter": ["haha", "wkwk", "hehe", "hihi", "😂", "🤣", "ngakak", "lucu"],
            "emotions": ["sedih", "senang", "marah", "kaget", "terkejut", "bahagia", "kesal"],
            "hooks": ["jadi", "nah", "tau gak", "coba tebak", "rahasia", "fakta", "ternyata"],
            "controversy": ["debat", "kontroversi", "salah", "benar", "setuju", "tidak setuju"]
        },
        "en": {
            "questions": ["?", "why", "how", "what", "when", "where", "who", "which"],
            "exclamations": ["!", "wow", "amazing", "insane", "unbelievable", "incredible", "omg", "no way"],
            "laughter": ["haha", "lol", "lmao", "😂", "🤣", "hilarious", "funny"],
            "emotions": ["sad", "happy", "angry", "shocked", "surprised", "excited", "upset"],
            "hooks": ["so", "guess what", "secret", "fact", "turns out", "actually", "here's the thing"],
            "controversy": ["debate", "controversial", "wrong", "right", "agree", "disagree", "argument"]
        }
    }
    
    lang_markers = markers.get(language, markers["en"])
    
    # Score each segment
    scored_segments = []
    
    for i, seg in enumerate(segments):
        text_lower = seg["text"].lower()
        score = 0.0
        reasons = []
        
        # Hook moments (especially at the beginning)
        if i < 3:  # First few segments
            hook_count = sum(1 for marker in lang_markers["hooks"] if marker in text_lower)
            if hook_count > 0:
                score += 0.5
                reasons.append("strong hook")
        
        # Questions
        question_count = sum(1 for marker in lang_markers["questions"] if marker in text_lower)
        if question_count > 0:
            score += 0.3 * min(question_count, 3)
            reasons.append("engaging questions")
        
        # Exclamations
        exclamation_count = sum(1 for marker in lang_markers["exclamations"] if marker in text_lower)
        if exclamation_count > 0:
            score += 0.4 * min(exclamation_count, 3)
            reasons.append("high energy")
        
        # Laughter
        laughter_count = sum(1 for marker in lang_markers["laughter"] if marker in text_lower)
        if laughter_count > 0:
            score += 0.4 * min(laughter_count, 2)
            reasons.append("funny moment")
        
        # Emotions
        emotion_count = sum(1 for marker in lang_markers["emotions"] if marker in text_lower)
        if emotion_count > 0:
            score += 0.3 * min(emotion_count, 2)
            reasons.append("emotional")
        
        # Controversy
        controversy_count = sum(1 for marker in lang_markers["controversy"] if marker in text_lower)
        if controversy_count > 0:
            score += 0.3
            reasons.append("controversial")
        
        # Boost for longer segments (more content)
        duration = seg["end"] - seg["start"]
        if duration > 10:
            score += 0.15
        
        if score > 0:
            scored_segments.append({
                "index": i,
                "start": seg["start"],
                "end": seg["end"],
                "text": seg["text"],
                "score": min(score, 1.0),
                "reasons": reasons
            })
    
    # Sort by score
    scored_segments.sort(key=lambda x: x["score"], reverse=True)
    
    # Group nearby segments into clips (30-60s)
    clips = []
    used_indices = set()
    
    for seg in scored_segments:
        if seg["index"] in used_indices:
            continue
        
        # Expand to create 30-60s clips
        clip_start = seg["start"]
        clip_end = seg["end"]
        clip_indices = {seg["index"]}
        
        # Look ahead
        for j in range(seg["index"] + 1, min(seg["index"] + 15, len(segments))):
            if j in used_indices:
                break
            if segments[j]["end"] - clip_start > 60:
                break
            clip_end = segments[j]["end"]
            clip_indices.add(j)
        
        # Look behind
        for j in range(seg["index"] - 1, max(seg["index"] - 15, -1), -1):
            if j in used_indices:
                break
            if clip_end - segments[j]["start"] > 60:
                break
            clip_start = segments[j]["start"]
            clip_indices.add(j)
        
        duration = clip_end - clip_start
        
        # Ensure minimum duration
        if duration < 15:
            continue
        
        # Ensure maximum duration
        if duration > 60:
            clip_end = clip_start + 60
        
        clips.append({
            "start": clip_start,
            "end": clip_end,
            "duration": clip_end - clip_start,
            "score": seg["score"],
            "reason": ", ".join(seg["reasons"]) if seg["reasons"] else "interesting moment",
            "text_preview": _get_text_preview(segments, clip_start, clip_end)
        })
        
        used_indices.update(clip_indices)
        
        if len(clips) >= max_clips:
            break
    
    return clips


def _get_text_preview(segments: List[Dict], start: float, end: float, max_length: int = 150) -> str:
    """Get text preview for a time range."""
    texts = []
    for seg in segments:
        if seg["start"] >= start and seg["end"] <= end:
            texts.append(seg["text"])
    
    preview = " ".join(texts)
    if len(preview) > max_length:
        preview = preview[:max_length-3] + "..."
    
    return preview
