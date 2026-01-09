"""
Core moderation AI library.

This package provides the core functionality for the moderation system,
including configuration, standards, metrics, and base classes.
"""

from .config import Config, get_config
from .base import (
    Comment,
    Post,
    Violation,
    ModerationResult,
    AnalysisResult,
    ModerationEngine,
    Analyzer,
    MetricsValidator,
    ModerationAction,
    Severity,
    Sentiment,
)
from .standards import StandardsEngine, Standard, Metric
from .metrics import (
    MetricsValidator as MetricsValidatorImpl,
    TextAnalyzer,
)

__all__ = [
    # Configuration
    "Config",
    "get_config",
    # Base classes
    "Comment",
    "Post",
    "Violation",
    "ModerationResult",
    "AnalysisResult",
    "ModerationEngine",
    "Analyzer",
    "MetricsValidator",
    "ModerationAction",
    "Severity",
    "Sentiment",
    # Standards
    "StandardsEngine",
    "Standard",
    "Metric",
    # Metrics
    "MetricsValidatorImpl",
    "TextAnalyzer",
]
