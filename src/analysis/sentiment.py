"""
Sentiment and tone analysis module.

This module provides sentiment analysis functionality including
polarity detection, subjectivity scoring, and tone analysis.
"""

from typing import Any, Dict, List, Optional, Tuple
import re
from collections import Counter

from .base import Analyzer
from ..core.base import Comment, AnalysisResult, Sentiment


class SentimentAnalyzer(Analyzer):
    """
    Analyzer for sentiment and tone analysis.

    Uses rule-based approach for sentiment detection with
    support for basic emotion analysis.
    """

    # Positive words
    POSITIVE_WORDS = {
        "good",
        "great",
        "awesome",
        "excellent",
        "amazing",
        "wonderful",
        "fantastic",
        "love",
        "like",
        "enjoy",
        "happy",
        "pleased",
        "satisfied",
        "delighted",
        "excited",
        "positive",
        "helpful",
        "useful",
        "beneficial",
        "valuable",
        "informative",
        "interesting",
        "engaging",
        "thanks",
        "thank",
        "appreciate",
        "brilliant",
        "perfect",
        "outstanding",
        "superb",
        "magnificent",
        "marvelous",
        "best",
        "favorite",
        "recommend",
        "agree",
        "agreeing",
        "beautiful",
        "nice",
        "cool",
        "fun",
        "hilarious",
        "funny",
    }

    # Negative words
    NEGATIVE_WORDS = {
        "bad",
        "terrible",
        "awful",
        "horrible",
        "worst",
        "hate",
        "dislike",
        "hate",
        "disappointed",
        "frustrated",
        "annoyed",
        "angry",
        "upset",
        "sad",
        "unhappy",
        "useless",
        "worthless",
        "boring",
        "dull",
        "stupid",
        "idiotic",
        "ridiculous",
        "pathetic",
        "disappointing",
        "unhelpful",
        "useless",
        "waste",
        "garbage",
        "trash",
        "crap",
        "shit",
        "sucks",
        "fail",
        "failure",
        "disgusting",
        "offensive",
        "rude",
        "mean",
        "harmful",
        "dangerous",
        "scary",
        "worried",
        "concerned",
        "negative",
        "poor",
        "weak",
        "broken",
        "wrong",
        "incorrect",
    }

    # Emotion keywords
    EMOTION_KEYWORDS = {
        "joy": ["happy", "joy", "excited", "delighted", "thrilled", "ecstatic"],
        "sadness": ["sad", "depressed", "unhappy", "miserable", "heartbroken"],
        "anger": ["angry", "furious", "irate", "outraged", "mad", "livid"],
        "fear": ["afraid", "scared", "terrified", "anxious", "worried", "nervous"],
        "surprise": ["surprised", "shocked", "amazed", "astonished", "stunned"],
        "disgust": ["disgusted", "revolted", "repulsed", "sickened"],
    }

    # Tone indicators
    TONE_INDICATORS = {
        "formal": [
            "respectfully",
            "regarding",
            "concerning",
            "furthermore",
            "additionally",
        ],
        "informal": ["lol", "omg", "haha", "wow", "yeah", "cool", "awesome"],
        "sarcastic": ["totally", "sure", "whatever", "great", "just", "obviously"],
        "aggressive": ["stupid", "idiot", "ridiculous", "pathetic", "shut up"],
        "respectful": ["please", "thank", "appreciate", "respect", "agree"],
        "questioning": ["why", "how", "what", "when", "where", "?"],
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize sentiment analyzer.

        Args:
            config: Optional configuration
        """
        super().__init__(config)
        self._case_sensitive = config.get("case_sensitive", False) if config else False
        self._min_confidence = config.get("min_confidence", 0.1) if config else 0.1

    def analyze(self, comment: Comment) -> AnalysisResult:
        """
        Analyze sentiment of a comment.

        Args:
            comment: The comment to analyze

        Returns:
            AnalysisResult with sentiment data
        """
        if not self.validate_comment(comment):
            return self._create_error_result(comment, "Invalid comment")

        text = self.preprocess_text(comment.text)
        words = text.split()

        # Calculate sentiment
        polarity = self._calculate_polarity(words)
        subjectivity = self._calculate_subjectivity(text)
        sentiment = self._classify_sentiment(polarity)

        # Analyze emotions
        emotions = self._detect_emotions(words)
        dominant_emotion = self._get_dominant_emotion(emotions)

        # Analyze tone
        tone = self._detect_tone(words)

        data = {
            "sentiment": sentiment.value,
            "polarity": polarity,
            "subjectivity": subjectivity,
            "confidence": min(abs(polarity) + 0.5, 1.0),
            "emotions": emotions,
            "dominant_emotion": dominant_emotion,
            "tone": tone,
            "word_count": len(words),
        }

        confidence = min(abs(polarity) + 0.5, 1.0)
        return self._create_result(comment, data, confidence=confidence)

    def analyze_batch(self, comments: List[Comment]) -> List[AnalysisResult]:
        """
        Analyze sentiment of multiple comments.

        Args:
            comments: List of comments to analyze

        Returns:
            List of AnalysisResult objects
        """
        return [self.analyze(comment) for comment in comments]

    def _calculate_polarity(self, words: List[str]) -> float:
        """
        Calculate sentiment polarity.

        Args:
            words: List of words

        Returns:
            Polarity score between -1.0 (negative) and 1.0 (positive)
        """
        positive_count = 0
        negative_count = 0

        for word in words:
            word_lower = word.lower() if not self._case_sensitive else word

            if word_lower in self.POSITIVE_WORDS:
                positive_count += 1
            elif word_lower in self.NEGATIVE_WORDS:
                negative_count += 1

        total = positive_count + negative_count

        if total == 0:
            return 0.0

        return (positive_count - negative_count) / total

    def _calculate_subjectivity(self, text: str) -> float:
        """
        Calculate subjectivity of text.

        Args:
            text: The text to analyze

        Returns:
            Subjectivity score between 0.0 (objective) and 1.0 (subjective)
        """
        # Check for subjective indicators
        subjective_indicators = [
            "i think",
            "i believe",
            "i feel",
            "in my opinion",
            "seems like",
            "probably",
            "maybe",
            "possibly",
            "personally",
            "subjectively",
            "basically",
        ]

        text_lower = text.lower()
        matches = sum(
            1 for indicator in subjective_indicators if indicator in text_lower
        )

        # Normalize by length
        score = min(matches / max(1, len(text) / 100), 1.0)
        return score

    def _classify_sentiment(self, polarity: float) -> Sentiment:
        """
        Classify sentiment based on polarity.

        Args:
            polarity: Polarity score

        Returns:
            Sentiment classification
        """
        if polarity > 0.1:
            return Sentiment.POSITIVE
        elif polarity < -0.1:
            return Sentiment.NEGATIVE
        else:
            return Sentiment.NEUTRAL

    def _detect_emotions(self, words: List[str]) -> Dict[str, float]:
        """
        Detect emotions in text.

        Args:
            words: List of words

        Returns:
            Dictionary mapping emotions to confidence scores
        """
        emotions: Dict[str, int] = {}

        for word in words:
            word_lower = word.lower() if not self._case_sensitive else word

            for emotion, keywords in self.EMOTION_KEYWORDS.items():
                if word_lower in keywords:
                    emotions[emotion] = emotions.get(emotion, 0) + 1

        # Normalize to confidence scores
        total = sum(emotions.values())
        if total == 0:
            return {}

        return {emotion: count / total for emotion, count in emotions.items()}

    def _get_dominant_emotion(self, emotions: Dict[str, float]) -> Optional[str]:
        """
        Get the dominant emotion.

        Args:
            emotions: Dictionary of emotions with confidence scores

        Returns:
            Dominant emotion or None
        """
        if not emotions:
            return None

        # Fix type checker issue by using explicit key parameter
        return max(emotions.keys(), key=lambda k: emotions[k])

    def _detect_tone(self, words: List[str]) -> Dict[str, float]:
        """
        Detect tone indicators in text.

        Args:
            words: List of words

        Returns:
            Dictionary mapping tones to confidence scores
        """
        tone_scores: Dict[str, int] = {}

        for word in words:
            word_lower = word.lower() if not self._case_sensitive else word

            for tone, indicators in self.TONE_INDICATORS.items():
                if word_lower in indicators:
                    tone_scores[tone] = tone_scores.get(tone, 0) + 1

        # Normalize to confidence scores
        total = sum(tone_scores.values())
        if total == 0:
            return {"neutral": 1.0}

        return {tone: count / total for tone, count in tone_scores.items()}

    def get_sentiment_distribution(self, comments: List[Comment]) -> Dict[str, float]:
        """
        Get distribution of sentiments across multiple comments.

        Args:
            comments: List of comments

        Returns:
            Dictionary mapping sentiment types to percentages
        """
        results = self.analyze_batch(comments)
        sentiment_counts = Counter()

        for result in results:
            if result.success:
                sentiment_counts[result.data.get("sentiment", "unknown")] += 1

        total = len(results)
        if total == 0:
            return {}

        return {
            sentiment.value: count / total
            for sentiment, count in sentiment_counts.items()
        }

    def get_average_polarity(self, comments: List[Comment]) -> float:
        """
        Get average polarity across multiple comments.

        Args:
            comments: List of comments

        Returns:
            Average polarity score
        """
        results = self.analyze_batch(comments)
        polarities = [
            result.data.get("polarity", 0.0) for result in results if result.success
        ]

        if not polarities:
            return 0.0

        return sum(polarities) / len(polarities)

    def get_trending_emotions(
        self, comments: List[Comment], top_n: int = 5
    ) -> List[Tuple[str, float]]:
        """
        Get trending emotions across multiple comments.

        Args:
            comments: List of comments
            top_n: Number of top emotions to return

        Returns:
            List of (emotion, confidence) tuples
        """
        results = self.analyze_batch(comments)
        emotion_counts: Counter[str] = Counter()

        for result in results:
            if result.success:
                emotion = result.data.get("dominant_emotion")
                if emotion:
                    emotion_counts[emotion] += 1

        total = sum(emotion_counts.values())
        if total == 0:
            return []

        # Calculate percentages and sort
        emotion_percentages = [
            (emotion, count / total)
            for emotion, count in emotion_counts.most_common(top_n)
        ]

        return emotion_percentages
