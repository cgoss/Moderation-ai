"""
Comment categorization module.

This module provides functionality to categorize comments
into topics and themes based on content analysis.
"""

from typing import Any, Dict, List, Optional, Tuple
from collections import Counter

from .base import Analyzer
from ..core.base import Comment, AnalysisResult


class Categorizer(Analyzer):
    """
    Analyzer for comment categorization.

    Categorizes comments into topics and themes using
    keyword-based approach with confidence scoring.
    """

    # Topic categories with keywords
    TOPIC_CATEGORIES = {
        "tech": [
            "software",
            "app",
            "code",
            "programming",
            "developer",
            "api",
            "technology",
            "tech",
            "digital",
            "hardware",
            "update",
            "version",
            "feature",
            "bug",
            "fix",
        ],
        "entertainment": [
            "movie",
            "music",
            "game",
            "video",
            "show",
            "entertainment",
            "fun",
            "funny",
            "cool",
            "amazing",
        ],
        "politics": [
            "politics",
            "government",
            "policy",
            "election",
            "democrat",
            "republican",
            "congress",
            "president",
            "vote",
            "campaign",
            "political",
            "legislation",
        ],
        "sports": [
            "sport",
            "team",
            "game",
            "player",
            "coach",
            "score",
            "win",
            "loss",
            "championship",
            "league",
        ],
        "business": [
            "business",
            "company",
            "market",
            "stock",
            "investment",
            "economy",
            "finance",
            "startup",
            "entrepreneur",
            "profit",
            "revenue",
            "customer",
            "product",
        ],
        "science": [
            "science",
            "research",
            "study",
            "experiment",
            "discovery",
            "theory",
            "hypothesis",
            "data",
            "analysis",
            "scientific",
            "laboratory",
            "finding",
        ],
        "health": [
            "health",
            "medical",
            "doctor",
            "medicine",
            "treatment",
            "symptom",
            "disease",
            "wellness",
            "fitness",
            "exercise",
            "diet",
            "nutrition",
        ],
        "education": [
            "education",
            "school",
            "student",
            "teacher",
            "learn",
            "study",
            "course",
            "university",
            "college",
            "knowledge",
            "academic",
            "curriculum",
        ],
    }

    # Content type categories
    CONTENT_TYPES = {
        "question": [
            "?",
            "how",
            "what",
            "when",
            "where",
            "why",
            "who",
            "which",
            "can someone",
            "anyone know",
        ],
        "opinion": [
            "i think",
            "in my opinion",
            "imo",
            "imho",
            "believe",
            "feel that",
            "seems to me",
        ],
        "complaint": [
            "problem",
            "issue",
            "broken",
            "not working",
            "frustrating",
            "disappointed",
            "unhappy",
            "fix this",
            "why not",
            "should be",
        ],
        "compliment": [
            "great",
            "awesome",
            "love",
            "excellent",
            "amazing",
            "wonderful",
            "good job",
            "well done",
        ],
        "suggestion": [
            "should",
            "could",
            "would be nice",
            "suggest",
            "recommend",
            "consider",
            "add",
        ],
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize categorizer.

        Args:
            config: Optional configuration
        """
        super().__init__(config)
        self._multi_label = config.get("multi_label", False) if config else False
        self._min_matches = config.get("min_matches", 2) if config else 2

    def analyze(self, comment: Comment) -> AnalysisResult:
        """
        Categorize a comment.

        Args:
            comment: The comment to categorize

        Returns:
            AnalysisResult with category data
        """
        if not self.validate_comment(comment):
            return self._create_error_result(comment, "Invalid comment")

        text = self.preprocess_text(comment.text)
        words = text.lower().split()

        # Categorize by topic
        topic, topic_confidence = self._categorize_topic(words)

        # Categorize by content type
        content_type, type_confidence = self._categorize_content_type(text)

        # Categorize by length
        length_category = self._categorize_length(len(text))

        # Get secondary categories if multi-label enabled
        secondary_categories = []
        if self._multi_label:
            secondary_categories = self._get_secondary_categories(words, topic)

        data = {
            "primary_topic": topic,
            "topic_confidence": topic_confidence,
            "secondary_topics": secondary_categories,
            "content_type": content_type,
            "type_confidence": type_confidence,
            "length_category": length_category,
            "word_count": len(words),
            "multi_label": self._multi_label,
        }

        confidence = (topic_confidence + type_confidence) / 2
        return self._create_result(comment, data, confidence=confidence)

    def analyze_batch(self, comments: List[Comment]) -> List[AnalysisResult]:
        """
        Categorize multiple comments.

        Args:
            comments: List of comments to categorize

        Returns:
            List of AnalysisResult objects
        """
        return [self.analyze(comment) for comment in comments]

    def _categorize_topic(self, words: List[str]) -> Tuple[str, float]:
        """
        Categorize comment by topic.

        Args:
            words: List of words

        Returns:
            Tuple of (topic, confidence)
        """
        topic_scores: Dict[str, int] = {}

        for topic, keywords in self.TOPIC_CATEGORIES.items():
            matches = sum(1 for word in words if word in keywords)
            if matches >= self._min_matches:
                topic_scores[topic] = matches

        if not topic_scores:
            return "general", 0.0

        # Get top topic
        top_topic = max(topic_scores.keys(), key=lambda k: topic_scores[k])
        max_matches = topic_scores[top_topic]

        # Calculate confidence based on match ratio
        confidence = min(max_matches / max(5, len(words)), 1.0)
        return top_topic, confidence

    def _categorize_content_type(self, text: str) -> Tuple[str, float]:
        """
        Categorize comment by content type.

        Args:
            text: The comment text

        Returns:
            Tuple of (content_type, confidence)
        """
        type_scores: Dict[str, int] = {}
        text_lower = text.lower()

        for content_type, indicators in self.CONTENT_TYPES.items():
            matches = sum(1 for indicator in indicators if indicator in text_lower)
            if matches > 0:
                type_scores[content_type] = matches

        if not type_scores:
            return "general", 0.0

        # Get top type
        top_type = max(type_scores.keys(), key=lambda k: type_scores[k])
        max_matches = type_scores[top_type]

        # Calculate confidence
        confidence = min(max_matches / max(1, len(text) / 20), 1.0)
        return top_type, confidence

    def _categorize_length(self, length: int) -> str:
        """
        Categorize comment by length.

        Args:
            length: Comment length in characters

        Returns:
            Length category
        """
        if length <= 50:
            return "very_short"
        elif length <= 100:
            return "short"
        elif length <= 250:
            return "medium"
        elif length <= 500:
            return "long"
        else:
            return "very_long"

    def _get_secondary_categories(
        self, words: List[str], primary_topic: str
    ) -> List[str]:
        """
        Get secondary categories for multi-label classification.

        Args:
            words: List of words
            primary_topic: The primary topic assigned

        Returns:
            List of secondary topics
        """
        secondary = []
        threshold = self._min_matches - 1

        for topic, keywords in self.TOPIC_CATEGORIES.items():
            if topic == primary_topic:
                continue

            matches = sum(1 for word in words if word in keywords)
            if matches >= threshold:
                secondary.append(topic)

        return sorted(
            secondary,
            key=lambda t: -sum(1 for w in words if w in self.TOPIC_CATEGORIES[t]),
        )[:3]

    def get_category_distribution(
        self, comments: List[Comment]
    ) -> Dict[str, Dict[str, float]]:
        """
        Get distribution of categories across comments.

        Args:
            comments: List of comments

        Returns:
            Dictionary with topic and content_type distributions
        """
        results = self.analyze_batch(comments)

        topic_counts: Counter = Counter()
        type_counts: Counter = Counter()

        for result in results:
            if result.success:
                topic = result.data.get("primary_topic", "unknown")
                content_type = result.data.get("content_type", "unknown")

                topic_counts[topic] += 1
                type_counts[content_type] += 1

        total = len(results)
        if total == 0:
            return {"topics": {}, "types": {}}

        return {
            "topics": {topic: count / total for topic, count in topic_counts.items()},
            "types": {
                content_type: count / total
                for content_type, count in type_counts.items()
            },
        }

    def get_top_topics(
        self, comments: List[Comment], limit: int = 10
    ) -> List[Tuple[str, int]]:
        """
        Get most common topics across comments.

        Args:
            comments: List of comments
            limit: Maximum number of topics to return

        Returns:
            List of (topic, count) tuples
        """
        results = self.analyze_batch(comments)
        topic_counts: Counter = Counter()

        for result in results:
            if result.success:
                topic = result.data.get("primary_topic", "unknown")
                topic_counts[topic] += 1

        return topic_counts.most_common(limit)
