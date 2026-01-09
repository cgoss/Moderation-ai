"""
Abuse and bullying detection module.

This module provides functionality to detect abusive,
harassing, or bullying behavior in comments.
"""

from typing import Any, Dict, List, Optional, Set
import re
from collections import Counter

from .base import Analyzer
from ..core.base import Comment, AnalysisResult, Severity


class AbuseDetector(Analyzer):
    """
    Analyzer for abuse and bullying detection.

    Detects various types of abusive behavior including
    direct attacks, harassment, hate speech, and threats.
    """

    # Direct attack patterns
    DIRECT_ATTACK_PATTERNS = [
        r"\b(you are|you\'re|ur)\s+(stupid|idiot|moron|loser|pathetic|useless|worthless)",
        r"\b(everyone knows|everyone sees)\s+(that you|you are|you\'re)",
        r"\b(nobody likes|no one likes)\s+you",
    ]

    # Harassment patterns
    HARASSMENT_PATTERNS = [
        r"\b(follow|stop|leave)\s+(me|us)\s+(alone|alone already)",
        r"\b(still|again|stop)\s+(doing this|talking|posting)",
        r"\b(get a life|shut up|go away|leave)",
        r"\b(stupid|idiot|loser)\s+(comment|post|message)",
    ]

    # Hate speech indicators
    HATE_SPEECH_INDICATORS = {
        "slurs": [
            "racist",
            "sexist",
            "homophobic",
            "transphobic",
            "xenophobic",
            "islamophobic",
            "antisemitic",
        ],
        "discrimination": [
            "inferior",
            "subhuman",
            "degenerate",
            "filth",
            "scum",
            "trash",
            "vermin",
            "animals",
        ],
        "stereotypes": [
            "all.*are",
            "typical.*",
            "just like.*",
        ],
    }

    # Threatening language
    THREAT_PATTERNS = [
        r"\b(kill|murder|destroy|hurt|harm)\s+(you|your)",
        r"\b(find|hunt|track)\s+(you|you\s+down)",
        r"\b(will\+be\+sorry|you\'ll\+regret|going to get you)",
        r"\b(doxxing|dox|expose)\s+(you|your\s+address)",
    ]

    # Repeated behavior indicators
    REPETITION_INDICATORS = [
        "mentioned",
        "tagged",
        "replied to",
        "quoted",
        "again",
        "still",
        "keep",
        "stop",
    ]

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize abuse detector.

        Args:
            config: Optional configuration
        """
        super().__init__(config)
        self._strict_mode = config.get("strict_mode", False) if config else False
        self._min_indicators = config.get("min_indicators", 2) if config else 2
        self._context_window = config.get("context_window", 50) if config else 50

    def analyze(self, comment: Comment) -> AnalysisResult:
        """
        Detect abuse in a comment.

        Args:
            comment: The comment to analyze

        Returns:
            AnalysisResult with abuse detection data
        """
        if not self.validate_comment(comment):
            return self._create_error_result(comment, "Invalid comment")

        text = comment.text
        text_lower = text.lower()

        # Detect different types of abuse
        direct_attack = self._detect_direct_attack(text)
        harassment = self._detect_harassment(text)
        hate_speech = self._detect_hate_speech(text)
        threats = self._detect_threats(text)
        repetition = self._detect_repetition(text, comment)

        # Calculate overall abuse score
        abuse_score = self._calculate_abuse_score(
            {
                "direct_attack": direct_attack,
                "harassment": harassment,
                "hate_speech": hate_speech,
                "threats": threats,
                "repetition": repetition,
            }
        )

        # Determine severity
        severity = self._classify_severity(abuse_score)

        # Determine if abuse detected
        is_abusive = abuse_score >= self._get_abuse_threshold()

        data = {
            "is_abusive": is_abusive,
            "abuse_score": abuse_score,
            "severity": severity.value if severity else None,
            "indicators": {
                "direct_attack": direct_attack,
                "harassment": harassment,
                "hate_speech": hate_speech,
                "threats": threats,
                "repetition": repetition,
            },
            "indicator_count": sum(
                [
                    direct_attack["detected"],
                    harassment["detected"],
                    hate_speech["detected"],
                    threats["detected"],
                    repetition["detected"],
                ]
            ),
            "matches": self._get_all_matches(text_lower),
        }

        confidence = min(abuse_score, 1.0)
        return self._create_result(comment, data, confidence=confidence)

    def analyze_batch(self, comments: List[Comment]) -> List[AnalysisResult]:
        """
        Detect abuse in multiple comments.

        Args:
            comments: List of comments to analyze

        Returns:
            List of AnalysisResult objects
        """
        return [self.analyze(comment) for comment in comments]

    def _detect_direct_attack(self, text: str) -> Dict[str, Any]:
        """
        Detect direct personal attacks.

        Args:
            text: The text to analyze

        Returns:
            Dictionary with detection results
        """
        matches = []
        text_lower = text.lower()

        for pattern in self.DIRECT_ATTACK_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                matches.append(pattern)

        detected = len(matches) > 0
        return {
            "detected": detected,
            "match_count": len(matches),
            "matches": matches[:3],
        }

    def _detect_harassment(self, text: str) -> Dict[str, Any]:
        """
        Detect harassing behavior.

        Args:
            text: The text to analyze

        Returns:
            Dictionary with detection results
        """
        matches = []
        text_lower = text.lower()

        for pattern in self.HARASSMENT_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                matches.append(pattern)

        detected = len(matches) > 0
        return {
            "detected": detected,
            "match_count": len(matches),
            "matches": matches[:3],
        }

    def _detect_hate_speech(self, text: str) -> Dict[str, Any]:
        """
        Detect hate speech indicators.

        Args:
            text: The text to analyze

        Returns:
            Dictionary with detection results
        """
        matches = []
        text_lower = text.lower()

        for category, keywords in self.HATE_SPEECH_INDICATORS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    matches.append(
                        {
                            "category": category,
                            "keyword": keyword,
                        }
                    )

        detected = len(matches) > 0
        return {
            "detected": detected,
            "match_count": len(matches),
            "matches": matches[:5],
        }

    def _detect_threats(self, text: str) -> Dict[str, Any]:
        """
        Detect threatening language.

        Args:
            text: The text to analyze

        Returns:
            Dictionary with detection results
        """
        matches = []
        text_lower = text.lower()

        for pattern in self.THREAT_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                matches.append(pattern)

        detected = len(matches) > 0
        return {
            "detected": detected,
            "match_count": len(matches),
            "matches": matches[:3],
        }

    def _detect_repetition(self, text: str, comment: Comment) -> Dict[str, Any]:
        """
        Detect repetitive behavior across comments.

        Args:
            text: The text to analyze
            comment: The comment being analyzed

        Returns:
            Dictionary with detection results
        """
        # Check for repeated phrases within comment
        words = text.lower().split()
        word_counts = Counter(words)

        repeated_words = [word for word, count in word_counts.items() if count >= 3]

        detected = len(repeated_words) > 0
        return {
            "detected": detected,
            "match_count": len(repeated_words),
            "matches": repeated_words[:5],
        }

    def _calculate_abuse_score(self, indicators: Dict[str, Any]) -> float:
        """
        Calculate overall abuse score.

        Args:
            indicators: Dictionary of all indicators

        Returns:
            Abuse score (0.0 to 1.0)
        """
        # Weight different types of abuse
        weights = {
            "direct_attack": 1.0,
            "harassment": 0.8,
            "hate_speech": 1.2,
            "threats": 1.5,
            "repetition": 0.5,
        }

        total_score = 0.0
        total_weight = 0.0

        for key, weight in weights.items():
            if key in indicators:
                indicator = indicators[key]
                if indicator["detected"]:
                    # Normalize by match count
                    normalized = min(indicator["match_count"] / 5.0, 1.0)
                    total_score += normalized * weight
                    total_weight += weight

        if total_weight == 0:
            return 0.0

        return total_score / total_weight

    def _classify_severity(self, score: float) -> Optional[Severity]:
        """
        Classify abuse severity.

        Args:
            score: Abuse score

        Returns:
            Severity level
        """
        if score < 0.3:
            return None
        elif score < 0.5:
            return Severity.LOW
        elif score < 0.7:
            return Severity.MEDIUM
        elif score < 0.9:
            return Severity.HIGH
        else:
            return Severity.CRITICAL

    def _get_abuse_threshold(self) -> float:
        """
        Get abuse threshold.

        Returns:
            Threshold value
        """
        return 0.4 if self._strict_mode else 0.6

    def _get_all_matches(self, text: str) -> List[str]:
        """
        Get all abuse pattern matches.

        Args:
            text: The text to analyze

        Returns:
            List of matched patterns
        """
        matches = []

        all_patterns = (
            self.DIRECT_ATTACK_PATTERNS
            + self.HARASSMENT_PATTERNS
            + self.THREAT_PATTERNS
        )

        for pattern in all_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                matches.append(pattern)

        # Add hate speech keywords
        for category, keywords in self.HATE_SPEECH_INDICATORS.items():
            for keyword in keywords:
                if keyword in text:
                    matches.append(keyword)

        return matches[:10]

    def get_abuse_statistics(self, comments: List[Comment]) -> Dict[str, Any]:
        """
        Get abuse statistics across multiple comments.

        Args:
            comments: List of comments

        Returns:
            Dictionary of abuse statistics
        """
        results = self.analyze_batch(comments)

        total = len(results)
        if total == 0:
            return {}

        abusive_count = sum(
            1 for result in results if result.success and result.data.get("is_abusive")
        )

        severity_counts: Counter = Counter()
        for result in results:
            if result.success:
                severity = result.data.get("severity")
                if severity:
                    severity_counts[severity] += 1

        return {
            "total_comments": total,
            "abusive_count": abusive_count,
            "abuse_rate": abusive_count / total,
            "severity_distribution": {
                severity: count / abusive_count
                for severity, count in severity_counts.items()
            },
            "most_common_indicators": self._get_common_indicators(results),
        }

    def _get_common_indicators(self, results: List[AnalysisResult]) -> List[str]:
        """
        Get most common abuse indicators.

        Args:
            results: List of analysis results

        Returns:
            List of common indicators
        """
        indicator_counts: Counter = Counter()

        for result in results:
            if result.success:
                matches = result.data.get("matches", [])
                for match in matches:
                    indicator_counts[match] += 1

        return [indicator for indicator, count in indicator_counts.most_common(10)]

    def is_severe_abuse(self, comment: Comment) -> bool:
        """
        Check if comment contains severe abuse.

        Args:
            comment: The comment to check

        Returns:
            True if severe abuse detected
        """
        result = self.analyze(comment)

        if not result.success:
            return False

        is_abusive = result.data.get("is_abusive", False)
        severity = result.data.get("severity")
        return is_abusive and severity in [
            Severity.HIGH,
            Severity.CRITICAL,
        ]
