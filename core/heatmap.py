"""
Heatmap extraction module
Fetches and parses YouTube 'Most Replayed' heatmap data
"""
import re
import json
import requests
from typing import List, Dict, Optional
from urllib.parse import urlparse, parse_qs

import config


def extract_video_id(url: str) -> Optional[str]:
    """
    Extract the YouTube video ID from a given URL.
    Supports standard YouTube URLs, shortened URLs, and Shorts URLs.
    
    Args:
        url: YouTube video URL
        
    Returns:
        Video ID string or None if invalid
    """
    parsed = urlparse(url)

    if parsed.hostname in ("youtu.be", "www.youtu.be"):
        return parsed.path[1:]

    if parsed.hostname in ("youtube.com", "www.youtube.com"):
        if parsed.path == "/watch":
            return parse_qs(parsed.query).get("v", [None])[0]
        if parsed.path.startswith("/shorts/"):
            return parsed.path.split("/")[2]

    return None


def extract_heatmap_data(video_id: str, min_score: float = None) -> List[Dict]:
    """
    Fetch and parse YouTube 'Most Replayed' heatmap data.
    Returns a list of high-engagement segments sorted by score.
    
    Args:
        video_id: YouTube video ID
        min_score: Minimum intensity score (defaults to config.MIN_SCORE)
        
    Returns:
        List of dicts with keys: start, duration, score
    """
    if min_score is None:
        min_score = config.MIN_SCORE
        
    url = f"https://www.youtube.com/watch?v={video_id}"
    headers = {"User-Agent": config.USER_AGENT}

    try:
        response = requests.get(url, headers=headers, timeout=config.REQUEST_TIMEOUT)
        html = response.text
    except Exception as e:
        print(f"Failed to fetch heatmap data: {e}")
        return []

    # Extract markers from HTML
    match = re.search(
        r'"markers":\s*(\[.*?\])\s*,\s*"?markersMetadata"?',
        html,
        re.DOTALL
    )

    if not match:
        return []

    try:
        markers = json.loads(match.group(1).replace('\\"', '"'))
    except Exception as e:
        print(f"Failed to parse markers: {e}")
        return []

    results = []

    for marker in markers:
        if "heatMarkerRenderer" in marker:
            marker = marker["heatMarkerRenderer"]

        try:
            score = float(marker.get("intensityScoreNormalized", 0))
            if score >= min_score:
                results.append({
                    "start": float(marker["startMillis"]) / 1000,
                    "duration": min(
                        float(marker["durationMillis"]) / 1000,
                        config.MAX_DURATION
                    ),
                    "score": score
                })
        except Exception:
            continue

    # Sort by score (highest first)
    results.sort(key=lambda x: x["score"], reverse=True)
    return results


def get_video_duration(video_id: str) -> int:
    """
    Retrieve the total duration of a YouTube video in seconds.
    
    Args:
        video_id: YouTube video ID
        
    Returns:
        Duration in seconds (defaults to 3600 if unable to fetch)
    """
    import subprocess
    import sys
    
    cmd = [
        sys.executable,
        "-m",
        "yt_dlp",
        "--get-duration",
        f"https://youtu.be/{video_id}"
    ]

    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        time_parts = res.stdout.strip().split(":")

        if len(time_parts) == 2:
            return int(time_parts[0]) * 60 + int(time_parts[1])
        if len(time_parts) == 3:
            return (
                int(time_parts[0]) * 3600 +
                int(time_parts[1]) * 60 +
                int(time_parts[2])
            )
    except Exception as e:
        print(f"Failed to get video duration: {e}")

    return 3600  # Default fallback
