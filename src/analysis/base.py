"""
Base analyzer class for all analysis modules.

This module provides the abstract base class that all analyzers
must implement, ensuring consistent interface across the system.
"""

from typing import Any, Dict, List, Optional
from abc import ABC, abstractmethod

from ..core.base import Comment, AnalysisResult, Analyzer as BaseAnalyzerInterface


class Analyzer(BaseAnalyzerInterface, ABC):
    """
    Abstract base class for all analyzers.

    All analysis modules (sentiment, categorization, etc.) should
    inherit from this class and implement the abstract methods.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize analyzer.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self._enabled = True

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

    def configure(self, **kwargs: Any) -> None:
        """
        Configure the analyzer.

        Args:
            **kwargs: Configuration parameters
        """
        self.config.update(kwargs)

    def get_config(self) -> Dict[str, Any]:
        """
        Get current configuration.

        Returns:
            Configuration dictionary
        """
        return self.config.copy()

    def enable(self) -> None:
        """Enable the analyzer."""
        self._enabled = True

    def disable(self) -> None:
        """Disable the analyzer."""
        self._enabled = False

    def is_enabled(self) -> bool:
        """
        Check if analyzer is enabled.

        Returns:
            True if enabled, False otherwise
        """
        return self._enabled

    def _create_result(
        self,
        comment: Comment,
        data: Dict[str, Any],
        error: Optional[str] = None,
        confidence: float = 1.0,
    ) -> AnalysisResult:
        """
        Create an AnalysisResult object.

        Args:
            comment: The comment analyzed
            data: Analysis data
            error: Optional error message
            confidence: Confidence score

        Returns:
            AnalysisResult object
        """
        return AnalysisResult(
            comment=comment,
            success=error is None,
            data=data,
            error=error,
            confidence=confidence,
        )

    def _create_error_result(self, comment: Comment, error: str) -> AnalysisResult:
        """
        Create an error AnalysisResult.

        Args:
            comment: The comment being analyzed
            error: Error message

        Returns:
            AnalysisResult with error
        """
        return self._create_result(
            comment=comment,
            data={},
            error=error,
            confidence=0.0,
        )

    def validate_comment(self, comment: Comment) -> bool:
        """
        Validate comment before analysis.

        Args:
            comment: The comment to validate

        Returns:
            True if valid, False otherwise
        """
        if not comment or not comment.text:
            return False

        if len(comment.text.strip()) == 0:
            return False

        return True

    def preprocess_text(self, text: str) -> str:
        """
        Preprocess text for analysis.

        Args:
            text: The text to preprocess

        Returns:
            Preprocessed text
        """
        # Basic preprocessing
        text = text.strip()

        # Optional: Add more preprocessing steps
        # - Lowercase (if needed)
        # - Remove extra whitespace
        # - Handle emojis
        # - Handle special characters

        return text


class CompositeAnalyzer(Analyzer):
    """
    Combines multiple analyzers for comprehensive analysis.

    Runs multiple analyzers in sequence and combines results.
    """

    def __init__(self, analyzers: List[Analyzer], combine_strategy: str = "merge"):
        """
        Initialize composite analyzer.

        Args:
            analyzers: List of analyzers to combine
            combine_strategy: How to combine results ("merge" or "replace")
        """
        super().__init__()
        self.analyzers = analyzers
        self.combine_strategy = combine_strategy

    def analyze(self, comment: Comment) -> AnalysisResult:
        """
        Analyze a comment using all analyzers.

        Args:
            comment: The comment to analyze

        Returns:
            Combined AnalysisResult
        """
        results = []
        for analyzer in self.analyzers:
            if analyzer.is_enabled() and analyzer.validate_comment(comment):
                result = analyzer.analyze(comment)
                results.append(result)

        return self._combine_results(comment, results)

    def analyze_batch(self, comments: List[Comment]) -> List[AnalysisResult]:
        """
        Analyze multiple comments using all analyzers.

        Args:
            comments: List of comments to analyze

        Returns:
            List of combined AnalysisResult objects
        """
        return [self.analyze(comment) for comment in comments]

    def _combine_results(
        self, comment: Comment, results: List[AnalysisResult]
    ) -> AnalysisResult:
        """
        Combine results from multiple analyzers.

        Args:
            comment: The comment analyzed
            results: List of results from analyzers

        Returns:
            Combined AnalysisResult
        """
        if not results:
            return self._create_error_result(
                comment=comment, error="No valid analyzers or all analyzers failed"
            )

        if len(results) == 1:
            return results[0]

        # Merge results
        combined_data: Dict[str, Any] = {}
        all_success = True
        overall_confidence = 0.0

        for result in results:
            if not result.success:
                all_success = False

            if self.combine_strategy == "merge":
                combined_data.update(result.data)
            elif self.combine_strategy == "replace":
                combined_data = result.data.copy()

            overall_confidence += result.confidence

        overall_confidence /= len(results)

        return self._create_result(
            comment=comment,
            data=combined_data,
            error=None if all_success else "Some analyzers failed",
            confidence=overall_confidence,
        )

    def add_analyzer(self, analyzer: Analyzer) -> None:
        """
        Add an analyzer to the composite.

        Args:
            analyzer: The analyzer to add
        """
        self.analyzers.append(analyzer)

    def remove_analyzer(self, analyzer: Analyzer) -> bool:
        """
        Remove an analyzer from the composite.

        Args:
            analyzer: The analyzer to remove

        Returns:
            True if removed, False if not found
        """
        if analyzer in self.analyzers:
            self.analyzers.remove(analyzer)
            return True
        return False

    def get_analyzers(self) -> List[Analyzer]:
        """
        Get all analyzers in the composite.

        Returns:
            List of analyzers
        """
        return self.analyzers.copy()
