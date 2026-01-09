"""
Comment summarization module.

This module provides functionality to summarize comments,
both individually and in batches.
"""

from typing import Any, Dict, List, Optional, Tuple
from collections import Counter

from .base import Analyzer
from ..core.base import Comment, AnalysisResult


class Summarizer(Analyzer):
    """
    Analyzer for comment summarization.

    Provides extractive summarization by identifying
    key sentences and important phrases.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize summarizer.

        Args:
            config: Optional configuration
        """
        super().__init__(config)
        self._max_sentences = config.get("max_sentences", 3) if config else 3
        self._min_sentence_length = (
            config.get("min_sentence_length", 5) if config else 5
        )
        self._include_reasoning = (
            config.get("include_reasoning", True) if config else True
        )

    def analyze(self, comment: Comment) -> AnalysisResult:
        """
        Summarize a comment.

        Args:
            comment: The comment to summarize

        Returns:
            AnalysisResult with summary data
        """
        if not self.validate_comment(comment):
            return self._create_error_result(comment, "Invalid comment")

        text = comment.text

        # Extract sentences
        sentences = self._extract_sentences(text)

        # Score sentences by importance
        scored_sentences = self._score_sentences(sentences, text)

        # Select top sentences
        top_sentences = sorted(scored_sentences, key=lambda x: x[1], reverse=True)[
            : self._max_sentences
        ]

        # Build summary
        summary = self._build_summary(top_sentences)

        # Extract key phrases
        key_phrases = self._extract_key_phrases(text)

        # Get summary statistics
        stats = self._get_summary_stats(text, summary)

        data = {
            "summary": summary,
            "original_length": len(text),
            "summary_length": len(summary),
            "compression_ratio": len(summary) / max(1, len(text)),
            "key_phrases": key_phrases,
            "sentence_count": len(sentences),
            "selected_sentences": len(top_sentences),
            "stats": stats,
        }

        confidence = self._calculate_confidence(text, summary)
        return self._create_result(comment, data, confidence=confidence)

    def analyze_batch(self, comments: List[Comment]) -> List[AnalysisResult]:
        """
        Summarize multiple comments.

        Args:
            comments: List of comments to summarize

        Returns:
            List of AnalysisResult objects
        """
        return [self.analyze(comment) for comment in comments]

    def _extract_sentences(self, text: str) -> List[str]:
        """
        Extract sentences from text.

        Args:
            text: The text to process

        Returns:
            List of sentences
        """
        import re

        # Split on sentence boundaries
        sentences = re.split(r"[.!?]+", text)

        # Clean and filter
        cleaned_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) >= self._min_sentence_length:
                cleaned_sentences.append(sentence)

        return cleaned_sentences

    def _score_sentences(
        self, sentences: List[str], full_text: str
    ) -> List[Tuple[str, float]]:
        """
        Score sentences by importance.

        Args:
            sentences: List of sentences
            full_text: Original full text

        Returns:
            List of (sentence, score) tuples
        """
        word_freq = Counter(full_text.lower().split())
        total_words = sum(word_freq.values())

        scored = []

        for sentence in sentences:
            sentence_words = sentence.lower().split()

            if not sentence_words:
                scored.append((sentence, 0.0))
                continue

            # Score based on word frequency (higher = more common)
            word_scores = [word_freq.get(word, 0) for word in sentence_words]
            avg_word_freq = sum(word_scores) / len(word_scores)

            # Normalize
            score = avg_word_freq / max(1, total_words)

            # Boost score for longer sentences
            if len(sentence_words) > 10:
                score *= 1.2
            elif len(sentence_words) > 5:
                score *= 1.1

            scored.append((sentence, score))

        return scored

    def _build_summary(self, scored_sentences: List[Tuple[str, float]]) -> str:
        """
        Build summary from scored sentences.

        Args:
            scored_sentences: List of (sentence, score) tuples

        Returns:
            Summary string
        """
        # Sort by position in original text (rough approximation)
        sentences = [s[0] for s in scored_sentences]

        return " ".join(sentences)

    def _extract_key_phrases(self, text: str) -> List[str]:
        """
        Extract key phrases from text.

        Args:
            text: The text to analyze

        Returns:
            List of key phrases
        """
        import re

        # Extract n-grams (2-3 word phrases)
        words = text.lower().split()
        phrases = []

        # 2-grams
        for i in range(len(words) - 1):
            phrase = f"{words[i]} {words[i + 1]}"
            if len(phrase.split()) == 2:
                phrases.append(phrase)

        # 3-grams
        for i in range(len(words) - 2):
            phrase = f"{words[i]} {words[i + 1]} {words[i + 2]}"
            if len(phrase.split()) == 3:
                phrases.append(phrase)

        # Count phrase frequency
        phrase_counts = Counter(phrases)

        # Get top phrases
        top_phrases = [phrase for phrase, count in phrase_counts.most_common(5)]

        return top_phrases

    def _get_summary_stats(self, original: str, summary: str) -> Dict[str, Any]:
        """
        Get summary statistics.

        Args:
            original: Original text
            summary: Summary text

        Returns:
            Dictionary of statistics
        """
        original_words = len(original.split())
        summary_words = len(summary.split())

        return {
            "original_word_count": original_words,
            "summary_word_count": summary_words,
            "word_reduction": (original_words - summary_words) / max(1, original_words),
            "char_reduction": (len(original) - len(summary)) / max(1, len(original)),
        }

    def _calculate_confidence(self, original: str, summary: str) -> float:
        """
        Calculate confidence in summary.

        Args:
            original: Original text
            summary: Summary text

        Returns:
            Confidence score (0.0 to 1.0)
        """
        if not summary:
            return 0.0

        original_words = set(original.lower().split())
        summary_words = set(summary.lower().split())

        # Word overlap
        overlap = len(original_words & summary_words)
        coverage = overlap / max(1, len(original_words))

        return min(coverage, 1.0)

    def summarize_batch(
        self, comments: List[Comment], max_summary_length: int = 500
    ) -> str:
        """
        Summarize multiple comments into a single summary.

        Args:
            comments: List of comments
            max_summary_length: Maximum length of combined summary

        Returns:
            Combined summary
        """
        results = self.analyze_batch(comments)
        summaries = [
            result.data.get("summary", "") for result in results if result.success
        ]

        # Extract key points from all summaries
        key_points = []
        for summary in summaries:
            points = summary.split(". ")
            key_points.extend(points)

        # Build combined summary
        combined = ". ".join(key_points[:10])

        # Truncate if needed
        if len(combined) > max_summary_length:
            combined = combined[: max_summary_length - 3] + "..."

        return combined

    def get_top_key_phrases(
        self, comments: List[Comment], limit: int = 10
    ) -> List[Tuple[str, int]]:
        """
        Get most common key phrases across comments.

        Args:
            comments: List of comments
            limit: Maximum number of phrases to return

        Returns:
            List of (phrase, count) tuples
        """
        results = self.analyze_batch(comments)
        all_phrases: List[str] = []

        for result in results:
            if result.success:
                phrases = result.data.get("key_phrases", [])
                all_phrases.extend(phrases)

        phrase_counts = Counter(all_phrases)
        return phrase_counts.most_common(limit)
