"""
Transcript extraction and analysis module
Fetches YouTube captions/subtitles and analyzes them for interesting moments
"""
import os
import sys
import json
import subprocess
import re
from typing import List, Dict, Optional
from pathlib import Path

import config


def fetch_captions(video_id: str, output_dir: str = "temp") -> Optional[List[Dict]]:
    """
    Fetch YouTube captions/subtitles using yt-dlp.
    
    Args:
        video_id: YouTube video ID
        output_dir: Directory to save subtitle files
        
    Returns:
        List of timestamped segments: [{start, end, text}, ...]
        None if captions not available
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Build yt-dlp command
    cmd = [
        sys.executable, "-m", "yt_dlp",
        "--write-auto-sub",
        "--sub-lang", ",".join(config.TRANSCRIPT_LANGUAGES),
        "--skip-download",
        "--sub-format", "json3",
        "--remote-components", "ejs:github",
    ]
    
    # Add cookie file BEFORE the URL
    cookies_path = getattr(config, 'COOKIES_FILE', 'cookies.txt')
    if os.path.exists(cookies_path):
        cmd.extend(["--cookies", cookies_path])
    
    cmd.extend([
        "-o", f"{output_dir}/{video_id}",
        f"https://youtu.be/{video_id}"
    ])
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # Find the downloaded subtitle file
        subtitle_file = None
        for lang in config.TRANSCRIPT_LANGUAGES:
            potential_file = Path(output_dir) / f"{video_id}.{lang}.json3"
            if potential_file.exists():
                subtitle_file = potential_file
                break
        
        if not subtitle_file:
            print(f"No subtitle file found for video {video_id}")
            return None
        
        # Parse JSON3 subtitle format
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
        
        # Clean up subtitle file
        subtitle_file.unlink()
        
        return segments
        
    except subprocess.TimeoutExpired:
        print(f"Timeout fetching captions for {video_id}")
        return None
    except Exception as e:
        print(f"Error fetching captions: {e}")
        return None


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
    Analyze transcript using LLM API (OpenAI-compatible).
    """
    import requests
    
    # Build full transcript
    full_transcript = "\n".join([
        f"[{seg['start']:.1f}s - {seg['end']:.1f}s] {seg['text']}"
        for seg in segments
    ])
    
    # Build prompt
    prompt = f"""Analyze this video transcript and identify the {max_clips} most interesting/viral moments suitable for short clips (30-60 seconds each).

Transcript:
{full_transcript[:4000]}  # Limit to avoid token limits

For each moment, provide:
1. Start time (in seconds)
2. End time (in seconds)
3. A brief reason why it's interesting
4. A score from 0.0 to 1.0

Focus on:
- Funny or surprising moments
- Questions and answers
- Emotional reactions
- Key insights or revelations
- Dramatic moments

Respond in JSON format:
[
  {{"start": 120.5, "end": 175.0, "reason": "Funny reaction", "score": 0.95}},
  ...
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
            {"role": "system", "content": "You are a video content analyst. Respond only with valid JSON."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    response = requests.post(
        config.LLM_API_URL,
        headers=headers,
        json=payload,
        timeout=30
    )
    
    response.raise_for_status()
    result = response.json()
    
    # Extract content
    content = result["choices"][0]["message"]["content"]
    
    # Parse JSON response
    # Remove markdown code blocks if present
    content = re.sub(r'```json\s*', '', content)
    content = re.sub(r'```\s*', '', content)
    
    clips = json.loads(content)
    
    # Enhance with text preview
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
    Analyze transcript using keyword-based heuristics.
    """
    # Define markers for different languages
    markers = {
        "id": {
            "questions": ["?", "kenapa", "gimana", "bagaimana", "mengapa", "apa", "siapa"],
            "exclamations": ["!", "wow", "gila", "serius", "nggak percaya", "luar biasa", "mantap"],
            "laughter": ["haha", "wkwk", "hehe", "hihi", "😂", "🤣"],
            "transitions": ["anyway", "jadi", "nah", "terus", "kemudian", "lalu"]
        },
        "en": {
            "questions": ["?", "why", "how", "what", "when", "where", "who"],
            "exclamations": ["!", "wow", "amazing", "insane", "unbelievable", "incredible"],
            "laughter": ["haha", "lol", "lmao", "😂", "🤣"],
            "transitions": ["anyway", "so", "then", "next", "now"]
        }
    }
    
    lang_markers = markers.get(language, markers["en"])
    
    # Score each segment
    scored_segments = []
    
    for i, seg in enumerate(segments):
        text_lower = seg["text"].lower()
        score = 0.0
        reasons = []
        
        # Check for questions
        question_count = sum(1 for marker in lang_markers["questions"] if marker in text_lower)
        if question_count > 0:
            score += 0.3 * min(question_count, 3)
            reasons.append("contains questions")
        
        # Check for exclamations
        exclamation_count = sum(1 for marker in lang_markers["exclamations"] if marker in text_lower)
        if exclamation_count > 0:
            score += 0.4 * min(exclamation_count, 3)
            reasons.append("high energy")
        
        # Check for laughter
        laughter_count = sum(1 for marker in lang_markers["laughter"] if marker in text_lower)
        if laughter_count > 0:
            score += 0.3 * min(laughter_count, 2)
            reasons.append("funny moment")
        
        # Check for transitions (potential topic change)
        transition_count = sum(1 for marker in lang_markers["transitions"] if marker in text_lower)
        if transition_count > 0:
            score += 0.2
            reasons.append("topic transition")
        
        # Boost score for longer segments (more content)
        duration = seg["end"] - seg["start"]
        if duration > 5:
            score += 0.1
        
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
    
    # Group nearby segments into clips
    clips = []
    used_indices = set()
    
    for seg in scored_segments:
        if seg["index"] in used_indices:
            continue
        
        # Expand to include nearby segments (create 30-60s clips)
        clip_start = seg["start"]
        clip_end = seg["end"]
        clip_indices = {seg["index"]}
        
        # Look ahead
        for j in range(seg["index"] + 1, min(seg["index"] + 10, len(segments))):
            if j in used_indices:
                break
            if segments[j]["end"] - clip_start > 60:
                break
            clip_end = segments[j]["end"]
            clip_indices.add(j)
        
        # Look behind
        for j in range(seg["index"] - 1, max(seg["index"] - 10, -1), -1):
            if j in used_indices:
                break
            if clip_end - segments[j]["start"] > 60:
                break
            clip_start = segments[j]["start"]
            clip_indices.add(j)
        
        duration = clip_end - clip_start
        
        # Ensure minimum duration
        if duration < 10:
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


def _get_text_preview(segments: List[Dict], start: float, end: float) -> str:
    """
    Get text preview for a time range.
    """
    texts = []
    for seg in segments:
        if seg["start"] >= start and seg["end"] <= end:
            texts.append(seg["text"])
    
    preview = " ".join(texts)
    if len(preview) > 100:
        preview = preview[:97] + "..."
    
    return preview
