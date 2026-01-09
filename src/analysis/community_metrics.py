"""
Community metrics module.

This module provides functionality to calculate
community health metrics and engagement analytics.
"""

from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
from collections import Counter, defaultdict

from .base import Analyzer
from ..core.base import Comment, AnalysisResult


class CommunityMetrics(Analyzer):
    """
    Analyzer for community metrics.

    Calculates various metrics related to community
    health, engagement, and user behavior.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize community metrics analyzer.

        Args:
            config: Optional configuration
        """
        super().__init__(config)
        self._time_window_hours = config.get("time_window_hours", 24) if config else 24

    def analyze(self, comment: Comment) -> AnalysisResult:
        """
        Analyze a comment for community metrics.

        Args:
            comment: The comment to analyze

        Returns:
            AnalysisResult with community metric data
        """
        if not self.validate_comment(comment):
            return self._create_error_result(comment, "Invalid comment")

        # Calculate individual comment metrics
        engagement_score = self._calculate_engagement_score(comment)
        influence_score = self._calculate_influence_score(comment)
        contribution_quality = self._calculate_contribution_quality(comment)

        # Identify user behavior patterns
        behavior_type = self._classify_behavior(comment)

        data = {
            "engagement_score": engagement_score,
            "influence_score": influence_score,
            "contribution_quality": contribution_quality,
            "behavior_type": behavior_type,
            "likes": comment.likes,
            "replies_count": comment.replies_count,
            "length": len(comment.text),
            "word_count": len(comment.text.split()),
        }

        confidence = (engagement_score + influence_score + contribution_quality) / 3
        return self._create_result(comment, data, confidence=confidence)

    def analyze_batch(self, comments: List[Comment]) -> List[AnalysisResult]:
        """
        Analyze multiple comments for community metrics.

        Args:
            comments: List of comments to analyze

        Returns:
            List of AnalysisResult objects
        """
        return [self.analyze(comment) for comment in comments]

    def calculate_community_health(self, comments: List[Comment]) -> Dict[str, Any]:
        """
        Calculate overall community health metrics.

        Args:
            comments: List of comments

        Returns:
            Dictionary of community health metrics
        """
        if not comments:
            return {}

        results = self.analyze_batch(comments)

        # Engagement metrics
        engagement_metrics = self._calculate_engagement_metrics(comments)

        # User behavior metrics
        behavior_metrics = self._calculate_behavior_metrics(results)

        # Content quality metrics
        quality_metrics = self._calculate_quality_metrics(comments)

        # Activity metrics
        activity_metrics = self._calculate_activity_metrics(comments)

        # Overall health score
        health_score = self._calculate_health_score(
            engagement_metrics, behavior_metrics, quality_metrics
        )

        return {
            "overall_health_score": health_score,
            "engagement_metrics": engagement_metrics,
            "behavior_metrics": behavior_metrics,
            "quality_metrics": quality_metrics,
            "activity_metrics": activity_metrics,
            "total_comments": len(comments),
            "analyzed_at": datetime.utcnow().isoformat(),
        }

    def _calculate_engagement_score(self, comment: Comment) -> float:
        """
        Calculate engagement score for a comment.

        Args:
            comment: The comment

        Returns:
            Engagement score (0.0 to 1.0)
        """
        # Base score from likes and replies
        base_score = min((comment.likes + comment.replies_count) / 10.0, 1.0)

        # Length bonus
        length = len(comment.text)
        if 50 <= length <= 500:
            base_score *= 1.2

        return min(base_score, 1.0)

    def _calculate_influence_score(self, comment: Comment) -> float:
        """
        Calculate influence score for a comment.

        Args:
            comment: The comment

        Returns:
            Influence score (0.0 to 1.0)
        """
        # Influence based on engagement
        engagement = comment.likes + comment.replies_count

        if engagement == 0:
            return 0.0

        # Logarithmic scale to avoid skew
        import math

        score = min(math.log(engagement + 1) / math.log(100), 1.0)

        return score

    def _calculate_contribution_quality(self, comment: Comment) -> float:
        """
        Calculate quality of contribution.

        Args:
            comment: The comment

        Returns:
            Quality score (0.0 to 1.0)
        """
        text = comment.text
        word_count = len(text.split())

        # Length scoring
        if word_count < 5:
            length_score = 0.3
        elif 5 <= word_count <= 20:
            length_score = 1.0
        elif 20 < word_count <= 50:
            length_score = 0.8
        else:
            length_score = 0.6

        # Engagement ratio
        total_possible = word_count + 10  # Normalize
        engagement_ratio = min(
            (comment.likes + comment.replies_count) / total_possible, 1.0
        )

        # Average the scores
        return (length_score + engagement_ratio) / 2.0

    def _classify_behavior(self, comment: Comment) -> str:
        """
        Classify user behavior type.

        Args:
            comment: The comment

        Returns:
            Behavior classification
        """
        # High engagement = contributory
        if comment.likes > 10 or comment.replies_count > 5:
            return "contributory"

        # Short and no engagement = casual
        if len(comment.text) < 30 and comment.likes == 0:
            return "casual"

        # Long and detailed = substantial
        if len(comment.text) > 200:
            return "substantial"

        # Default = regular
        return "regular"

    def _calculate_engagement_metrics(self, comments: List[Comment]) -> Dict[str, Any]:
        """
        Calculate engagement metrics.

        Args:
            comments: List of comments

        Returns:
            Dictionary of engagement metrics
        """
        total_likes = sum(c.likes for c in comments)
        total_replies = sum(c.replies_count for c in comments)
        total_comments = len(comments)

        if total_comments == 0:
            return {}

        avg_likes = total_likes / total_comments
        avg_replies = total_replies / total_comments

        # Calculate engagement rate
        engaged_comments = sum(
            1 for c in comments if c.likes > 0 or c.replies_count > 0
        )
        engagement_rate = engaged_comments / total_comments

        return {
            "total_likes": total_likes,
            "total_replies": total_replies,
            "average_likes": avg_likes,
            "average_replies": avg_replies,
            "engagement_rate": engagement_rate,
        }

    def _calculate_behavior_metrics(
        self, results: List[AnalysisResult]
    ) -> Dict[str, Any]:
        """
        Calculate behavior metrics.

        Args:
            results: List of analysis results

        Returns:
            Dictionary of behavior metrics
        """
        if not results:
            return {}

        behavior_counts: Counter = Counter()

        for result in results:
            if result.success:
                behavior = result.data.get("behavior_type", "unknown")
                behavior_counts[behavior] += 1

        total = len(results)

        return {
            "behavior_distribution": {
                behavior: count / total for behavior, count in behavior_counts.items()
            },
            "dominant_behavior": behavior_counts.most_common(1)[0][0],
        }

    def _calculate_quality_metrics(self, comments: List[Comment]) -> Dict[str, Any]:
        """
        Calculate content quality metrics.

        Args:
            comments: List of comments

        Returns:
            Dictionary of quality metrics
        """
        if not comments:
            return {}

        lengths = [len(c.text) for c in comments]
        word_counts = [len(c.text.split()) for c in comments]

        return {
            "average_length": sum(lengths) / len(lengths),
            "median_length": sorted(lengths)[len(lengths) // 2],
            "average_word_count": sum(word_counts) / len(word_counts),
            "short_comments": sum(1 for l in lengths if l < 50),
            "long_comments": sum(1 for l in lengths if l > 200),
        }

    def _calculate_activity_metrics(self, comments: List[Comment]) -> Dict[str, Any]:
        """
        Calculate activity metrics.

        Args:
            comments: List of comments

        Returns:
            Dictionary of activity metrics
        """
        if not comments:
            return {}

        # Group comments by user
        user_comment_counts: Counter = Counter()

        for comment in comments:
            user_comment_counts[comment.author_id] += 1

        # Calculate activity distribution
        comment_counts = list(user_comment_counts.values())

        return {
            "total_unique_users": len(user_comment_counts),
            "average_comments_per_user": sum(comment_counts) / len(comment_counts),
            "most_active_users": user_comment_counts.most_common(5),
            "user_distribution": self._calculate_user_distribution(comment_counts),
        }

    def _calculate_user_distribution(self, counts: List[int]) -> Dict[str, float]:
        """
        Calculate user activity distribution.

        Args:
            counts: List of comment counts per user

        Returns:
            Dictionary with distribution metrics
        """
        if not counts:
            return {}

        total = sum(counts)

        # Calculate percentile ranges
        import statistics

        try:
            mean = statistics.mean(counts)
            median = statistics.median(counts)
        except statistics.StatisticsError:
            mean = sum(counts) / len(counts)
            median = sorted(counts)[len(counts) // 2]

        return {
            "mean_comments_per_user": mean,
            "median_comments_per_user": median,
            "total_users": len(counts),
            "power_users": sum(1 for c in counts if c > mean * 2),
            "power_user_ratio": sum(1 for c in counts if c > mean * 2) / len(counts),
        }

    def _calculate_health_score(
        self,
        engagement: Dict[str, Any],
        behavior: Dict[str, Any],
        quality: Dict[str, Any],
    ) -> float:
        """
        Calculate overall community health score.

        Args:
            engagement: Engagement metrics
            behavior: Behavior metrics
            quality: Quality metrics

        Returns:
            Health score (0.0 to 1.0)
        """
        scores = []

        # Engagement score
        if engagement and "engagement_rate" in engagement:
            scores.append(engagement["engagement_rate"])

        # Quality score (inverse of short comments)
        if quality and "short_comments" in quality:
            total = quality.get("short_comments", 0) + quality.get("long_comments", 0)
            if total > 0:
                quality_score = quality.get("long_comments", 0) / total
                scores.append(quality_score)

        # Behavior score (more contributory = better)
        if behavior and "behavior_distribution" in behavior:
            contributory = behavior["behavior_distribution"].get("contributory", 0)
            scores.append(contributory)

        if not scores:
            return 0.5

        return sum(scores) / len(scores)

    def get_top_contributors(
        self, comments: List[Comment], limit: int = 10
    ) -> List[Tuple[str, int]]:
        """
        Get top contributors by engagement.

        Args:
            comments: List of comments
            limit: Maximum number of contributors to return

        Returns:
            List of (user_id, engagement_score) tuples
        """
        user_engagement: Dict[str, int] = defaultdict(int)

        for comment in comments:
            engagement = comment.likes + comment.replies_count
            user_engagement[comment.author_id] += engagement

        # Sort by engagement
        sorted_users = sorted(user_engagement.items(), key=lambda x: x[1], reverse=True)

        return sorted_users[:limit]

    def get_engagement_trend(
        self, comments: List[Comment], window_hours: int = 24
    ) -> List[Dict[str, Any]]:
        """
        Calculate engagement trend over time.

        Args:
            comments: List of comments
            window_hours: Time window for grouping

        Returns:
            List of time-windowed engagement data
        """
        if not comments:
            return []

        # Group comments by time window
        time_groups: Dict[int, List[Comment]] = defaultdict(list)

        for comment in comments:
            window = int(comment.created_at.timestamp() / (window_hours * 3600))
            time_groups[window].append(comment)

        # Calculate engagement for each window
        trends = []
        for window, group_comments in sorted(time_groups.items()):
            if not group_comments:
                continue

            total_engagement = sum(c.likes + c.replies_count for c in group_comments)
            avg_engagement = total_engagement / len(group_comments)

            trends.append(
                {
                    "window": window,
                    "timestamp": window * window_hours * 3600,
                    "comment_count": len(group_comments),
                    "total_engagement": total_engagement,
                    "average_engagement": avg_engagement,
                }
            )

        return trends
