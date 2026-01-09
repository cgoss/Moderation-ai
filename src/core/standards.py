"""
Standards engine for moderation system.

This module implements the StandardsEngine class which manages moderation
standards and provides the core logic for evaluating comments against
those standards.
"""

from typing import Any, Dict, List, Optional, Set
from datetime import datetime
import re
from dataclasses import dataclass, field

from .base import (
    Comment,
    ModerationResult,
    Violation,
    ModerationAction,
    Severity,
    ModerationEngine,
)


@dataclass
class Standard:
    """Represents a moderation standard."""

    name: str
    description: str
    metrics: List[str]
    enabled: bool = True
    weight: float = 1.0
    severity_threshold: float = 0.7
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert standard to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "metrics": self.metrics,
            "enabled": self.enabled,
            "weight": self.weight,
            "severity_threshold": self.severity_threshold,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Standard":
        """Create standard from dictionary."""
        return cls(**data)


@dataclass
class Metric:
    """Represents a validation metric."""

    name: str
    description: str
    check_pattern: str
    severity: Severity
    threshold: float
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert metric to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "check_pattern": self.check_pattern,
            "severity": self.severity.value,
            "threshold": self.threshold,
            "enabled": self.enabled,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Metric":
        """Create metric from dictionary."""
        if isinstance(data.get("severity"), str):
            data["severity"] = Severity(data["severity"])
        return cls(**data)


class StandardsEngine(ModerationEngine):
    """
    Engine for evaluating comments against moderation standards.

    This class implements the core moderation logic by checking comments
    against defined standards and metrics, calculating violation scores,
    and determining appropriate moderation actions.
    """

    DEFAULT_STANDARDS = {
        "safety": Standard(
            name="safety",
            description="Protect users from harmful, dangerous, or illegal content",
            metrics=["profanity", "threats", "self_harm", "illegal_content"],
            weight=1.5,
            severity_threshold=0.6,
        ),
        "quality": Standard(
            name="quality",
            description="Maintain high-quality, constructive discussion",
            metrics=["length", "substance", "relevance", "coherence"],
            weight=1.0,
            severity_threshold=0.7,
        ),
        "spam": Standard(
            name="spam",
            description="Prevent spam and promotional content",
            metrics=["repetition", "links", "keywords", "patterns"],
            weight=1.2,
            severity_threshold=0.6,
        ),
        "policy": Standard(
            name="policy",
            description="Enforce platform-specific policies",
            metrics=["harassment", "hate_speech", "misinformation", "violence"],
            weight=1.5,
            severity_threshold=0.5,
        ),
        "engagement": Standard(
            name="engagement",
            description="Encourage meaningful engagement",
            metrics=["tone", "constructiveness", "civility", "helpfulness"],
            weight=0.8,
            severity_threshold=0.7,
        ),
    }

    DEFAULT_METRICS = {
        "profanity": Metric(
            name="profanity",
            description="Detect profane language",
            check_pattern=r"\b(?:shit|fuck|damn|ass|bitch|crap|bastard|idiot|stupid)\b",
            severity=Severity.MEDIUM,
            threshold=0.7,
        ),
        "threats": Metric(
            name="threats",
            description="Detect threatening language",
            check_pattern=r"(?:kill|destroy|hurt|harm|attack|assault|murder|rape)",
            severity=Severity.CRITICAL,
            threshold=0.5,
        ),
        "self_harm": Metric(
            name="self_harm",
            description="Detect self-harm language",
            check_pattern=r"(?:suicide|kill myself|end it|hurt myself)",
            severity=Severity.CRITICAL,
            threshold=0.5,
        ),
        "illegal_content": Metric(
            name="illegal_content",
            description="Detect illegal content references",
            check_pattern=r"(?:drugs|weapons|piracy|illegal|black market)",
            severity=Severity.HIGH,
            threshold=0.7,
        ),
        "length": Metric(
            name="length",
            description="Check if comment is too short",
            check_pattern=r"^.+$",
            severity=Severity.LOW,
            threshold=0.6,
        ),
        "substance": Metric(
            name="substance",
            description="Check if comment has meaningful content",
            check_pattern=r"(?:agree|disagree|good|bad|nice|cool|awesome|great)",
            severity=Severity.LOW,
            threshold=0.8,
        ),
        "relevance": Metric(
            name="relevance",
            description="Check comment relevance to post",
            check_pattern=r".+",
            severity=Severity.MEDIUM,
            threshold=0.7,
        ),
        "coherence": Metric(
            name="coherence",
            description="Check if comment is coherent",
            check_pattern=r".+",
            severity=Severity.MEDIUM,
            threshold=0.7,
        ),
        "repetition": Metric(
            name="repetition",
            description="Detect repetitive content",
            check_pattern=r"(.)\1{3,}",
            severity=Severity.MEDIUM,
            threshold=0.7,
        ),
        "links": Metric(
            name="links",
            description="Detect promotional links",
            check_pattern=r"https?://\S+",
            severity=Severity.MEDIUM,
            threshold=0.8,
        ),
        "keywords": Metric(
            name="keywords",
            description="Detect spam keywords",
            check_pattern=r"(?:subscribe|follow|like|check this|visit my)",
            severity=Severity.MEDIUM,
            threshold=0.7,
        ),
        "patterns": Metric(
            name="patterns",
            description="Detect spam patterns",
            check_pattern=r"(?:\d{3,}|\$[0-9,]+|free.*money)",
            severity=Severity.MEDIUM,
            threshold=0.7,
        ),
        "harassment": Metric(
            name="harassment",
            description="Detect harassment",
            check_pattern=r"(?:stupid|idiot|loser|pathetic|shut up|you're awful)",
            severity=Severity.HIGH,
            threshold=0.6,
        ),
        "hate_speech": Metric(
            name="hate_speech",
            description="Detect hate speech",
            check_pattern=r"(?:hate|discriminate|racist|sexist|homophobic)",
            severity=Severity.CRITICAL,
            threshold=0.5,
        ),
        "misinformation": Metric(
            name="misinformation",
            description="Detect potential misinformation",
            check_pattern=r"(?:fake news|conspiracy|false|not true)",
            severity=Severity.HIGH,
            threshold=0.7,
        ),
        "violence": Metric(
            name="violence",
            description="Detect violent language",
            check_pattern=r"(?:beat|punch|kick|hit|violent|bloody|kill)",
            severity=Severity.HIGH,
            threshold=0.6,
        ),
        "tone": Metric(
            name="tone",
            description="Assess comment tone",
            check_pattern=r".+",
            severity=Severity.LOW,
            threshold=0.7,
        ),
        "constructiveness": Metric(
            name="constructiveness",
            description="Check if comment is constructive",
            check_pattern=r"(?:improve|suggest|recommend|maybe|could|should)",
            severity=Severity.LOW,
            threshold=0.7,
        ),
        "civility": Metric(
            name="civility",
            description="Check comment civility",
            check_pattern=r".+",
            severity=Severity.MEDIUM,
            threshold=0.7,
        ),
        "helpfulness": Metric(
            name="helpfulness",
            description="Check if comment is helpful",
            check_pattern=r"(?:help|useful|thanks|thank|appreciate)",
            severity=Severity.LOW,
            threshold=0.7,
        ),
    }

    def __init__(
        self,
        standards: Optional[Dict[str, Standard]] = None,
        metrics: Optional[Dict[str, Metric]] = None,
        threshold: float = 0.7,
        auto_moderate: bool = False,
    ):
        """
        Initialize the standards engine.

        Args:
            standards: Dictionary of standards (uses defaults if None)
            metrics: Dictionary of metrics (uses defaults if None)
            threshold: Global violation threshold
            auto_moderate: Whether to automatically moderate
        """
        self.standards = standards or self.DEFAULT_STANDARDS.copy()
        self.metrics = metrics or self.DEFAULT_METRICS.copy()
        self.threshold = threshold
        self.auto_moderate = auto_moderate
        self._cache: Dict[str, Any] = {}

    def moderate(self, comment: Comment) -> ModerationResult:
        """
        Moderate a single comment.

        Args:
            comment: The comment to moderate

        Returns:
            ModerationResult with action and violations
        """
        violations: List[Violation] = []
        total_score = 0.0
        total_weight = 0.0

        for standard_name, standard in self.standards.items():
            if not standard.enabled:
                continue

            standard_violations = self._check_standard(comment, standard)
            violations.extend(standard_violations)

            if standard_violations:
                violation_score = max(v.confidence for v in standard_violations)
                total_score += violation_score * standard.weight
                total_weight += standard.weight
            else:
                total_weight += standard.weight

        final_score = total_score / total_weight if total_weight > 0 else 0.0

        action = self._determine_action(final_score, violations)
        confidence = self._calculate_confidence(final_score, violations)
        reasoning = self._generate_reasoning(violations, final_score)

        return ModerationResult(
            comment=comment,
            action=action,
            violations=violations,
            score=final_score,
            confidence=confidence,
            reasoning=reasoning,
        )

    def moderate_batch(self, comments: List[Comment]) -> List[ModerationResult]:
        """
        Moderate multiple comments.

        Args:
            comments: List of comments to moderate

        Returns:
            List of ModerationResult objects
        """
        return [self.moderate(comment) for comment in comments]

    def _check_standard(self, comment: Comment, standard: Standard) -> List[Violation]:
        """
        Check a comment against a specific standard.

        Args:
            comment: The comment to check
            standard: The standard to check against

        Returns:
            List of violations found
        """
        violations: List[Violation] = []
        violated_metrics: List[str] = []

        for metric_name in standard.metrics:
            if metric_name not in self.metrics:
                continue

            metric = self.metrics[metric_name]
            if not metric.enabled:
                continue

            passed, score, reasoning = self._check_metric(comment, metric)

            if not passed:
                violated_metrics.append(metric_name)

        if violated_metrics:
            confidence = max(
                self.metrics[m].threshold for m in violated_metrics if m in self.metrics
            )

            violation = Violation(
                standard=standard.name,
                description=standard.description,
                severity=self._determine_severity(confidence, standard),
                confidence=confidence,
                violated_metrics=violated_metrics,
                reasoning=f"Comment violates {standard.name} standard based on metrics: {', '.join(violated_metrics)}",
            )
            violations.append(violation)

        return violations

    def _check_metric(
        self, comment: Comment, metric: Metric
    ) -> tuple[bool, float, str]:
        """
        Check a comment against a specific metric.

        Args:
            comment: The comment to check
            metric: The metric to check against

        Returns:
            Tuple of (passed, score, reasoning)
        """
        text = comment.text.lower()

        try:
            pattern = re.compile(metric.check_pattern, re.IGNORECASE)
            matches = pattern.findall(text)

            if matches:
                score = len(matches) / max(1, len(text.split()))
                passed = score < metric.threshold
                reasoning = f"Found {len(matches)} matches for {metric.name} pattern"
                return passed, score, reasoning
            else:
                return True, 0.0, f"No matches found for {metric.name}"
        except Exception:
            return True, 0.0, f"Error checking {metric.name}"

    def _determine_severity(self, confidence: float, standard: Standard) -> Severity:
        """
        Determine the severity level for a violation.

        Args:
            confidence: The violation confidence score
            standard: The standard being evaluated

        Returns:
            Severity level
        """
        if confidence >= 0.9:
            return Severity.CRITICAL
        elif confidence >= 0.7:
            return Severity.HIGH
        elif confidence >= 0.5:
            return Severity.MEDIUM
        else:
            return Severity.LOW

    def _determine_action(
        self, score: float, violations: List[Violation]
    ) -> ModerationAction:
        """
        Determine the appropriate moderation action.

        Args:
            score: The overall violation score
            violations: List of violations found

        Returns:
            Recommended moderation action
        """
        if not violations:
            return ModerationAction.APPROVE

        # Check for critical violations
        if any(v.severity == Severity.CRITICAL for v in violations):
            return ModerationAction.REMOVE

        # Check for high severity
        if any(v.severity == Severity.HIGH for v in violations):
            return ModerationAction.REMOVE

        # Check if score exceeds threshold
        if score >= self.threshold and self.auto_moderate:
            return ModerationAction.HIDE

        # Otherwise flag for review
        return ModerationAction.FLAG

    def _calculate_confidence(self, score: float, violations: List[Violation]) -> float:
        """
        Calculate overall confidence in the moderation decision.

        Args:
            score: The overall violation score
            violations: List of violations found

        Returns:
            Confidence score (0.0 to 1.0)
        """
        if not violations:
            return 1.0

        # Confidence is based on the number and severity of violations
        max_severity_confidence = max(v.confidence for v in violations)
        violation_count_factor = min(len(violations) / 5.0, 1.0)

        return (max_severity_confidence + violation_count_factor) / 2.0

    def _generate_reasoning(self, violations: List[Violation], score: float) -> str:
        """
        Generate human-readable reasoning for the moderation decision.

        Args:
            violations: List of violations found
            score: The overall violation score

        Returns:
            Reasoning string
        """
        if not violations:
            return f"Comment passes all standards. No violations detected."

        reasons = [f"Found {len(violations)} violation(s):"]
        for violation in violations:
            reasons.append(f"  - {violation.standard}: {violation.reasoning}")

        reasons.append(f"Overall score: {score:.2f} (threshold: {self.threshold})")

        return "\n".join(reasons)

    def add_standard(self, standard: Standard) -> None:
        """
        Add a new moderation standard.

        Args:
            standard: The standard to add
        """
        self.standards[standard.name] = standard

    def remove_standard(self, name: str) -> bool:
        """
        Remove a moderation standard.

        Args:
            name: Name of the standard to remove

        Returns:
            True if removed, False if not found
        """
        if name in self.standards:
            del self.standards[name]
            return True
        return False

    def add_metric(self, metric: Metric) -> None:
        """
        Add a new validation metric.

        Args:
            metric: The metric to add
        """
        self.metrics[metric.name] = metric

    def remove_metric(self, name: str) -> bool:
        """
        Remove a validation metric.

        Args:
            name: Name of the metric to remove

        Returns:
            True if removed, False if not found
        """
        if name in self.metrics:
            del self.metrics[name]
            return True
        return False

    def enable_standard(self, name: str) -> bool:
        """
        Enable a moderation standard.

        Args:
            name: Name of the standard to enable

        Returns:
            True if enabled, False if not found
        """
        if name in self.standards:
            self.standards[name].enabled = True
            return True
        return False

    def disable_standard(self, name: str) -> bool:
        """
        Disable a moderation standard.

        Args:
            name: Name of the standard to disable

        Returns:
            True if disabled, False if not found
        """
        if name in self.standards:
            self.standards[name].enabled = False
            return True
        return False

    def get_standards(self) -> Dict[str, Standard]:
        """
        Get all moderation standards.

        Returns:
            Dictionary of standards
        """
        return self.standards.copy()

    def get_metrics(self) -> Dict[str, Metric]:
        """
        Get all validation metrics.

        Returns:
            Dictionary of metrics
        """
        return self.metrics.copy()
