"""
AI enhancement module
Generates titles, descriptions, and analyzes transcripts using LLM
"""
import os
import json
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
        video_context: Optional context (duration, score, etc.)
        progress_callback: Optional callback for progress updates
        
    Returns:
        Generated title string
    """
    if not config.AI_TITLE_ENABLED:
        return "Viral Moment"
    
    if progress_callback:
        progress_callback("ai", 0, "Generating title")
    
    # Try to use available LLM API
    try:
        title = _generate_with_llm(
            prompt=_build_title_prompt(transcript, video_context),
            max_length=100
        )
        
        if progress_callback:
            progress_callback("ai", 100, "Title generated")
        
        return title
        
    except Exception as e:
        if progress_callback:
            progress_callback("ai", 100, f"Using fallback title: {str(e)}")
        
        # Fallback: extract key phrases from transcript
        return _generate_title_fallback(transcript)


def generate_description(
    transcript: str,
    video_context: Optional[Dict] = None,
    progress_callback: Optional[Callable] = None
) -> str:
    """
    Generate engaging description for video clip using AI.
    
    Args:
        transcript: Video transcript text
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
            prompt=_build_description_prompt(transcript, video_context),
            max_length=500
        )
        
        if progress_callback:
            progress_callback("ai", 100, "Description generated")
        
        return description
        
    except Exception as e:
        if progress_callback:
            progress_callback("ai", 100, f"Using fallback description: {str(e)}")
        
        # Fallback: simple description
        return _generate_description_fallback(transcript)


def analyze_transcript(
    transcript: str,
    progress_callback: Optional[Callable] = None
) -> Dict:
    """
    Analyze transcript to extract key moments and topics.
    
    Args:
        transcript: Video transcript text
        progress_callback: Optional callback for progress updates
        
    Returns:
        Dict with analysis results (keywords, topics, sentiment, etc.)
    """
    if progress_callback:
        progress_callback("ai", 0, "Analyzing transcript")
    
    analysis = {
        "keywords": _extract_keywords(transcript),
        "topics": _extract_topics(transcript),
        "sentiment": _analyze_sentiment(transcript),
        "hook_moments": _find_hook_moments(transcript)
    }
    
    if progress_callback:
        progress_callback("ai", 100, "Analysis complete")
    
    return analysis


def _generate_with_llm(prompt: str, max_length: int = 100) -> str:
    """
    Generate text using available LLM API.
    Placeholder for actual LLM integration.
    """
    # TODO: Integrate with actual LLM API (OpenAI, Anthropic, local model, etc.)
    # For now, return a placeholder
    
    # Check if OpenAI API key is available
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        try:
            import openai
            openai.api_key = api_key
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a creative content writer for social media."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_length,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        except Exception:
            pass
    
    # Fallback: return placeholder
    return "AI-generated content (LLM not configured)"


def _build_title_prompt(transcript: str, context: Optional[Dict] = None) -> str:
    """Build prompt for title generation"""
    prompt = f"""Generate a catchy, engaging title for a short video clip based on this transcript:

Transcript:
{transcript[:500]}...

Requirements:
- Maximum 100 characters
- Attention-grabbing and clickable
- Include relevant keywords
- Suitable for social media (TikTok, Instagram, YouTube Shorts)
- In Indonesian language

Generate only the title, no explanation."""
    
    return prompt


def _build_description_prompt(transcript: str, context: Optional[Dict] = None) -> str:
    """Build prompt for description generation"""
    prompt = f"""Generate an engaging description for a short video clip based on this transcript:

Transcript:
{transcript[:500]}...

Requirements:
- Maximum 500 characters
- Engaging and informative
- Include 3-5 relevant hashtags
- Suitable for social media
- In Indonesian language

Generate only the description with hashtags, no explanation."""
    
    return prompt


def _generate_title_fallback(transcript: str) -> str:
    """Generate title using simple keyword extraction"""
    # Extract first sentence or key phrase
    sentences = transcript.split('.')
    if sentences:
        first_sentence = sentences[0].strip()
        if len(first_sentence) > 100:
            first_sentence = first_sentence[:97] + "..."
        return first_sentence
    
    return "Momen Viral"


def _generate_description_fallback(transcript: str) -> str:
    """Generate description using simple summarization"""
    # Take first few sentences
    sentences = transcript.split('.')[:3]
    description = '. '.join(s.strip() for s in sentences if s.strip())
    
    # Add generic hashtags
    hashtags = "#viral #trending #shorts"
    
    return f"{description}\n\n{hashtags}"


def _extract_keywords(transcript: str) -> List[str]:
    """Extract important keywords from transcript"""
    # Simple keyword extraction (can be improved with NLP)
    words = transcript.lower().split()
    
    # Remove common words
    stop_words = {'dan', 'atau', 'yang', 'ini', 'itu', 'di', 'ke', 'dari', 'untuk', 'pada', 'dengan'}
    keywords = [w for w in words if w not in stop_words and len(w) > 3]
    
    # Count frequency
    word_freq = {}
    for word in keywords:
        word_freq[word] = word_freq.get(word, 0) + 1
    
    # Return top 10 keywords
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return [word for word, freq in sorted_words[:10]]


def _extract_topics(transcript: str) -> List[str]:
    """Extract main topics from transcript"""
    # Simple topic extraction
    # In a real implementation, use topic modeling (LDA, etc.)
    
    keywords = _extract_keywords(transcript)
    
    # Group related keywords into topics
    # For now, just return top keywords as topics
    return keywords[:5]


def _analyze_sentiment(transcript: str) -> str:
    """Analyze sentiment of transcript"""
    # Simple sentiment analysis
    # In a real implementation, use sentiment analysis model
    
    positive_words = ['bagus', 'hebat', 'keren', 'mantap', 'seru', 'lucu', 'senang']
    negative_words = ['buruk', 'jelek', 'sedih', 'marah', 'kecewa']
    
    transcript_lower = transcript.lower()
    
    positive_count = sum(1 for word in positive_words if word in transcript_lower)
    negative_count = sum(1 for word in negative_words if word in transcript_lower)
    
    if positive_count > negative_count:
        return "positive"
    elif negative_count > positive_count:
        return "negative"
    else:
        return "neutral"


def _find_hook_moments(transcript: str) -> List[Dict]:
    """Find potential hook moments in transcript"""
    # Detect questions, exclamations, and key phrases
    
    hook_patterns = [
        '?',  # Questions
        '!',  # Exclamations
        'wow', 'gila', 'serius', 'nggak percaya', 'luar biasa'
    ]
    
    hooks = []
    sentences = transcript.split('.')
    
    for i, sentence in enumerate(sentences):
        sentence_lower = sentence.lower()
        for pattern in hook_patterns:
            if pattern in sentence_lower:
                hooks.append({
                    "position": i,
                    "text": sentence.strip(),
                    "type": "question" if pattern == '?' else "exclamation"
                })
                break
    
    return hooks


def combine_heatmap_with_transcript(
    heatmap_segments: List[Dict],
    transcript_analysis: Dict
) -> List[Dict]:
    """
    Combine heatmap data with transcript analysis for smart segment selection.
    
    Args:
        heatmap_segments: List of heatmap segments with scores
        transcript_analysis: Transcript analysis results
        
    Returns:
        Enhanced segments with combined scores
    """
    enhanced_segments = []
    
    for segment in heatmap_segments:
        # Start with heatmap score
        combined_score = segment["score"]
        
        # Boost score if segment contains hook moments
        # (This is a simplified implementation)
        
        enhanced_segments.append({
            **segment,
            "combined_score": combined_score,
            "has_hook": False  # Placeholder
        })
    
    # Sort by combined score
    enhanced_segments.sort(key=lambda x: x["combined_score"], reverse=True)
    
    return enhanced_segments
