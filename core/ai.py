"""
AI enhancement module
Generates titles, descriptions, and analyzes content using LLM (enowxai proxy)
"""
import os
import json
import re
from typing import Optional, Dict, List, Callable

import config


def generate_title(
    transcript: str,
    video_context: Optional[Dict] = None,
    progress_callback: Optional[Callable] = None
) -> str:
    """
    Generate catchy title for video clip using AI.
    
    Args:
        transcript: Video transcript text
        video_context: Optional context (duration, score, reason, etc.)
        progress_callback: Optional callback for progress updates
        
    Returns:
        Generated title string
    """
    if not config.AI_TITLE_ENABLED:
        return "Momen Viral"
    
    if progress_callback:
        progress_callback("ai", 0, "Generating title")
    
    # Try to use LLM API
    try:
        title = _generate_with_llm(
            prompt=_build_title_prompt(transcript, video_context),
            max_tokens=100,
            temperature=0.8
        )
        
        # Clean up title
        title = title.strip().strip('"').strip("'")
        
        if progress_callback:
            progress_callback("ai", 100, "Title generated")
        
        return title if title else _generate_title_fallback(transcript)
        
    except Exception as e:
        if progress_callback:
            progress_callback("ai", 100, f"Using fallback title: {str(e)}")
        
        return _generate_title_fallback(transcript)


def generate_description(
    transcript: str,
    title: str = "",
    video_context: Optional[Dict] = None,
    progress_callback: Optional[Callable] = None
) -> str:
    """
    Generate engaging description for video clip using AI.
    
    Args:
        transcript: Video transcript text
        title: Generated title (optional)
        video_context: Optional context (duration, score, etc.)
        progress_callback: Optional callback for progress updates
        
    Returns:
        Generated description string with hashtags
    """
    if not config.AI_DESCRIPTION_ENABLED:
        return ""
    
    if progress_callback:
        progress_callback("ai", 0, "Generating description")
    
    try:
        description = _generate_with_llm(
            prompt=_build_description_prompt(transcript, title, video_context),
            max_tokens=300,
            temperature=0.7
        )
        
        if progress_callback:
            progress_callback("ai", 100, "Description generated")
        
        return description if description else _generate_description_fallback(transcript)
        
    except Exception as e:
        if progress_callback:
            progress_callback("ai", 100, f"Using fallback description: {str(e)}")
        
        return _generate_description_fallback(transcript)


def _generate_with_llm(prompt: str, max_tokens: int = 100, temperature: float = 0.7) -> str:
    """
    Generate text using enowxai LLM proxy.
    
    Args:
        prompt: The prompt to send
        max_tokens: Maximum tokens to generate
        temperature: Sampling temperature
        
    Returns:
        Generated text
    """
    import requests
    
    if not config.LLM_API_URL or not config.LLM_API_KEY:
        raise Exception("LLM API not configured")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {config.LLM_API_KEY}"
    }
    
    payload = {
        "model": config.LLM_MODEL,
        "messages": [
            {"role": "system", "content": "You are a creative content writer for social media. Be concise and engaging."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": temperature
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
    return content.strip()


def _build_title_prompt(transcript: str, context: Optional[Dict] = None) -> str:
    """Build prompt for title generation"""
    
    # Limit transcript length
    transcript_preview = transcript[:800] if len(transcript) > 800 else transcript
    
    context_info = ""
    if context:
        if context.get("reason"):
            context_info = f"\nWhy this clip is interesting: {context['reason']}"
        if context.get("duration"):
            context_info += f"\nClip duration: {context['duration']:.0f} seconds"
    
    prompt = f"""Generate a catchy, clickbait-style title for a short video clip based on this transcript:

Transcript:
{transcript_preview}
{context_info}

Requirements:
- Maximum 80 characters
- Attention-grabbing and clickable
- Use emotional hooks (shocking, funny, surprising, etc.)
- Include relevant keywords
- Suitable for TikTok, Instagram Reels, YouTube Shorts
- In Indonesian language
- NO quotation marks in the title

Generate ONLY the title, nothing else."""
    
    return prompt


def _build_description_prompt(transcript: str, title: str = "", context: Optional[Dict] = None) -> str:
    """Build prompt for description generation"""
    
    # Limit transcript length
    transcript_preview = transcript[:800] if len(transcript) > 800 else transcript
    
    title_info = f"\nTitle: {title}" if title else ""
    
    prompt = f"""Generate an engaging description for a short video clip based on this transcript:
{title_info}

Transcript:
{transcript_preview}

Requirements:
- Maximum 300 characters
- Engaging and informative
- Include 5-7 relevant hashtags at the end
- Suitable for social media (TikTok, Instagram, YouTube Shorts)
- In Indonesian language
- Use emojis sparingly (1-2 max)

Generate ONLY the description with hashtags, nothing else."""
    
    return prompt


def _generate_title_fallback(transcript: str) -> str:
    """Generate title using simple keyword extraction"""
    # Extract first sentence or key phrase
    sentences = transcript.split('.')
    if sentences:
        first_sentence = sentences[0].strip()
        
        # Remove common filler words
        first_sentence = re.sub(r'^(jadi|nah|oke|ok|ya|eh|um|uh)\s+', '', first_sentence, flags=re.IGNORECASE)
        
        if len(first_sentence) > 80:
            first_sentence = first_sentence[:77] + "..."
        
        if first_sentence:
            return first_sentence
    
    return "Momen Viral 🔥"


def _generate_description_fallback(transcript: str) -> str:
    """Generate description using simple summarization"""
    # Take first few sentences
    sentences = [s.strip() for s in transcript.split('.')[:3] if s.strip()]
    description = '. '.join(sentences)
    
    if len(description) > 250:
        description = description[:247] + "..."
    
    # Add generic hashtags
    hashtags = "#viral #trending #shorts #fyp #foryou"
    
    return f"{description}\n\n{hashtags}"


def analyze_content_for_hooks(transcript: str, language: str = "id") -> Dict:
    """
    Analyze content to find hook moments (first 3 seconds that grab attention).
    
    Args:
        transcript: Video transcript text
        language: Language code
        
    Returns:
        Dict with hook analysis
    """
    # Hook indicators
    hook_patterns = {
        "id": [
            r"tau gak",
            r"coba tebak",
            r"rahasia",
            r"fakta",
            r"ternyata",
            r"jangan",
            r"harus",
            r"penting",
            r"wajib",
            r"gila",
            r"wow"
        ],
        "en": [
            r"guess what",
            r"you won't believe",
            r"secret",
            r"fact",
            r"turns out",
            r"don't",
            r"must",
            r"important",
            r"crazy",
            r"wow"
        ]
    }
    
    patterns = hook_patterns.get(language, hook_patterns["en"])
    
    # Check first 100 characters
    first_part = transcript[:100].lower()
    
    hook_score = 0.0
    found_hooks = []
    
    for pattern in patterns:
        if re.search(pattern, first_part):
            hook_score += 0.2
            found_hooks.append(pattern)
    
    # Check for questions in the beginning
    if '?' in first_part:
        hook_score += 0.3
        found_hooks.append("question")
    
    # Check for exclamations
    if '!' in first_part:
        hook_score += 0.2
        found_hooks.append("exclamation")
    
    return {
        "has_hook": hook_score > 0.3,
        "hook_score": min(hook_score, 1.0),
        "hook_elements": found_hooks
    }


def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """
    Extract important keywords from text.
    
    Args:
        text: Input text
        max_keywords: Maximum number of keywords to return
        
    Returns:
        List of keywords
    """
    # Simple keyword extraction
    words = re.findall(r'\b\w+\b', text.lower())
    
    # Remove common stop words
    stop_words = {
        'dan', 'atau', 'yang', 'ini', 'itu', 'di', 'ke', 'dari', 'untuk', 'pada', 'dengan',
        'adalah', 'akan', 'ada', 'juga', 'tidak', 'bisa', 'sudah', 'saya', 'kamu', 'dia',
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
        'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does',
        'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that',
        'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'my', 'your', 'his',
        'her', 'its', 'our', 'their'
    }
    
    keywords = [w for w in words if w not in stop_words and len(w) > 3]
    
    # Count frequency
    word_freq = {}
    for word in keywords:
        word_freq[word] = word_freq.get(word, 0) + 1
    
    # Return top keywords
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return [word for word, freq in sorted_words[:max_keywords]]


def generate_hashtags(keywords: List[str], max_hashtags: int = 7) -> List[str]:
    """
    Generate hashtags from keywords.
    
    Args:
        keywords: List of keywords
        max_hashtags: Maximum number of hashtags
        
    Returns:
        List of hashtags
    """
    # Convert keywords to hashtags
    hashtags = [f"#{word}" for word in keywords[:max_hashtags]]
    
    # Add generic viral hashtags
    generic_tags = ["#viral", "#trending", "#fyp", "#foryou", "#shorts"]
    
    # Combine, remove duplicates, limit to max
    all_tags = hashtags + [tag for tag in generic_tags if tag not in hashtags]
    
    return all_tags[:max_hashtags]


def analyze_sentiment(text: str) -> Dict:
    """
    Analyze sentiment of text.
    
    Args:
        text: Input text
        
    Returns:
        Dict with sentiment analysis
    """
    # Simple sentiment analysis based on keywords
    positive_words = [
        'bagus', 'hebat', 'keren', 'mantap', 'seru', 'lucu', 'senang', 'bahagia',
        'sukses', 'berhasil', 'amazing', 'great', 'awesome', 'good', 'happy', 'love'
    ]
    
    negative_words = [
        'buruk', 'jelek', 'sedih', 'marah', 'kecewa', 'gagal', 'salah',
        'bad', 'terrible', 'sad', 'angry', 'disappointed', 'fail', 'wrong'
    ]
    
    text_lower = text.lower()
    
    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)
    
    total = positive_count + negative_count
    
    if total == 0:
        sentiment = "neutral"
        confidence = 0.5
    elif positive_count > negative_count:
        sentiment = "positive"
        confidence = positive_count / total
    else:
        sentiment = "negative"
        confidence = negative_count / total
    
    return {
        "sentiment": sentiment,
        "confidence": confidence,
        "positive_count": positive_count,
        "negative_count": negative_count
    }


def suggest_clip_improvements(clip_data: Dict) -> List[str]:
    """
    Suggest improvements for a clip based on its data.
    
    Args:
        clip_data: Clip data dict with transcript, duration, etc.
        
    Returns:
        List of improvement suggestions
    """
    suggestions = []
    
    transcript = clip_data.get("text_preview", "")
    duration = clip_data.get("duration", 0)
    
    # Check duration
    if duration < 15:
        suggestions.append("Clip is too short - consider extending to 15-30 seconds")
    elif duration > 60:
        suggestions.append("Clip is too long - consider trimming to under 60 seconds")
    
    # Check for hook
    hook_analysis = analyze_content_for_hooks(transcript)
    if not hook_analysis["has_hook"]:
        suggestions.append("Add a strong hook in the first 3 seconds to grab attention")
    
    # Check for call-to-action
    cta_keywords = ["follow", "like", "subscribe", "comment", "share", "ikuti", "suka", "komen"]
    has_cta = any(keyword in transcript.lower() for keyword in cta_keywords)
    if not has_cta:
        suggestions.append("Consider adding a call-to-action (follow, like, comment)")
    
    # Check sentiment
    sentiment = analyze_sentiment(transcript)
    if sentiment["sentiment"] == "negative" and sentiment["confidence"] > 0.7:
        suggestions.append("Content has negative sentiment - ensure it's intentional")
    
    return suggestions
