"""
Base classes and interfaces for the Moderation AI core module.

This module defines abstract base classes and interfaces that provide
the foundation for the moderation system, including data models and
common interfaces.
"""

from typing import Any, Dict, List, Optional, Protocol, runtime_checkable
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import json


class ModerationAction(str, Enum):
    """Possible moderation actions."""

    APPROVE = "approve"
    FLAG = "flag"
    HIDE = "hide"
    REMOVE = "remove"


class Severity(str, Enum):
    """Severity levels for violations."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Sentiment(str, Enum):
    """Sentiment categories."""

    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"


@dataclass
class Comment:
    """Represents a comment from any platform."""

    id: str
    text: str
    author_id: str
    author_name: str
    created_at: datetime
    platform: str
    post_id: str
    parent_id: Optional[str] = None
    likes: int = 0
    replies_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert comment to dictionary."""
        return {
            "id": self.id,
            "text": self.text,
            "author_id": self.author_id,
            "author_name": self.author_name,
            "created_at": self.created_at.isoformat(),
            "platform": self.platform,
            "post_id": self.post_id,
            "parent_id": self.parent_id,
            "likes": self.likes,
            "replies_count": self.replies_count,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Comment":
        """Create comment from dictionary."""
        if isinstance(data.get("created_at"), str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        return cls(**data)


@dataclass
class Violation:
    """Represents a moderation standard violation."""

    standard: str
    description: str
    severity: Severity
    confidence: float
    violated_metrics: List[str]
    reasoning: str
    position: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert violation to dictionary."""
        return {
            "standard": self.standard,
            "description": self.description,
            "severity": self.severity.value,
            "confidence": self.confidence,
            "violated_metrics": self.violated_metrics,
            "reasoning": self.reasoning,
            "position": self.position,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Violation":
        """Create violation from dictionary."""
        if isinstance(data.get("severity"), str):
            data["severity"] = Severity(data["severity"])
        return cls(**data)


@dataclass
class ModerationResult:
    """Result of moderating a comment."""

    comment: Comment
    action: ModerationAction
    violations: List[Violation]
    score: float
    confidence: float
    reasoning: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def has_violations(self) -> bool:
        """Check if there are any violations."""
        return len(self.violations) > 0

    @property
    def is_severe(self) -> bool:
        """Check if any violation is high or critical severity."""
        return any(
            v.severity in (Severity.HIGH, Severity.CRITICAL) for v in self.violations
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "comment": self.comment.to_dict(),
            "action": self.action.value,
            "violations": [v.to_dict() for v in self.violations],
            "score": self.score,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
            "has_violations": self.has_violations,
            "is_severe": self.is_severe,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModerationResult":
        """Create result from dictionary."""
        if isinstance(data.get("comment"), dict):
            data["comment"] = Comment.from_dict(data["comment"])
        if isinstance(data.get("action"), str):
            data["action"] = ModerationAction(data["action"])
        if isinstance(data.get("violations"), list):
            data["violations"] = [Violation.from_dict(v) for v in data["violations"]]
        if isinstance(data.get("timestamp"), str):
            data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)


@dataclass
class AnalysisResult:
    """Base result for all analysis operations."""

    comment: Comment
    success: bool
    data: Dict[str, Any]
    error: Optional[str] = None
    confidence: float = 1.0
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "comment_id": self.comment.id,
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AnalysisResult":
        """Create result from dictionary."""
        if isinstance(data.get("timestamp"), str):
            data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)


@dataclass
class Post:
    """Represents a post from any platform."""

    id: str
    title: str
    content: str
    author_id: str
    author_name: str
    created_at: datetime
    platform: str
    url: str
    likes: int = 0
    shares: int = 0
    comments_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert post to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "author_id": self.author_id,
            "author_name": self.author_name,
            "created_at": self.created_at.isoformat(),
            "platform": self.platform,
            "url": self.url,
            "likes": self.likes,
            "shares": self.shares,
            "comments_count": self.comments_count,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Post":
        """Create post from dictionary."""
        if isinstance(data.get("created_at"), str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        return cls(**data)


class ModerationEngine(ABC):
    """Abstract base class for moderation engines."""

    @abstractmethod
    def moderate(self, comment: Comment) -> ModerationResult:
        """
        Moderate a single comment.

        Args:
            comment: The comment to moderate

        Returns:
            ModerationResult with action and violations
        """
        pass

    @abstractmethod
    def moderate_batch(self, comments: List[Comment]) -> List[ModerationResult]:
        """
        Moderate multiple comments.

        Args:
            comments: List of comments to moderate

        Returns:
            List of ModerationResult objects
        """
        pass


class Analyzer(ABC):
    """Abstract base class for analyzers."""

    @abstractmethod
    def analyze(self, comment: Comment) -> AnalysisResult:
        """
        Analyze a single comment.

        Args:
            comment: The comment to analyze

        Returns:
            AnalysisResult with analysis data
        """
        pass

    @abstractmethod
    def analyze_batch(self, comments: List[Comment]) -> List[AnalysisResult]:
        """
        Analyze multiple comments.

        Args:
            comments: List of comments to analyze

        Returns:
            List of AnalysisResult objects
        """
        pass


class MetricsValidator(ABC):
    """Abstract base class for metrics validators."""

    @abstractmethod
    def validate(self, comment: Comment, metric: str) -> tuple[bool, float, str]:
        """
        Validate a comment against a specific metric.

        Args:
            comment: The comment to validate
            metric: The metric to validate against

        Returns:
            Tuple of (passed, score, reasoning)
        """
        pass

    @abstractmethod
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
        pass


@runtime_checkable
class Configurable(Protocol):
    """Protocol for objects that can be configured."""

    def configure(self, **kwargs: Any) -> None:
        """Configure the object with keyword arguments."""
        ...

    def get_config(self) -> Dict[str, Any]:
        """Get the current configuration."""
        ...
