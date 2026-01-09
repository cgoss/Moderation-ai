"""
Metrics validator for comment validation.

This module implements the MetricsValidator class which provides methods
for validating comments against specific metrics and provides detailed
reasoning for validation results.
"""

from typing import Any, Dict, List, Optional, Callable
import re
from collections import Counter

from .base import Comment, MetricsValidator as AbstractMetricsValidator, Severity
from .standards import Metric


class MetricsValidator(AbstractMetricsValidator):
    """
    Validator for checking comments against specific metrics.

    This class provides detailed validation logic for various metrics
    used in the moderation system, including text analysis, pattern
    matching, and rule-based validation.
    """

    def __init__(self, metrics: Optional[Dict[str, Metric]] = None):
        """
        Initialize metrics validator.

        Args:
            metrics: Dictionary of metrics to validate (optional)
        """
        self.metrics: Dict[str, Metric] = metrics or {}
        self._custom_validators: Dict[str, Callable] = {}

    def validate(self, comment: Comment, metric: str) -> tuple[bool, float, str]:
        """
        Validate a comment against a specific metric.

        Args:
            comment: The comment to validate
            metric: The metric to validate against

        Returns:
            Tuple of (passed, score, reasoning)
        """
        if metric not in self.metrics:
            return True, 0.0, f"Metric '{metric}' not found"

        metric_obj = self.metrics[metric]

        # Check for custom validator
        if metric in self._custom_validators:
            return self._custom_validators[metric](comment, metric_obj)

        # Use default validation logic
        return self._default_validate(comment, metric_obj)

    def validate_all(
        self, comment: Comment, metrics: List[str]
    ) -> Dict[str, tuple[bool, float, str]]:
        """
        Validate a comment against multiple metrics.

        Args:
            comment: The comment to validate
            metrics: List of metrics to validate against

        Returns:
            Dictionary mapping metric names to (passed, score, reasoning) tuples
        """
        results: Dict[str, tuple[bool, float, str]] = {}

        for metric in metrics:
            results[metric] = self.validate(comment, metric)

        return results

    def _default_validate(
        self, comment: Comment, metric: Metric
    ) -> tuple[bool, float, str]:
        """
        Default validation logic for a metric.

        Args:
            comment: The comment to validate
            metric: The metric to validate against

        Returns:
            Tuple of (passed, score, reasoning)
        """
        text = comment.text.lower()

        try:
            pattern = re.compile(metric.check_pattern, re.IGNORECASE)
            matches = pattern.findall(text)

            if matches:
                score = self._calculate_score(matches, text)
                passed = score < metric.threshold
                reasoning = self._generate_reasoning(matches, metric, score)
                return passed, score, reasoning
            else:
                return True, 0.0, f"No violations found for '{metric.name}'"
        except Exception as e:
            return True, 0.0, f"Error validating '{metric.name}': {str(e)}"

    def _calculate_score(self, matches: List, text: str) -> float:
        """
        Calculate a validation score based on matches.

        Args:
            matches: List of pattern matches
            text: The comment text

        Returns:
            Score between 0.0 and 1.0
        """
        if not matches:
            return 0.0

        # Score based on frequency and word count
        word_count = len(text.split())
        match_count = len(matches)

        # Normalize score: more matches in shorter text = higher score
        if word_count > 0:
            score = min(match_count / word_count, 1.0)
        else:
            score = 1.0

        return score

    def _generate_reasoning(self, matches: List, metric: Metric, score: float) -> str:
        """
        Generate human-readable reasoning for validation result.

        Args:
            matches: List of pattern matches
            metric: The metric being validated
            score: The calculated score

        Returns:
            Reasoning string
        """
        if not matches:
            return f"No violations found for '{metric.name}'"

        match_text = ", ".join(str(m)[:20] for m in matches[:3])
        if len(matches) > 3:
            match_text += f" and {len(matches) - 3} more"

        return (
            f"Found {len(matches)} violation(s) for '{metric.name}': "
            f"{match_text}. Score: {score:.2f} (threshold: {metric.threshold})"
        )

    def add_custom_validator(self, metric_name: str, validator: Callable) -> None:
        """
        Add a custom validator for a specific metric.

        Args:
            metric_name: Name of the metric
            validator: Validation function taking (comment, metric) and returning
                      tuple[bool, float, str]
        """
        self._custom_validators[metric_name] = validator

    def remove_custom_validator(self, metric_name: str) -> bool:
        """
        Remove a custom validator.

        Args:
            metric_name: Name of the metric

        Returns:
            True if removed, False if not found
        """
        if metric_name in self._custom_validators:
            del self._custom_validators[metric_name]
            return True
        return False

    def add_metric(self, metric: Metric) -> None:
        """
        Add a new metric to validate against.

        Args:
            metric: The metric to add
        """
        self.metrics[metric.name] = metric

    def remove_metric(self, metric_name: str) -> bool:
        """
        Remove a metric.

        Args:
            metric_name: Name of the metric to remove

        Returns:
            True if removed, False if not found
        """
        if metric_name in self.metrics:
            del self.metrics[metric_name]
            return True
        return False


class TextAnalyzer:
    """
    Utility class for text analysis operations.

    Provides common text analysis functions used across
    the metrics validation system.
    """

    @staticmethod
    def count_words(text: str) -> int:
        """
        Count words in text.

        Args:
            text: The text to analyze

        Returns:
            Number of words
        """
        return len(text.split())

    @staticmethod
    def count_sentences(text: str) -> int:
        """
        Count sentences in text.

        Args:
            text: The text to analyze

        Returns:
            Number of sentences
        """
        sentence_endings = re.compile(r"[.!?]+")
        return len(sentence_endings.findall(text))

    @staticmethod
    def count_links(text: str) -> int:
        """
        Count URLs in text.

        Args:
            text: The text to analyze

        Returns:
            Number of URLs
        """
        url_pattern = re.compile(r"https?://\S+|www\.\S+")
        return len(url_pattern.findall(text))

    @staticmethod
    def count_mentions(text: str) -> int:
        """
        Count user mentions in text.

        Args:
            text: The text to analyze

        Returns:
            Number of mentions
        """
        mention_pattern = re.compile(r"@\w+")
        return len(mention_pattern.findall(text))

    @staticmethod
    def count_hashtags(text: str) -> int:
        """
        Count hashtags in text.

        Args:
            text: The text to analyze

        Returns:
            Number of hashtags
        """
        hashtag_pattern = re.compile(r"#\w+")
        return len(hashtag_pattern.findall(text))

    @staticmethod
    def count_emojis(text: str) -> int:
        """
        Count emojis in text.

        Args:
            text: The text to analyze

        Returns:
            Number of emojis
        """
        emoji_pattern = re.compile(
            "["
            "\U0001f600-\U0001f64f"
            "\U0001f300-\U0001f5ff"
            "\U0001f680-\U0001f6ff"
            "\U0001f1e0-\U0001f1ff"
            "\U00002702-\U000027b0"
            "\U000024c2-\U0001f251"
            "]+",
            flags=re.UNICODE,
        )
        return len(emoji_pattern.findall(text))

    @staticmethod
    def detect_caps_abuse(text: str, threshold: float = 0.7) -> bool:
        """
        Detect excessive use of capital letters.

        Args:
            text: The text to analyze
            threshold: Minimum ratio of caps to consider abuse

        Returns:
            True if caps abuse detected
        """
        if len(text) == 0:
            return False

        alpha_chars = sum(1 for c in text if c.isalpha())
        if alpha_chars == 0:
            return False

        caps_chars = sum(1 for c in text if c.isupper())
        caps_ratio = caps_chars / alpha_chars

        return caps_ratio >= threshold

    @staticmethod
    def detect_repetition(text: str, min_repeats: int = 3) -> bool:
        """
        Detect repeated characters or patterns.

        Args:
            text: The text to analyze
            min_repeats: Minimum number of repeats to flag

        Returns:
            True if repetition detected
        """
        # Check for repeated characters
        char_pattern = re.compile(r"(.)\1{" + str(min_repeats) + ",}")
        if char_pattern.search(text):
            return True

        # Check for repeated words
        words = text.lower().split()
        if len(words) >= min_repeats:
            word_counts = Counter(words)
            for count in word_counts.values():
                if count >= min_repeats:
                    return True

        return False

    @staticmethod
    def calculate_readability(text: str) -> float:
        """
        Calculate a basic readability score (lower is more readable).

        Args:
            text: The text to analyze

        Returns:
            Readability score
        """
        words = TextAnalyzer.count_words(text)
        sentences = TextAnalyzer.count_sentences(text)

        if sentences == 0:
            return 0.0

        # Average sentence length
        avg_sentence_length = words / sentences

        # Simple readability score based on sentence length
        # Shorter sentences = more readable
        if avg_sentence_length <= 10:
            return 0.0
        elif avg_sentence_length <= 20:
            return 0.3
        elif avg_sentence_length <= 30:
            return 0.6
        else:
            return 1.0

    @staticmethod
    def detect_all_caps(text: str) -> bool:
        """
        Detect if text is all caps.

        Args:
            text: The text to analyze

        Returns:
            True if all caps
        """
        if len(text) == 0:
            return False

        alpha_chars = sum(1 for c in text if c.isalpha())
        if alpha_chars == 0:
            return False

        caps_chars = sum(1 for c in text if c.isupper())
        return caps_chars == alpha_chars

    @staticmethod
    def contains_profanity(
        text: str, profanity_list: Optional[List[str]] = None
    ) -> bool:
        """
        Check if text contains profanity.

        Args:
            text: The text to analyze
            profanity_list: List of profanity words (uses defaults if None)

        Returns:
            True if profanity detected
        """
        if profanity_list is None:
            profanity_list = [
                "shit",
                "fuck",
                "damn",
                "ass",
                "bitch",
                "crap",
                "bastard",
                "idiot",
                "stupid",
                "dumb",
                "moron",
            ]

        text_lower = text.lower()
        words = text_lower.split()

        for word in words:
            # Remove punctuation
            clean_word = "".join(c for c in word if c.isalnum())
            if clean_word in profanity_list:
                return True

        return False

    @staticmethod
    def extract_keywords(text: str, top_n: int = 5) -> List[tuple[str, int]]:
        """
        Extract most frequent keywords from text.

        Args:
            text: The text to analyze
            top_n: Number of top keywords to return

        Returns:
            List of (keyword, count) tuples
        """
        words = text.lower().split()

        # Remove common stop words
        stop_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "from",
            "as",
            "is",
            "was",
            "are",
            "were",
            "be",
            "been",
            "being",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "should",
            "could",
            "may",
            "might",
            "must",
            "i",
            "you",
            "he",
            "she",
            "it",
            "we",
            "they",
            "this",
            "that",
            "these",
            "those",
            "my",
            "your",
            "his",
            "her",
            "its",
            "our",
            "their",
        }

        filtered_words = [
            "".join(c for c in word if c.isalnum())
            for word in words
            if word not in stop_words and len(word) > 2
        ]

        word_counts = Counter(filtered_words)
        return word_counts.most_common(top_n)
