"""
Content ideation module.

This module provides functionality to suggest content
ideas based on community feedback and discussions.
"""

from typing import Any, Dict, List, Optional, Tuple
from collections import Counter, defaultdict

from .base import Analyzer
from ..core.base import Comment, AnalysisResult


class ContentIdeator(Analyzer):
    """
    Analyzer for content ideation.

    Analyzes comments to suggest content ideas and
    identify topics that the community wants to see.
    """

    # Request patterns
    REQUEST_PATTERNS = [
        r"\b(more|another|next|future)\s+(content|video|post|article)",
        r"\b(wish|hope|want|need)\s+(to see|would like)",
        r"\b(make|create|do)\s+(a video|a tutorial|a guide)",
        r"\b(tutorial|guide|how to|explain)\s+(please|can someone)",
    ]

    # Topic indicators
    TOPIC_INDICATORS = {
        "tutorial": ["tutorial", "guide", "how to", "learn", "explain"],
        "product_review": ["review", "comparison", "vs", "versus", "rating"],
        "news": ["news", "update", "announcement", "breaking"],
        "entertainment": ["funny", "meme", "joke", "entertainment"],
        "discussion": ["discussion", "opinion", "thoughts", "take on"],
        "help": ["help", "question", "issue", "problem", "stuck"],
        "feedback": ["suggestion", "improvement", "feedback", "idea"],
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize content ideator.

        Args:
            config: Optional configuration
        """
        super().__init__(config)
        self._min_requests = config.get("min_requests", 5) if config else 5
        self._min_score = config.get("min_score", 0.6) if config else 0.6

    def analyze(self, comment: Comment) -> AnalysisResult:
        """
        Analyze a comment for content ideation.

        Args:
            comment: The comment to analyze

        Returns:
            AnalysisResult with content ideation data
        """
        if not self.validate_comment(comment):
            return self._create_error_result(comment, "Invalid comment")

        text = comment.text

        # Check for content requests
        is_request = self._is_content_request(text)

        # Extract topic
        topic = self._extract_topic(text)

        # Extract key themes
        themes = self._extract_themes(text)

        # Classify content type
        content_type = self._classify_content_type(text)

        # Calculate ideation score
        score = self._calculate_ideation_score(text, is_request, topic, themes)

        data = {
            "is_request": is_request,
            "content_type": content_type,
            "topic": topic,
            "themes": themes,
            "ideation_score": score,
            "length": len(text),
            "word_count": len(text.split()),
        }

        confidence = score
        return self._create_result(comment, data, confidence=confidence)

    def analyze_batch(self, comments: List[Comment]) -> List[AnalysisResult]:
        """
        Analyze multiple comments for content ideation.

        Args:
            comments: List of comments to analyze

        Returns:
            List of AnalysisResult objects
        """
        return [self.analyze(comment) for comment in comments]

    def _is_content_request(self, text: str) -> bool:
        """
        Check if text contains a content request.

        Args:
            text: The text to check

        Returns:
            True if content request detected
        """
        text_lower = text.lower()

        for pattern in self.REQUEST_PATTERNS:
            import re

            if re.search(pattern, text_lower):
                return True

        return False

    def _extract_topic(self, text: str) -> Optional[str]:
        """
        Extract the main topic from text.

        Args:
            text: The text to analyze

        Returns:
            Detected topic or None
        """
        text_lower = text.lower()

        for topic, indicators in self.TOPIC_INDICATORS.items():
            for indicator in indicators:
                if indicator in text_lower:
                    return topic

        return None

    def _extract_themes(self, text: str) -> List[str]:
        """
        Extract key themes from text.

        Args:
            text: The text to analyze

        Returns:
            List of themes
        """
        words = text.lower().split()

        # Filter out common words
        stop_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "is",
            "are",
            "was",
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
            "could",
        }

        themes = [word for word in words if word not in stop_words and len(word) > 3]

        return themes[:10]

    def _classify_content_type(self, text: str) -> str:
        """
        Classify the content type.

        Args:
            text: The text to classify

        Returns:
            Content type classification
        """
        text_lower = text.lower()

        # Check for question
        if "?" in text:
            return "question"

        # Check for feedback
        feedback_words = ["suggest", "improve", "better", "should", "add", "feature"]
        if any(word in text_lower for word in feedback_words):
            return "feedback"

        # Check for complaint
        complaint_words = ["problem", "issue", "broken", "not working", "bug"]
        if any(word in text_lower for word in complaint_words):
            return "complaint"

        # Check for appreciation
        appreciation_words = ["love", "great", "awesome", "thanks", "thank", "good"]
        if any(word in text_lower for word in appreciation_words):
            return "appreciation"

        return "general"

    def _calculate_ideation_score(
        self, text: str, is_request: bool, topic: Optional[str], themes: List[str]
    ) -> float:
        """
        Calculate content ideation score.

        Args:
            text: The text to analyze
            is_request: Whether it's a content request
            topic: Detected topic
            themes: Extracted themes

        Returns:
            Score (0.0 to 1.0)
        """
        score = 0.0

        # Boost for content requests
        if is_request:
            score += 0.4

        # Boost for identified topic
        if topic:
            score += 0.3

        # Boost for themes
        if themes:
            score += min(len(themes) * 0.05, 0.2)

        # Length bonus (not too short, not too long)
        length = len(text)
        if 50 <= length <= 300:
            score += 0.1

        return min(score, 1.0)

    def suggest_content_ideas(
        self, comments: List[Comment], limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Suggest content ideas from comments.

        Args:
            comments: List of comments
            limit: Maximum number of ideas to return

        Returns:
            List of content idea dictionaries
        """
        results = self.analyze_batch(comments)

        # Extract high-scoring requests
        ideas = []
        for result in results:
            if result.success:
                data = result.data
                if (
                    data.get("is_request")
                    and data.get("ideation_score", 0.0) >= self._min_score
                ):
                    ideas.append(
                        {
                            "comment_id": result.comment.id,
                            "text": result.comment.text,
                            "topic": data.get("topic"),
                            "themes": data.get("themes", []),
                            "score": data.get("ideation_score", 0.0),
                            "content_type": data.get("content_type"),
                        }
                    )

        # Group similar ideas
        grouped_ideas = self._group_similar_ideas(ideas)

        # Sort by score and frequency
        sorted_ideas = sorted(
            grouped_ideas,
            key=lambda x: (x["score"] * 10 + x["frequency"]),
            reverse=True,
        )[:limit]

        return sorted_ideas

    def _group_similar_ideas(self, ideas: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Group similar content ideas.

        Args:
            ideas: List of idea dictionaries

        Returns:
            List of grouped ideas
        """
        grouped = []

        for idea in ideas:
            # Check for similar ideas
            found_similar = False
            for grouped_idea in grouped:
                if self._are_topics_similar(idea["topic"], grouped_idea["topic"]):
                    grouped_idea["frequency"] += 1
                    grouped_idea["examples"].append(idea["text"])
                    found_similar = True
                    break

            if not found_similar:
                grouped.append(
                    {
                        "text": idea["text"],
                        "topic": idea["topic"],
                        "themes": idea["themes"],
                        "score": idea["score"],
                        "content_type": idea["content_type"],
                        "frequency": 1,
                        "examples": [idea["text"]],
                    }
                )

        # Filter by minimum requests
        filtered = [idea for idea in grouped if idea["frequency"] >= self._min_requests]

        return filtered

    def _are_topics_similar(self, topic1: Optional[str], topic2: Optional[str]) -> bool:
        """
        Check if two topics are similar.

        Args:
            topic1: First topic
            topic2: Second topic

        Returns:
            True if topics are the same or similar
        """
        if not topic1 or not topic2:
            return False

        return topic1 == topic2

    def get_topic_distribution(self, comments: List[Comment]) -> Dict[str, float]:
        """
        Get distribution of topics.

        Args:
            comments: List of comments

        Returns:
            Dictionary mapping topics to percentages
        """
        results = self.analyze_batch(comments)

        topic_counts: Counter = Counter()

        for result in results:
            if result.success:
                topic = result.data.get("topic")
                if topic:
                    topic_counts[topic] += 1

        total = sum(topic_counts.values())
        if total == 0:
            return {}

        return {topic: count / total for topic, count in topic_counts.items()}

    def get_top_themes(
        self, comments: List[Comment], limit: int = 10
    ) -> List[Tuple[str, int]]:
        """
        Get most common themes.

        Args:
            comments: List of comments
            limit: Maximum number of themes to return

        Returns:
            List of (theme, count) tuples
        """
        results = self.analyze_batch(comments)

        theme_counts: Counter = Counter()

        for result in results:
            if result.success:
                themes = result.data.get("themes", [])
                for theme in themes:
                    theme_counts[theme] += 1

        return theme_counts.most_common(limit)
